# app.py
import json
import logging
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import database as db
from ml.indian_curriculum import (
    get_subjects_for_stream,
    get_topics_for_subject      as curriculum_topics,
    get_difficulty,
)
import llm

try:
    import rag
    _RAG_AVAILABLE = True
except ImportError:
    rag = None
    _RAG_AVAILABLE = False

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger("learnflow")

# ── ML imports with graceful fallback ─────────────────────────
try:
    from ml.forgetting_inference import predict_next_review as _predict_next_review
    _FORGETTING_MODEL_AVAILABLE = True
    logger.info("Forgetting model loaded successfully")
except Exception as e:
    _FORGETTING_MODEL_AVAILABLE = False
    logger.warning(f"Forgetting model unavailable: {e}. Using rule-based fallback.")

try:
    from ml.backlog_inference import predict_backlog as _predict_backlog
    _BACKLOG_MODEL_AVAILABLE = True
    logger.info("Backlog model loaded successfully")
except Exception as e:
    _BACKLOG_MODEL_AVAILABLE = False
    logger.warning(f"Backlog model unavailable: {e}. Using rule-based fallback.")


app = FastAPI(
    title       = "LearnFlow API",
    description = "AI-powered study companion for Indian students",
    version     = "2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
    allow_credentials = True
)

@app.on_event("startup")
async def startup():
    db.create_tables()
    logger.info("LearnFlow API started — database ready")


# ── Pydantic models ────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:     str
    email:    str
    password: str
    stream:   str

class LoginRequest(BaseModel):
    email:    str
    password: str

class SubjectRequest(BaseModel):
    name:           str
    stream:         str
    exam_name:      str
    exam_date:      str
    chapters_total: int

class StudyLogRequest(BaseModel):
    subject_id:     int
    topics_covered: int
    study_time:     float
    quiz_score:     float
    days_skipped:   int
    self_rating:    int
    notes:          str = ""

class QuestionAttemptDetail(BaseModel):
    question_id:    int
    chosen_option:  str
    correct_option: str
    is_correct:     bool
    time_spent_sec: float = 0.0

class QuizSubmitRequest(BaseModel):
    topic_id:          int
    score:             float
    time_spent:        float
    self_rating:       int
    difficulty:        int
    correct_count:     int = 0
    total_count:       int = 0
    question_attempts: list = []   # list of QuestionAttemptDetail dicts

class QuizCheckRequest(BaseModel):
    answers: dict  # {question_id (str): chosen_option (str)}

class AddQuestionRequest(BaseModel):
    topic_id:    int
    question:    str
    option_a:    str
    option_b:    str
    option_c:    str
    option_d:    str
    answer:      str
    explanation: str
    difficulty:  int

class StudyPlanRequest(BaseModel):
    subject_id: int
    exam_date:  str
    exam_name:  str = "Exam"

class CopilotChatRequest(BaseModel):
    message:         str
    history:         list = []
    conversation_id: str | None = None   # optional - client can pass back to continue thread


# ── Fallback ML functions (rule-based, clearly labelled) ───────

def _rule_based_next_review(attempts: list, topic_difficulty: float, last_score: float) -> dict:
    """
    Rule-based spaced-repetition fallback used when the LSTM model is unavailable.
    Based on simplified Ebbinghaus formula with score and difficulty adjustments.
    NOT a machine-learning prediction.
    """
    n = len(attempts)

    # Base interval from last score
    if last_score >= 85:
        base_days = 14
    elif last_score >= 70:
        base_days = 7
    elif last_score >= 55:
        base_days = 4
    elif last_score >= 40:
        base_days = 2
    else:
        base_days = 1

    # Difficulty penalty
    diff_penalty = (topic_difficulty - 1) / 4          # 0 to 1
    adjusted     = base_days * (1 - diff_penalty * 0.4)

    # Repeat-attempt bonus — more attempts means better retention
    if n >= 3:
        adjusted = min(adjusted * 1.3, 21)

    days_until  = max(1, round(adjusted))
    recall_prob = min(0.95, max(0.1, last_score / 100 * 0.9))
    next_review = datetime.now() + timedelta(days=days_until)

    if days_until <= 1:
        urgency = "today"
        message = "Review this topic today — your recall needs reinforcement"
    elif days_until <= 3:
        urgency = "soon"
        message = f"Review in {days_until} days to stay on track"
    else:
        urgency = "later"
        message = f"You are on track — next review in {days_until} days"

    return {
        "recall_prob":  round(recall_prob, 3),
        "next_review":  next_review.strftime("%Y-%m-%d"),
        "days_until":   days_until,
        "urgency":      urgency,
        "message":      message,
        "model_source": "rule_based_fallback"   # clearly labelled as non-ML
    }


