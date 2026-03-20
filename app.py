# app.py
# FastAPI entry point for LearnFlow
# Connects database, inference engines and frontend

import json
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

import database as db
from ml.forgetting_inference import predict_next_review, predict_all_topics
from ml.backlog_inference import predict_backlog, predict_all_subjects
from ml.indian_curriculum import (
    get_subjects_for_stream,
    get_topics_for_subject,
    get_difficulty,
    get_stream_summary
)

# ─────────────────────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────────────────────

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

# Initialise database on startup
@app.on_event("startup")
async def startup():
    db.create_tables()
    print("LearnFlow API started — database ready")


# ─────────────────────────────────────────────────────────────
# Pydantic models — request/response schemas
# ─────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:   str
    email:  str
    password: str
    stream: str   # PCM / PCB / Commerce / Arts / University

class LoginRequest(BaseModel):
    email:    str
    password: str

class SubjectRequest(BaseModel):
    name:           str
    stream:         str
    exam_name:      str
    exam_date:      str   # YYYY-MM-DD
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


# ─────────────────────────────────────────────────────────────
# Simple session — user_id passed in header
# ─────────────────────────────────────────────────────────────

def get_current_user(user_id: int) -> dict:
    """Get user from database by ID."""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail      = "User not found"
        )
    return user


# ─────────────────────────────────────────────────────────────
# Auth routes
# ─────────────────────────────────────────────────────────────

@app.post("/auth/register")
def register(req: RegisterRequest):
    # Check email not already used
    existing = db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code = 400,
            detail      = "Email already registered"
        )

    # Validate stream
    valid_streams = ["PCM", "PCB", "Commerce", "Arts", "University"]
    if req.stream not in valid_streams:
        raise HTTPException(
            status_code = 400,
            detail      = f"Stream must be one of {valid_streams}"
        )

    # Create user — in production hash the password
    user_id = db.create_user(
        name     = req.name,
        email    = req.email,
        password = req.password,
        stream   = req.stream
    )

    # Auto-create topics from curriculum for their stream
    _seed_topics_for_user(user_id, req.stream)

    return {
        "message": "Account created successfully",
        "user_id": user_id,
        "stream":  req.stream
    }


@app.post("/auth/login")
def login(req: LoginRequest):
    user = db.get_user_by_email(req.email)
    if not user or user["password"] != req.password:
        raise HTTPException(
            status_code = 401,
            detail      = "Invalid email or password"
        )
    return {
        "message": "Login successful",
        "user_id": user["id"],
        "name":    user["name"],
        "stream":  user["stream"],
        "streak":  user["streak"],
        "xp":      user["xp"]
    }


# ─────────────────────────────────────────────────────────────
# Curriculum routes
# ─────────────────────────────────────────────────────────────

@app.get("/curriculum/{stream}")
def get_curriculum(stream: str):
    """Returns full subject + topic list for a stream."""
    subjects = get_subjects_for_stream(stream)
    if not subjects:
        raise HTTPException(404, "Stream not found")

    result = {}
    for subject in subjects:
        topics = get_topics_for_subject(stream, subject)
        result[subject] = [
            {
                "name":       topic,
                "difficulty": get_difficulty(stream, subject, topic)
            }
            for topic in topics
        ]
    return {"stream": stream, "subjects": result}


# ─────────────────────────────────────────────────────────────
# Subject routes
# ─────────────────────────────────────────────────────────────

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

    # Auto-create topics from curriculum
    topics = get_topics_for_subject(req.stream, req.name)
    for topic_name in topics:
        difficulty = get_difficulty(req.stream, req.name, topic_name)
        db.create_topic(
            subject_id = subject_id,
            user_id    = user_id,
            name       = topic_name,
            difficulty = difficulty
        )

    return {
        "message":    f"Subject {req.name} added",
        "subject_id": subject_id,
        "topics_created": len(topics)
    }


# ─────────────────────────────────────────────────────────────
# Quiz routes
# ─────────────────────────────────────────────────────────────

@app.get("/quiz/{topic_id}/questions")
def get_quiz_questions(topic_id: int, difficulty: int = None):
    """Returns 10 random questions for a topic."""
    questions = db.get_questions(
        topic_id   = topic_id,
        difficulty = difficulty,
        limit      = 10
    )
    if not questions:
        raise HTTPException(
            404,
            "No questions found for this topic. "
            "Add questions first."
        )
    # Hide correct answer from response
    for q in questions:
        q.pop("answer", None)
        q.pop("explanation", None)
    return {"questions": questions, "total": len(questions)}


@app.post("/quiz/submit/{user_id}")
def submit_quiz(user_id: int, req: QuizSubmitRequest):
    """
    Saves quiz attempt and runs forgetting LSTM
    to compute next review date.
    """
    get_current_user(user_id)

    # Save attempt to database
    db.save_quiz_attempt(
        user_id     = user_id,
        topic_id    = req.topic_id,
        score       = req.score,
        time_spent  = req.time_spent,
        self_rating = req.self_rating,
        difficulty  = req.difficulty
    )

    # Fetch topic info for inference
    topic = db.get_topic_by_id(req.topic_id)
    if not topic:
        raise HTTPException(404, "Topic not found")

    # Get last 10 attempts for this topic
    attempts_raw = db.get_quiz_attempts(user_id, req.topic_id, limit=10)

    # Convert to format inference expects
    attempts = []
    for a in attempts_raw:
        attempts.append({
            "score":       a["score"],
            "time_spent":  a["time_spent"],
            "self_rating": a["self_rating"],
            "timestamp":   datetime.fromisoformat(a["timestamp"])
        })

    # Run forgetting LSTM
    prediction = predict_next_review(
        attempts         = attempts,
        topic_difficulty = topic["difficulty"],
        last_score       = req.score
    )

    # Save review schedule
    db.upsert_review_schedule(
        user_id     = user_id,
        topic_id    = req.topic_id,
        next_review = prediction["next_review"],
        recall_prob = prediction["recall_prob"],
        days_until  = prediction["days_until"],
        urgency     = prediction["urgency"],
        message     = prediction["message"]
    )

    # Award XP
    xp_earned = _calculate_xp(req.score, req.difficulty)
    db.update_streak_xp(user_id, streak=0, xp=xp_earned)

    return {
        "message":    "Quiz submitted",
        "score":      req.score,
        "xp_earned":  xp_earned,
        "prediction": prediction
    }


