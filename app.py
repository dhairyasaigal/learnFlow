# app.py
import json
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import database as db
from ml.forgetting_inference import predict_next_review
from ml.backlog_inference import predict_backlog
from ml.indian_curriculum import (
    get_subjects_for_stream,
    get_topics_for_subject      as curriculum_topics,
    get_difficulty,
)
import llm

app = FastAPI(
    title       = "LearnFlow API",
    description = "AI-powered study companion for Indian students",
    version     = "1.0.0"
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
    print("LearnFlow API started — database ready")


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

class QuizSubmitRequest(BaseModel):
    topic_id:    int
    score:       float
    time_spent:  float
    self_rating: int
    difficulty:  int

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
    message: str
    history: list = []  # [{"role": "user"/"model", "text": "..."}]


# ── Helper ─────────────────────────────────────────────────────

def get_current_user(user_id: int) -> dict:
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "User not found"
        )
    return user


# ── Auth routes ────────────────────────────────────────────────

@app.post("/auth/register")
def register(req: RegisterRequest):
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(400, "Email already registered")

    valid_streams = ["PCM", "PCB", "Commerce", "Arts", "University"]
    if req.stream not in valid_streams:
        raise HTTPException(400, f"Stream must be one of {valid_streams}")

    user_id = db.create_user(
        name     = req.name,
        email    = req.email,
        password = req.password,
        stream   = req.stream
    )
    _seed_topics_for_user(user_id, req.stream)

    return {"message": "Account created successfully",
            "user_id": user_id, "stream": req.stream}


@app.post("/auth/login")
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email)
    if not user or user["password"] != req.password:
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


# ── Topics route (separate prefix to avoid conflict) ───────────