def _rule_based_backlog(study_logs: list, subject: str, chapters_total: int,
                        days_to_exam: int, exam_name: str = "your exam") -> dict:
    """
    Rule-based backlog severity fallback used when the LSTM model is unavailable.
    Computes severity from coverage rate and urgency.
    NOT a machine-learning prediction.
    """
    covered   = sum(int(log.get("topics_covered", 0)) for log in study_logs)
    remaining = max(0, chapters_total - covered)

    if days_to_exam <= 0:
        severity_10 = 10.0
    else:
        needed_pace  = remaining / days_to_exam             # chapters/day needed
        comfortable  = 2.0                                   # comfortable pace
        pace_factor  = min(1.0, needed_pace / (comfortable * 3))

        urgency_factor = 0.0
        if days_to_exam < 7:
            urgency_factor = 0.5
        elif days_to_exam < 14:
            urgency_factor = 0.3
        elif days_to_exam < 30:
            urgency_factor = 0.1

        completion_deficit = remaining / max(1, chapters_total)
        severity_raw       = (completion_deficit * 0.5 + pace_factor * 0.3 + urgency_factor * 0.2)
        severity_10        = round(min(10.0, severity_raw * 10), 1)

    if severity_10 >= 7.5:
        severity_label = "Critical"
        alert_level    = "critical"
        message        = (f"{subject} is at critical backlog risk. "
                          f"Only {days_to_exam} days until {exam_name}. "
                          f"Immediate action required.")
    elif severity_10 >= 5.0:
        severity_label = "High"
        alert_level    = "warning"
        message        = f"{subject} backlog is building up. Increase your study pace now."
    elif severity_10 >= 3.0:
        severity_label = "Moderate"
        alert_level    = "warning"
        message        = f"{subject} is slightly behind. A small push this week will help."
    elif severity_10 >= 1.5:
        severity_label = "Low"
        alert_level    = "safe"
        message        = f"{subject} is manageable — keep the current pace."
    else:
        severity_label = "On Track"
        alert_level    = "safe"
        message        = f"{subject} is looking good — maintain your current pace."

    chapters_per_day = round(remaining / max(1, days_to_exam), 1)

    catchup = {
        "chapters_remaining": remaining,
        "days_to_exam":       days_to_exam,
        "chapters_per_day":   chapters_per_day,
        "advice": (f"Study {chapters_per_day} chapters per day to clear your backlog in time."
                   if remaining > 0 else "Focus on revision — you have covered the syllabus.")
    }

    return {
        "subject":        subject,
        "severity_raw":   severity_10 / 10,
        "severity_10":    severity_10,
        "severity_label": severity_label,
        "alert_level":    alert_level,
        "message":        message,
        "catchup_plan":   catchup,
        "model_source":   "rule_based_fallback"    # clearly labelled as non-ML
    }


def predict_next_review_safe(attempts, topic_difficulty, last_score):
    """Calls LSTM model if available, else uses rule-based fallback."""
    if _FORGETTING_MODEL_AVAILABLE:
        try:
            result = _predict_next_review(
                attempts         = attempts,
                topic_difficulty = topic_difficulty,
                last_score       = last_score
            )
            result["model_source"] = "lstm"
            return result
        except Exception as e:
            logger.error(f"Forgetting model inference failed: {e}")

    return _rule_based_next_review(attempts, topic_difficulty, last_score)


def predict_backlog_safe(study_logs, subject, chapters_total, days_to_exam, exam_name):
    """Calls LSTM model if available, else uses rule-based fallback."""
    if _BACKLOG_MODEL_AVAILABLE:
        try:
            result = _predict_backlog(
                study_logs     = study_logs,
                subject        = subject,
                chapters_total = chapters_total,
                days_to_exam   = days_to_exam,
                exam_name      = exam_name
            )
            result["model_source"] = "lstm"
            return result
        except Exception as e:
            logger.error(f"Backlog model inference failed: {e}")

    return _rule_based_backlog(study_logs, subject, chapters_total, days_to_exam, exam_name)

class RagIngestRequest(BaseModel):
    paths: List[str]
    stream: Optional[str] = None
    subject: Optional[str] = None
    class_level: Optional[str] = None
    board: Optional[str] = None
    chapter: Optional[str] = None
    reindex: bool = False