@app.post("/quiz/questions/add")
def add_question(req: AddQuestionRequest):
    """Add a new question to the question bank."""
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


# ─────────────────────────────────────────────────────────────
# Study log routes
# ─────────────────────────────────────────────────────────────

@app.post("/study-log/{user_id}")
def log_study_session(user_id: int, req: StudyLogRequest):
    """
    Saves a manual study log and runs
    backlog LSTM for the subject.
    """
    get_current_user(user_id)

    # Save log
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

    # Get subject info
    subject = db.get_subject_by_id(req.subject_id)
    if not subject:
        raise HTTPException(404, "Subject not found")

    # Get last 14 study logs
    logs_raw = db.get_study_logs(user_id, req.subject_id, limit=14)

    # Convert for inference
    study_logs = []
    for log in logs_raw:
        study_logs.append({
            "date":           datetime.fromisoformat(log["date"]),
            "topics_covered": log["topics_covered"],
            "study_time":     log["study_time"],
            "quiz_score":     log["quiz_score"],
            "days_skipped":   log["days_skipped"]
        })

    # Calculate days to exam
    days_to_exam = 30  # default
    if subject.get("exam_date"):
        exam_dt      = datetime.strptime(subject["exam_date"], "%Y-%m-%d")
        days_to_exam = max(1, (exam_dt - datetime.now()).days)

    # Run backlog LSTM
    backlog = predict_backlog(
        study_logs     = study_logs,
        subject        = subject["name"],
        chapters_total = subject["chapters_total"],
        days_to_exam   = days_to_exam,
        exam_name      = subject.get("exam_name", "your exam")
    )

    # Save backlog alert
    db.upsert_backlog_alert(
        user_id        = user_id,
        subject_id     = req.subject_id,
        severity_10    = backlog["severity_10"],
        severity_label = backlog["severity_label"],
        alert_level    = backlog["alert_level"],
        message        = backlog["message"],
        catchup_plan   = json.dumps(backlog["catchup_plan"])
    )

    return {
        "message": "Study session logged",
        "backlog": backlog
    }


# ─────────────────────────────────────────────────────────────
# Dashboard route
# ─────────────────────────────────────────────────────────────

@app.get("/dashboard/{user_id}")
def get_dashboard(user_id: int):
    """
    Returns everything needed for the dashboard
    in a single API call.
    """
    get_current_user(user_id)

    # Summary stats
    summary        = db.get_dashboard_summary(user_id)

    # Today's review queue
    review_queue   = db.get_todays_review(user_id)

    # Backlog alerts
    backlog_alerts = db.get_backlog_alerts(user_id)

    # Parse catchup_plan JSON strings
    for alert in backlog_alerts:
        if alert.get("catchup_plan"):
            try:
                alert["catchup_plan"] = json.loads(
                    alert["catchup_plan"]
                )
            except Exception:
                pass

    return {
        "summary":        summary,
        "review_queue":   review_queue,
        "backlog_alerts": backlog_alerts,
        "generated_at":   datetime.now().isoformat()
    }


# ─────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────

def _seed_topics_for_user(user_id: int, stream: str):
    """
    Auto-creates subjects and topics from curriculum
    when a new user registers.
    """
    subjects = get_subjects_for_stream(stream)
    for subject_name in subjects:
        subject_id = db.create_subject(
            user_id        = user_id,
            name           = subject_name,
            stream         = stream,
            exam_name      = "Board Exam",
            exam_date      = (datetime.now() +
                              timedelta(days=90)).strftime("%Y-%m-%d"),
            chapters_total = len(
                get_topics_for_subject(stream, subject_name)
            )
        )
        topics = get_topics_for_subject(stream, subject_name)
        for topic_name in topics:
            difficulty = get_difficulty(stream, subject_name, topic_name)
            db.create_topic(
                subject_id = subject_id,
                user_id    = user_id,
                name       = topic_name,
                difficulty = difficulty
            )


def _calculate_xp(score: float, difficulty: int) -> int:
    """
    Awards XP based on score and question difficulty.
    Higher difficulty + higher score = more XP.
    """
    base_xp        = 10
    score_bonus    = int(score / 10)
    diff_bonus     = difficulty * 2
    return base_xp + score_bonus + diff_bonus


# ─────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status":  "running",
        "version": "1.0.0",
        "time":    datetime.now().isoformat()
    }


# ─────────────────────────────────────────────────────────────
# Serve React frontend
# ─────────────────────────────────────────────────────────────

frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(frontend_dist), html=True),
        name="static"
    )


# ─────────────────────────────────────────────────────────────
# Run directly
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