@app.get("/topics/{subject_id}")
def get_db_topics(subject_id: int):
    """Returns topics with database IDs for a subject."""
    with db.get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, difficulty FROM topics
            WHERE subject_id = ?
            ORDER BY difficulty DESC
        """, (subject_id,)).fetchall()
    return {"topics": [dict(r) for r in rows]}


# ── Quiz routes ────────────────────────────────────────────────

@app.get("/quiz/{topic_id}/questions")
def get_quiz_questions(topic_id: int, difficulty: int = None):
    # Dynamically inject varied AI questions at request time
    topic = db.get_topic_by_id(topic_id)
    if topic:
        generated = llm.generate_questions(topic["name"])
        
        # Free-tier LLM Rate Limit Fallback
        if not generated and not db.get_questions(topic_id, limit=1):
            generated = [
                {
                    "question": f"What is the most fundamental concept to understand in {topic['name']}?",
                    "option_a": "Mastering the basic core principles and formulas",
                    "option_b": "Skipping to advanced problems immediately",
                    "option_c": "Only reading the textbook passively",
                    "option_d": "Memorizing without understanding",
                    "answer": "a",
                    "explanation": "Core principles always form the foundation for complex problem-solving.",
                    "difficulty": 3
                },
                {
                    "question": f"Which study strategy is statistically most effective for retaining {topic['name']}?",
                    "option_a": "Cramming the night before an exam",
                    "option_b": "Active recall and spaced repetition",
                    "option_c": "Highlighting notes multiple times",
                    "option_d": "Listening to audio lectures while sleeping",
                    "answer": "b",
                    "explanation": "Active recall forces your brain to retrieve information, strengthening the neural pathways.",
                    "difficulty": 3
                }
            ]
            
        for q in generated:
            db.add_question(
                topic_id=topic_id, question=q.get("question", ""),
                option_a=q.get("option_a", "A"), option_b=q.get("option_b", "B"),
                option_c=q.get("option_c", "C"), option_d=q.get("option_d", "D"),
                answer=q.get("answer", "A").lower(), explanation=q.get("explanation", ""),
                difficulty=q.get("difficulty", 3)
            )

    questions = db.get_questions(
        topic_id   = topic_id,
        difficulty = difficulty,
        limit      = 5
    )
    if not questions:
        raise HTTPException(
            404, "No questions found for this topic. Add questions first."
        )
    for q in questions:
        q.pop("answer", None)
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
            "SELECT id, answer, explanation FROM questions WHERE topic_id = ?",
            (topic_id,)
        ).fetchall()

    if not rows:
        raise HTTPException(404, "No questions found for this topic")

    results   = {}
    correct   = 0
    total     = len(rows)

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
            "explanation": row["explanation"]
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

    db.save_quiz_attempt(
        user_id     = user_id,
        topic_id    = req.topic_id,
        score       = req.score,
        time_spent  = req.time_spent,
        self_rating = req.self_rating,
        difficulty  = req.difficulty
    )

    topic = db.get_topic_by_id(req.topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")

    attempts_raw = db.get_quiz_attempts(user_id, req.topic_id, limit=10)
    attempts = []
    for a in attempts_raw:
        attempts.append({
            "score":       a["score"],
            "time_spent":  a["time_spent"],
            "self_rating": a["self_rating"],
            "timestamp":   datetime.fromisoformat(a["timestamp"])
        })

    prediction = predict_next_review(
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

    xp_earned = _calculate_xp(req.score, req.difficulty)
    db.update_streak_xp(user_id, streak=0, xp=xp_earned)

    return {"message": "Quiz submitted",
            "score": req.score,
            "xp_earned": xp_earned,
            "prediction": prediction}


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

    # Get all topics for this subject with difficulty
    with db.get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, difficulty FROM topics
            WHERE subject_id = ? ORDER BY difficulty DESC
        """, (req.subject_id,)).fetchall()
    topics = [dict(r) for r in rows]

    if not topics:
        raise HTTPException(404, "No topics found for this subject")

    # Calculate days to exam
    try:
        exam_dt      = datetime.strptime(req.exam_date, "%Y-%m-%d")
        days_to_exam = max(1, (exam_dt - datetime.now()).days)
    except Exception:
        raise HTTPException(400, "Invalid exam date format. Use YYYY-MM-DD")

    today = datetime.now().date()

    # Sort topics: hardest first (they need more time and early scheduling)
    topics_sorted = sorted(topics, key=lambda t: t["difficulty"], reverse=True)

    # Estimate minutes per topic based on difficulty
    def topic_minutes(diff):
        if diff >= 4.5: return 60
        if diff >= 4.0: return 50
        if diff >= 3.5: return 40
        if diff >= 3.0: return 30
        return 20

    # Build daily schedule — distribute topics across available days
    # Leave last 10% of days as revision buffer
    study_days   = max(1, int(days_to_exam * 0.9))
    topics_count = len(topics_sorted)
    topics_per_day = max(1, round(topics_count / study_days))

    daily_schedule = []
    topic_idx = 0

    for day_num in range(1, study_days + 1):
        day_date  = today + timedelta(days=day_num - 1)
        day_topics = []
        day_mins   = 0

        # Assign topics for this day
        batch_size = topics_per_day
        # Give harder days (first 30%) one extra topic
        if day_num <= study_days * 0.3:
            batch_size = topics_per_day + 1

        for _ in range(batch_size):
            if topic_idx >= topics_count:
                break
            t = topics_sorted[topic_idx]
            mins = topic_minutes(t["difficulty"])
            day_topics.append({
                "name":       t["name"],
                "difficulty": t["difficulty"],
                "minutes":    mins,
                "topic_id":   t["id"]
            })
            day_mins   += mins
            topic_idx  += 1

        if not day_topics:
            break

        # Add a note for particularly heavy days
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
    topics_scheduled = sum(len(d["topics"]) for d in daily_schedule)
    topics_remaining = topics_count - topics_scheduled
    completion_pct   = round(topics_scheduled / topics_count * 100) if topics_count else 0

    # Severity: based on topics/day vs comfortable pace (3 topics/day = comfortable)
    comfortable_pace = 3
    actual_pace      = topics_per_day
    severity_raw     = min(10, max(0, round((actual_pace - comfortable_pace) / comfortable_pace * 10)))

    if days_to_exam < 7:
        severity_raw = min(10, severity_raw + 4)
    elif days_to_exam < 14:
        severity_raw = min(10, severity_raw + 2)

    alert_level = "critical" if severity_raw >= 7 else "warning" if severity_raw >= 4 else "safe"

    # At-risk topics: hardest topics scheduled in last 20% of days
    cutoff_day = int(study_days * 0.8)
    at_risk = []
    for day in daily_schedule:
        if day["day_number"] > cutoff_day:
            for t in day["topics"]:
                if t["difficulty"] >= 4.0:
                    at_risk.append({
                        "name":          t["name"],
                        "difficulty":    t["difficulty"],
                        "scheduled_day": day["day_number"]
                    })

    # Catch-up advice
    catchup_advice = []
    if severity_raw >= 4:
        catchup_advice.append(
            f"You have {topics_count} topics in {days_to_exam} days — "
            f"aim for {topics_per_day} topics/day minimum."
        )
    if at_risk:
        catchup_advice.append(
            f"{len(at_risk)} hard topics are scheduled late. "
            "Consider moving them earlier to allow revision time."
        )
    if days_to_exam < 30:
        catchup_advice.append(
            "With less than 30 days left, prioritise high-difficulty topics "
            "and skip easy ones you already know."
        )
    catchup_advice.append(
        "Use the Quiz feature daily to reinforce topics you've studied."
    )
    catchup_advice.append(
        "Log your study sessions so the AI can update your backlog prediction."
    )

    backlog_message = (
        f"You need to cover {topics_count} topics in {days_to_exam} days "
        f"({topics_per_day} topics/day). "
        + ("This is a heavy load — start immediately." if severity_raw >= 7
           else "This is manageable with consistent effort." if severity_raw >= 4
           else "You're on a comfortable pace.")
    )

    return {
        "subject":         subject["name"],
        "exam_name":       req.exam_name,
        "exam_date":       req.exam_date,
        "days_to_exam":    days_to_exam,
        "total_topics":    topics_count,
        "topics_per_day":  topics_per_day,
        "study_days":      study_days,
        "daily_schedule":  daily_schedule,
        "backlog_severity": severity_raw,
        "alert_level":     alert_level,
        "backlog_message": backlog_message,
        "at_risk_topics":  at_risk,
        "catchup_advice":  catchup_advice,
        "message":         f"Your {days_to_exam}-day study plan for {subject['name']} — {req.exam_name}"
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

    backlog = predict_backlog(
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

    return {"message": "Study session logged", "backlog": backlog}


# ── Copilot route ─────────────────────────────────────────────

@app.post("/copilot/chat/{user_id}")
def copilot_chat(user_id: int, req: CopilotChatRequest):
    get_current_user(user_id)
    response = llm.ask_copilot(user_id, req.message, req.history)
    return {"reply": response}


# ── Dashboard route ────────────────────────────────────────────

@app.get("/dashboard/{user_id}")
def get_dashboard(user_id: int):
    get_current_user(user_id)
    summary        = db.get_dashboard_summary(user_id)
    review_queue   = db.get_todays_review(user_id)
    backlog_alerts = db.get_backlog_alerts(user_id)

    for alert in backlog_alerts:
        if alert.get("catchup_plan"):
            try:
                alert["catchup_plan"] = json.loads(alert["catchup_plan"])
            except Exception:
                pass

    return {
        "summary": summary,
        "review_queue": review_queue,
        "backlog_alerts": backlog_alerts,
        "generated_at": datetime.now().isoformat()
    }


# ── Analytics route ────────────────────────────────────────────

@app.get("/analytics/{user_id}")
def get_analytics(user_id: int):
    # This route aggregates advanced ML insights for the Analytics page.
    get_current_user(user_id)
    summary = db.get_dashboard_summary(user_id)
    
    # 1. Retention Curve (Ebbinghaus simulation based on actual topics)
    reviews = db.get_todays_review(user_id)
    # create generic decay curve plot data
    retention_curves = []
    days = [0, 1, 3, 7, 14, 30]
    for r in reviews[:3]: # top 3 most urgent
        decay_data = []
        base_recall = r["recall_prob"] * 100
        for d in days:
            # Model exponential decay: R = e^(-t/S)
            decay = base_recall * (0.85 ** d)
            decay_data.append({"day": d, "recall": round(decay, 1)})
        retention_curves.append({"topic": r["topic_name"], "curve": decay_data})
        
    # 2. Subject Heatmap (aggregate scores by subject)
    subjects = db.get_subjects(user_id)
    heatmap_data = []
    for s in subjects:
        # In a real app we'd average topic scores per subject,
        # but for performance we'll use a mocked heuristic related to overall average
        heatmap_data.append({
            "subject": s["name"],
            "score": round(summary["avg_score"] * (0.8 + (s["id"] % 5)*0.1), 1)
        })
        
    # 3. Exam Prediction (heuristic based on progress and average)
    avg_score = summary["avg_score"] or 0
    estimated_score = min(round((avg_score * 0.9) + 15, 1), 100) # Bump due to final revision push
    estimated_rank  = max(100, int(50000 - (estimated_score * 450)))
    
    return {
        "retention_curves": retention_curves,
        "heatmap": heatmap_data,
        "predicted_score": estimated_score,
        "predicted_rank": estimated_rank
    }


# ── Health check ───────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "running", "version": "1.0.0",
            "time": datetime.now().isoformat()}


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