class RagSearchRequest(BaseModel):
    query: str
    stream: Optional[str] = None
    subjects: Optional[List[str]] = None
    top_k: Optional[int] = None


# ── Helper ─────────────────────────────────────────────────────

def get_current_user(user_id: int) -> dict:
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "User not found"
        )
    return user


def require_admin(request: Request):
    admin_key = os.getenv("RAG_ADMIN_KEY")
    if not admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    provided_key = request.headers.get("X-Admin-Key", "")
    if not secrets.compare_digest(provided_key, admin_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )


# ── Auth routes ────────────────────────────────────────────────

@app.post("/auth/register")
def register(req: RegisterRequest):
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(400, "Email already registered")

    valid_streams = ["PCM", "PCB", "Commerce", "Arts", "University"]
    if req.stream not in valid_streams:
        raise HTTPException(400, f"Stream must be one of {valid_streams}")

    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    user_id = db.create_user(
        name     = req.name.strip(),
        email    = req.email.strip().lower(),
        password = req.password,
        stream   = req.stream
    )
    _seed_topics_for_user(user_id, req.stream)

    return {"message": "Account created successfully",
            "user_id": user_id, "stream": req.stream}


@app.post("/auth/login")
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email.strip().lower())
    if not user or not db.verify_password(req.password, user["password"]):
        raise HTTPException(401, "Invalid email or password")
    return {
        "message": "Login successful",
        "user_id": user["id"],
        "name":    user["name"],
        "stream":  user["stream"],
        "streak":  user["streak"],
        "xp":      user["xp"]
    }


# ── Curriculum routes ──────────────────────────────────────────

@app.get("/curriculum/{stream}")
def get_curriculum(stream: str):
    subjects = get_subjects_for_stream(stream)
    if not subjects:
        raise HTTPException(404, "Stream not found")
    result = {}
    for subject in subjects:
        topics = curriculum_topics(stream, subject)
        result[subject] = [
            {"name": t, "difficulty": get_difficulty(stream, subject, t)}
            for t in topics
        ]
    return {"stream": stream, "subjects": result}


# ── Subject routes ─────────────────────────────────────────────

@app.get("/subjects/{user_id}")
def list_subjects(user_id: int):
    subjects = db.get_subjects(user_id)
    return {"subjects": subjects}


@app.post("/subjects/{user_id}")
def add_subject(user_id: int, req: SubjectRequest):
    get_current_user(user_id)
    subject_id = db.create_subject(
        user_id        = user_id,
        name           = req.name,
        stream         = req.stream,
        exam_name      = req.exam_name,
        exam_date      = req.exam_date,
        chapters_total = req.chapters_total
    )
    topics = curriculum_topics(req.stream, req.name)
    for topic_name in topics:
        difficulty = get_difficulty(req.stream, req.name, topic_name)
        db.create_topic(
            subject_id = subject_id,
            user_id    = user_id,
            name       = topic_name,
            difficulty = difficulty
        )
    return {"message": f"Subject {req.name} added",
            "subject_id": subject_id,
            "topics_created": len(topics)}


# ── Topics route ───────────────────────────────────────────────

@app.get("/topics/{subject_id}")
def get_db_topics(subject_id: int):
    """Returns topics with database IDs and mastery for a subject."""
    with db.get_db() as conn:
        rows = conn.execute("""
            SELECT t.id, t.name, t.difficulty,
                   tm.mastery_score, tm.last_quiz_score, tm.attempts_count
            FROM topics t
            LEFT JOIN topic_mastery tm ON t.id = tm.topic_id
            WHERE t.subject_id = ?
            ORDER BY t.difficulty DESC
        """, (subject_id,)).fetchall()
    return {"topics": [dict(r) for r in rows]}


# ── Quiz routes ────────────────────────────────────────────────

@app.get("/quiz/{topic_id}/questions")
def get_quiz_questions(topic_id: int, difficulty: int = None):
    topic = db.get_topic_by_id(topic_id)
    if topic:
        existing_count = len(db.get_questions(topic_id, limit=100))
        # Only call LLM to generate if we have fewer than 10 questions
        if existing_count < 10:
            try:
                generated = llm.generate_questions(topic["name"])
                if not generated and existing_count == 0:
                    # Static fallback — clearly study-method-agnostic
                    generated = [
                        {
                            "question": f"Which of the following BEST describes a key principle of {topic['name']}?",
                            "option_a": "It relies on memorisation without understanding",
                            "option_b": "It requires understanding of foundational concepts and their applications",
                            "option_c": "It can be mastered by reading once",
                            "option_d": "It has no connection to other topics in the subject",
                            "answer": "b",
                            "explanation": f"Mastery of {topic['name']} requires understanding core principles and applying them across different contexts.",
                            "difficulty": int(round(topic.get("difficulty", 3)))
                        }
                    ]
                for q in generated:
                    db.add_question(
                        topic_id    = topic_id,
                        question    = q.get("question", ""),
                        option_a    = q.get("option_a", "A"),
                        option_b    = q.get("option_b", "B"),
                        option_c    = q.get("option_c", "C"),
                        option_d    = q.get("option_d", "D"),
                        answer      = q.get("answer", "a").lower(),
                        explanation = q.get("explanation", ""),
                        difficulty  = q.get("difficulty", 3),
                        source      = "ai_generated"
                    )
            except Exception as e:
                logger.warning(f"Question generation failed for topic {topic_id}: {e}")

    questions = db.get_questions(
        topic_id   = topic_id,
        difficulty = difficulty,
        limit      = 10
    )
    if not questions:
        raise HTTPException(404, "No questions found for this topic. Add questions first.")

    for q in questions:
        q.pop("answer",      None)
        q.pop("explanation", None)
    return {"questions": questions, "total": len(questions)}


@app.post("/quiz/check/{topic_id}")
def check_quiz_answers(topic_id: int, req: QuizCheckRequest):
    """
    Scores a quiz server-side.
    Receives {question_id: chosen_option} and returns
    score, per-question results, and correct answers.
    """
    with db.get_db() as conn:
        rows = conn.execute(
            "SELECT id, answer, explanation, difficulty FROM questions WHERE topic_id = ?",
            (topic_id,)
        ).fetchall()

    if not rows:
        raise HTTPException(404, "No questions found for this topic")

    results = {}
    correct = 0
    total   = len(rows)

    for row in rows:
        qid      = str(row["id"])
        chosen   = req.answers.get(qid, "")
        is_right = chosen.lower() == row["answer"].lower()
        if is_right:
            correct += 1
        results[qid] = {
            "correct":     is_right,
            "chosen":      chosen,
            "answer":      row["answer"],
            "explanation": row["explanation"],
            "difficulty":  row["difficulty"]
        }

    score = round((correct / total) * 100) if total else 0
    return {
        "score":   score,
        "correct": correct,
        "total":   total,
        "results": results
    }


@app.post("/quiz/submit/{user_id}")
def submit_quiz(user_id: int, req: QuizSubmitRequest):
    get_current_user(user_id)

    # Save aggregate quiz attempt
    attempt_id = db.save_quiz_attempt(
        user_id       = user_id,
        topic_id      = req.topic_id,
        score         = req.score,
        time_spent    = req.time_spent,
        self_rating   = req.self_rating,
        difficulty    = req.difficulty,
        correct_count = req.correct_count,
        total_count   = req.total_count
    )

    # Save per-question attempts if provided
    if req.question_attempts:
        for qa in req.question_attempts:
            if isinstance(qa, dict):
                db.save_question_attempt(
                    user_id        = user_id,
                    quiz_attempt_id= attempt_id,
                    topic_id       = req.topic_id,
                    question_id    = qa.get("question_id"),
                    chosen_option  = qa.get("chosen_option", ""),
                    correct_option = qa.get("correct_option", ""),
                    is_correct     = qa.get("is_correct", False),
                    time_spent_sec = qa.get("time_spent_sec", 0.0)
                )

    # Update topic mastery
    db.upsert_topic_mastery(
        user_id    = user_id,
        topic_id   = req.topic_id,
        score      = req.score,
        difficulty = req.difficulty
    )

    topic = db.get_topic_by_id(req.topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")

    # Build attempt history for forgetting model
    attempts_raw = db.get_quiz_attempts(user_id, req.topic_id, limit=10)
    attempts = []
    for a in attempts_raw:
        attempts.append({
            "score":       a["score"],
            "time_spent":  a["time_spent"],
            "self_rating": a["self_rating"],
            "timestamp":   datetime.fromisoformat(a["timestamp"])
        })

    # Predict next review (ML or rule-based fallback)
    prediction = predict_next_review_safe(
        attempts         = attempts,
        topic_difficulty = topic["difficulty"],
        last_score       = req.score
    )

    db.upsert_review_schedule(
        user_id     = user_id,
        topic_id    = req.topic_id,
        next_review = prediction["next_review"],
        recall_prob = prediction["recall_prob"],
        days_until  = prediction["days_until"],
        urgency     = prediction["urgency"],
        message     = prediction["message"]
    )

    # XP and streak update
    xp_earned = _calculate_xp(req.score, req.difficulty)
    db.update_streak_and_xp(user_id, xp_earned)

    # Log learning event
    db.log_learning_event(
        user_id    = user_id,
        topic_id   = req.topic_id,
        event_type = "QUIZ_COMPLETED",
        score      = req.score,
        time_spent = req.time_spent
    )

    return {
        "message":    "Quiz submitted",
        "attempt_id": attempt_id,
        "score":      req.score,
        "xp_earned":  xp_earned,
        "prediction": prediction
    }


@app.post("/quiz/questions/add")
def add_question(req: AddQuestionRequest):
    question_id = db.add_question(
        topic_id    = req.topic_id,
        question    = req.question,
        option_a    = req.option_a,
        option_b    = req.option_b,
        option_c    = req.option_c,
        option_d    = req.option_d,
        answer      = req.answer,
        explanation = req.explanation,
        difficulty  = req.difficulty
    )
    return {"message": "Question added", "question_id": question_id}


# ── Study plan route ──────────────────────────────────────────

@app.post("/study-plan/{user_id}")
def generate_study_plan(user_id: int, req: StudyPlanRequest):
    get_current_user(user_id)

    subject = db.get_subject_by_id(req.subject_id)
    if not subject:
        raise HTTPException(404, "Subject not found")

    # Get topics with mastery data
    with db.get_db() as conn:
        rows = conn.execute("""
            SELECT t.id, t.name, t.difficulty,
                   COALESCE(tm.mastery_score, 0) as mastery_score,
                   COALESCE(tm.last_quiz_score, 0) as last_quiz_score
            FROM topics t
            LEFT JOIN topic_mastery tm ON t.id = tm.topic_id AND tm.user_id = ?
            WHERE t.subject_id = ?
            ORDER BY t.difficulty DESC
        """, (user_id, req.subject_id)).fetchall()
    topics = [dict(r) for r in rows]

    if not topics:
        raise HTTPException(404, "No topics found for this subject")

    try:
        exam_dt      = datetime.strptime(req.exam_date, "%Y-%m-%d")
        days_to_exam = max(1, (exam_dt - datetime.now()).days)
    except Exception:
        raise HTTPException(400, "Invalid exam date format. Use YYYY-MM-DD")

    today = datetime.now().date()

    # Sort: unmastered hard topics first, mastered easy topics last
    def sort_key(t):
        mastery_inv = 1.0 - min(1.0, t.get("mastery_score", 0) / 100)
        difficulty  = t["difficulty"] / 5
        return (mastery_inv * 0.6 + difficulty * 0.4)

    topics_sorted  = sorted(topics, key=sort_key, reverse=True)
    study_days     = max(1, int(days_to_exam * 0.9))
    topics_count   = len(topics_sorted)
    topics_per_day = max(1, round(topics_count / study_days))

    def topic_minutes(diff, mastery):
        base = {5: 60, 4: 50, 3: 40, 2: 30, 1: 20}.get(int(round(diff)), 30)
        return max(15, int(base * (1 - min(0.5, mastery / 200))))

    daily_schedule = []
    topic_idx = 0

    for day_num in range(1, study_days + 1):
        day_date   = today + timedelta(days=day_num - 1)
        day_topics = []
        day_mins   = 0
        batch_size = topics_per_day + (1 if day_num <= study_days * 0.3 else 0)

        for _ in range(batch_size):
            if topic_idx >= topics_count:
                break
            t    = topics_sorted[topic_idx]
            mins = topic_minutes(t["difficulty"], t.get("mastery_score", 0))
            day_topics.append({
                "name":          t["name"],
                "difficulty":    t["difficulty"],
                "minutes":       mins,
                "topic_id":      t["id"],
                "mastery_score": round(t.get("mastery_score", 0), 1)
            })
            day_mins  += mins
            topic_idx += 1

        if not day_topics:
            break

        note = None
        if day_mins > 120:
            note = "Heavy day — consider splitting into two sessions."
        elif all(t["difficulty"] >= 4.0 for t in day_topics):
            note = "All hard topics today — take breaks every 45 minutes."

        daily_schedule.append({
            "day_number":        day_num,
            "date":              day_date.isoformat(),
            "date_label":        day_date.strftime("%a, %d %b"),
            "is_today":          day_date == today,
            "is_past":           day_date < today,
            "topics":            day_topics,
            "estimated_minutes": day_mins,
            "note":              note
        })

    # Backlog analysis
    topics_scheduled  = sum(len(d["topics"]) for d in daily_schedule)
    comfortable_pace  = 3
    severity_raw      = min(10, max(0, round((topics_per_day - comfortable_pace) / comfortable_pace * 10)))
    if days_to_exam < 7:
        severity_raw = min(10, severity_raw + 4)
    elif days_to_exam < 14:
        severity_raw = min(10, severity_raw + 2)
    alert_level = "critical" if severity_raw >= 7 else "warning" if severity_raw >= 4 else "safe"

    at_risk = []
    cutoff_day = int(study_days * 0.8)
    for day in daily_schedule:
        if day["day_number"] > cutoff_day:
            for t in day["topics"]:
                if t["difficulty"] >= 4.0 and t.get("mastery_score", 0) < 50:
                    at_risk.append({
                        "name":          t["name"],
                        "difficulty":    t["difficulty"],
                        "scheduled_day": day["day_number"],
                        "mastery_score": t.get("mastery_score", 0)
                    })

    catchup_advice = []
    if severity_raw >= 4:
        catchup_advice.append(
            f"You have {topics_count} topics in {days_to_exam} days — "
            f"aim for {topics_per_day} topics/day minimum."
        )
    if at_risk:
        catchup_advice.append(
            f"{len(at_risk)} hard unmastered topics are scheduled late. "
            "Consider moving them earlier to allow revision time."
        )
    catchup_advice.append("Use the Quiz feature daily to reinforce topics you have studied.")
    catchup_advice.append("Log your study sessions so the system can update your backlog prediction.")

    # Persist the plan to DB
    db.save_study_plan(
        user_id        = user_id,
        subject_id     = req.subject_id,
        exam_date      = req.exam_date,
        exam_name      = req.exam_name,
        days_to_exam   = days_to_exam,
        total_topics   = topics_count,
        topics_per_day = topics_per_day,
        plan_json      = json.dumps(daily_schedule)
    )

    backlog_message = (
        f"You need to cover {topics_count} topics in {days_to_exam} days "
        f"({topics_per_day} topics/day). "
        + ("This is a heavy load — start immediately." if severity_raw >= 7
           else "This is manageable with consistent effort." if severity_raw >= 4
           else "You are on a comfortable pace.")
    )

    return {
        "subject":          subject["name"],
        "exam_name":        req.exam_name,
        "exam_date":        req.exam_date,
        "days_to_exam":     days_to_exam,
        "total_topics":     topics_count,
        "topics_per_day":   topics_per_day,
        "study_days":       study_days,
        "daily_schedule":   daily_schedule,
        "backlog_severity": severity_raw,
        "alert_level":      alert_level,
        "backlog_message":  backlog_message,
        "at_risk_topics":   at_risk,
        "catchup_advice":   catchup_advice,
        "message":          f"Your {days_to_exam}-day study plan for {subject['name']} — {req.exam_name}"
    }


# ── Study log routes ───────────────────────────────────────────

@app.post("/study-log/{user_id}")
def log_study_session(user_id: int, req: StudyLogRequest):
    get_current_user(user_id)

    db.save_study_log(
        user_id        = user_id,
        subject_id     = req.subject_id,
        topics_covered = req.topics_covered,
        study_time     = req.study_time,
        quiz_score     = req.quiz_score,
        days_skipped   = req.days_skipped,
        self_rating    = req.self_rating,
        notes          = req.notes
    )

    subject = db.get_subject_by_id(req.subject_id)
    if not subject:
        raise HTTPException(404, "Subject not found")

    logs_raw = db.get_study_logs(user_id, req.subject_id, limit=14)
    study_logs = []
    for log in logs_raw:
        try:
            date_val = datetime.fromisoformat(str(log["date"]))
        except Exception:
            date_val = datetime.now()
        study_logs.append({
            "date":           date_val,
            "topics_covered": log["topics_covered"],
            "study_time":     log["study_time"],
            "quiz_score":     log["quiz_score"],
            "days_skipped":   log["days_skipped"]
        })

    days_to_exam = 30
    if subject.get("exam_date"):
        try:
            exam_dt      = datetime.strptime(subject["exam_date"], "%Y-%m-%d")
            days_to_exam = max(1, (exam_dt - datetime.now()).days)
        except Exception:
            pass

    # Backlog prediction — ML or rule-based fallback
    backlog = predict_backlog_safe(
        study_logs     = study_logs,
        subject        = subject["name"],
        chapters_total = subject["chapters_total"],
        days_to_exam   = days_to_exam,
        exam_name      = subject.get("exam_name", "your exam")
    )

    db.upsert_backlog_alert(
        user_id        = user_id,
        subject_id     = req.subject_id,
        severity_10    = backlog["severity_10"],
        severity_label = backlog["severity_label"],
        alert_level    = backlog["alert_level"],
        message        = backlog["message"],
        catchup_plan   = json.dumps(backlog["catchup_plan"])
    )

    # Update streak and XP
    db.update_streak_and_xp(user_id, xp_earned=20)

    # Log learning event
    db.log_learning_event(
        user_id    = user_id,
        topic_id   = None,
        event_type = "STUDY_SESSION_COMPLETED",
        score      = req.quiz_score,
        time_spent = req.study_time
    )

    return {"message": "Study session logged", "backlog": backlog}


# ── Copilot routes ─────────────────────────────────────────────

@app.post("/copilot/chat/{user_id}")
def copilot_chat(user_id: int, req: CopilotChatRequest):
    get_current_user(user_id)

    # Get or create a conversation
    conv_id = req.conversation_id
    if not conv_id:
        conv_id = db.create_conversation(user_id)
    else:
        # Verify the conversation belongs to this user
        if not db.conversation_belongs_to_user(conv_id, user_id):
            conv_id = db.create_conversation(user_id)

    # Save the user message
    db.save_message(conv_id, "user", req.message)

    # Build history from DB (last 10 messages) + any extra in-memory history from client
    db_history = db.get_conversation_messages(conv_id, limit=10)
    history_for_llm = [{"role": m["role"], "text": m["content"]} for m in db_history[:-1]]  # exclude just-saved user msg

    try:
        response = llm.ask_copilot(user_id, req.message, history_for_llm)
    except Exception as e:
        logger.error(f"Copilot error for user {user_id}: {e}")
        response = "⚠️ AI Copilot is temporarily unavailable. Please try again in a moment."

    # Save the assistant response
    db.save_message(conv_id, "assistant", response)

    return {"reply": response, "conversation_id": conv_id}


@app.get("/copilot/conversations/{user_id}")
def get_conversations(user_id: int):
    """Returns list of the user's conversation threads."""
    get_current_user(user_id)
    conversations = db.get_user_conversations(user_id)
    return {"conversations": conversations}


@app.get("/copilot/conversation/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str, user_id: int):
    """Returns messages in a conversation thread."""
    if not db.conversation_belongs_to_user(conversation_id, user_id):
        raise HTTPException(403, "Access denied")
    messages = db.get_conversation_messages(conversation_id, limit=50)
    return {"messages": messages}


# ── RAG routes ────────────────────────────────────────────────

@app.post("/rag/ingest")
def rag_ingest(req: RagIngestRequest, request: Request):
    if not _RAG_AVAILABLE or rag is None:
        raise HTTPException(503, "RAG dependencies are not installed on this server")
    require_admin(request)
    metadata = {
        "stream": req.stream,
        "subject": req.subject,
        "class_level": req.class_level,
        "board": req.board,
        "chapter": req.chapter
    }
    try:
        results = rag.ingest_paths(req.paths, metadata, reindex=req.reindex)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ingested": results, "count": len(results)}


@app.post("/rag/search")
def rag_search(req: RagSearchRequest, request: Request):
    if not _RAG_AVAILABLE or rag is None:
        raise HTTPException(503, "RAG dependencies are not installed on this server")
    require_admin(request)
    documents = rag.retrieve_documents(
        query=req.query,
        stream=req.stream,
        subjects=req.subjects,
        top_k=req.top_k
    )
    return {"matches": [rag.serialize_document(doc) for doc in documents]}


# ── Dashboard route ────────────────────────────────────────────

@app.get("/dashboard/{user_id}")
def get_dashboard(user_id: int):
    get_current_user(user_id)
    summary        = db.get_dashboard_summary(user_id)
    review_queue   = db.get_todays_review(user_id)
    backlog_alerts = db.get_backlog_alerts(user_id)
    weak_topics    = db.get_weak_topics(user_id, limit=5)
    recent_quizzes = db.get_recent_quiz_attempts(user_id, limit=5)

    for alert in backlog_alerts:
        if alert.get("catchup_plan"):
            try:
                alert["catchup_plan"] = json.loads(alert["catchup_plan"])
            except Exception:
                pass

    return {
        "summary":        summary,
        "review_queue":   review_queue,
        "backlog_alerts": backlog_alerts,
        "weak_topics":    weak_topics,
        "recent_quizzes": recent_quizzes,
        "generated_at":   datetime.now().isoformat()
    }


# ── Analytics route ────────────────────────────────────────────

@app.get("/analytics/{user_id}")
def get_analytics(user_id: int):
    """
    Returns real analytics data from the database.
    Fake/heuristic predictions have been removed.
    Predictions that require sufficient data will show
    'insufficient_data' status until enough data is collected.
    """
    get_current_user(user_id)
    summary = db.get_dashboard_summary(user_id)

    # 1. Retention Curves — from actual review schedule (real recall_prob values)
    reviews = db.get_todays_review(user_id)
    all_reviews = db.get_all_review_schedule(user_id)
    retention_curves = []
    days = [0, 1, 3, 7, 14, 30]
    for r in all_reviews[:5]:  # top 5 topics with review schedules
        base_recall = r["recall_prob"] * 100
        # Use the stored recall_prob as the starting point — decay is illustrative
        decay_data = []
        for d in days:
            # Ebbinghaus-inspired decay from the stored recall probability
            decay = base_recall * (0.9 ** d)
            decay_data.append({"day": d, "recall": round(min(100, max(0, decay)), 1)})
        retention_curves.append({
            "topic":          r["topic_name"],
            "current_recall": round(base_recall, 1),
            "urgency":        r["urgency"],
            "curve":          decay_data
        })

    # 2. Subject Heatmap — real per-subject average scores from quiz_attempts
    heatmap_data = db.get_subject_performance(user_id)

    # 3. Topic mastery breakdown
    mastery_data = db.get_all_topic_mastery(user_id)

    # 4. Recent quiz performance trend (last 20 attempts)
    recent_attempts = db.get_recent_quiz_attempts(user_id, limit=20)

    # 5. Exam prediction — only show if we have enough data (>= 10 quiz attempts)
    total_attempts = summary.get("total_quiz_attempts", 0)
    if total_attempts >= 10:
        avg_score = summary["avg_score"] or 0
        exam_prediction = {
            "status":          "available",
            "estimated_score": round(avg_score, 1),
            "confidence":      "low",
            "data_points":     total_attempts,
            "note":            "Estimated from quiz history. Accuracy improves with more attempts."
        }
    else:
        exam_prediction = {
            "status":      "insufficient_data",
            "data_points": total_attempts,
            "required":    10,
            "note":        f"Complete at least 10 quizzes to generate exam predictions. ({total_attempts}/10 done)"
        }

    return {
        "retention_curves":   retention_curves,
        "heatmap":            heatmap_data,
        "mastery_breakdown":  mastery_data,
        "recent_performance": recent_attempts,
        "exam_prediction":    exam_prediction,
        "model_status": {
            "forgetting_model": "lstm" if _FORGETTING_MODEL_AVAILABLE else "rule_based_fallback",
            "backlog_model":    "lstm" if _BACKLOG_MODEL_AVAILABLE    else "rule_based_fallback"
        }
    }


# ── Student context endpoint ────────────────────────────────────

@app.get("/student-context/{user_id}")
def get_student_context(user_id: int):
    """Returns the full student learning context used by the Copilot."""
    get_current_user(user_id)
    context = llm.build_student_context(user_id)
    return {"context": context}


# ── Health check ───────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status":  "running",
        "version": "2.0.0",
        "time":    datetime.now().isoformat(),
        "models": {
            "forgetting": "lstm" if _FORGETTING_MODEL_AVAILABLE else "rule_based_fallback",
            "backlog":    "lstm" if _BACKLOG_MODEL_AVAILABLE    else "rule_based_fallback"
        }
    }


# ── Serve React frontend ───────────────────────────────────────

frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True),
              name="static")


# ── Helpers ────────────────────────────────────────────────────

def _seed_topics_for_user(user_id: int, stream: str):
    subjects = get_subjects_for_stream(stream)
    for subject_name in subjects:
        subject_id = db.create_subject(
            user_id        = user_id,
            name           = subject_name,
            stream         = stream,
            exam_name      = "Board Exam",
            exam_date      = (datetime.now() +
                              timedelta(days=90)).strftime("%Y-%m-%d"),
            chapters_total = len(curriculum_topics(stream, subject_name))
        )
        for topic_name in curriculum_topics(stream, subject_name):
            db.create_topic(
                subject_id = subject_id,
                user_id    = user_id,
                name       = topic_name,
                difficulty = get_difficulty(stream, subject_name, topic_name)
            )


def _calculate_xp(score: float, difficulty: int) -> int:
    return 10 + int(score / 10) + difficulty * 2


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
