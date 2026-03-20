# ml/backlog_inference.py
import numpy as np
import tensorflow as tf
from pathlib import Path
from datetime import datetime

BASE_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "saved" / "backlog_model.h5"

# ── Load model once at startup ─────────────────────────────
_model = None

def get_model():
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(str(MODEL_PATH))
    return _model


# ── Feature builder ────────────────────────────────────────
def build_sequence(study_logs: list, chapters_total: int,
                   days_to_exam: int) -> np.ndarray:
    """
    Converts last 14 days of study logs into LSTM input.

    study_logs: list of dicts with keys:
        date              : datetime
        topics_covered    : int
        study_time        : float minutes
        quiz_score        : float 0-100
        days_skipped      : int

    chapters_total : int total chapters in subject
    days_to_exam   : int days remaining until exam

    Returns: np.ndarray shape (1, 14, 6)
    """
    SEQ_LEN = 14
    sequence = []

    # Sort logs oldest first
    sorted_logs = sorted(study_logs, key=lambda x: x["date"])

    # Pad with zeros if fewer than 14 days of logs
    if len(sorted_logs) < SEQ_LEN:
        pad_len = SEQ_LEN - len(sorted_logs)
        for i in range(pad_len):
            sequence.append([0.0, 0.0, 0.5, 0.0, 1.0,
                             min(days_to_exam + pad_len - i, 90) / 90])

    chapters_left = chapters_total

    for i, log in enumerate(sorted_logs[-SEQ_LEN:]):
        covered       = int(log.get("topics_covered", 0))
        time          = float(log.get("study_time",   0))
        score         = float(log.get("quiz_score",   50))
        skipped       = int(log.get("days_skipped",   0))
        chapters_left = max(0, chapters_left - covered)
        days_rem      = max(1, days_to_exam - (len(sorted_logs) - i))

        sequence.append([
            min(covered, 6) / 6,
            min(time, 360) / 360,
            np.clip(score, 0, 100) / 100,
            min(skipped, 7) / 7,
            chapters_left / max(1, chapters_total),
            min(days_rem, 90) / 90
        ])

    arr = np.array(sequence[-SEQ_LEN:], dtype=np.float32)
    return np.expand_dims(arr, axis=0)  # shape (1, 14, 6)


# ── Main inference function ────────────────────────────────
def predict_backlog(
    study_logs:     list,
    subject:        str,
    chapters_total: int,
    days_to_exam:   int,
    exam_name:      str = "your exam"
) -> dict:
    """
    Predicts backlog severity for one subject.

    Returns dict with:
        severity_raw   : float 0-1
        severity_10    : float 0-10
        severity_label : str
        alert_level    : str  "critical" / "warning" / "safe"
        message        : str
        catchup_plan   : dict
    """
    model    = get_model()
    sequence = build_sequence(study_logs, chapters_total, days_to_exam)

    severity_raw   = float(model.predict(sequence, verbose=0)[0][0])
    severity_raw   = np.clip(severity_raw, 0.0, 1.0)
    severity_10    = round(severity_raw * 10, 1)

    # Classify severity
    if severity_10 >= 7.5:
        severity_label = "Critical"
        alert_level    = "critical"
    elif severity_10 >= 5.0:
        severity_label = "High"
        alert_level    = "warning"
    elif severity_10 >= 3.0:
        severity_label = "Moderate"
        alert_level    = "warning"
    elif severity_10 >= 1.5:
        severity_label = "Low"
        alert_level    = "safe"
    else:
        severity_label = "On Track"
        alert_level    = "safe"

    # Generate message
    message = _generate_message(
        severity_10, subject, days_to_exam, exam_name
    )

    # Generate catch-up plan
    catchup = _generate_catchup_plan(
        study_logs, chapters_total, days_to_exam, severity_10
    )

    return {
        "subject":        subject,
        "severity_raw":   severity_raw,
        "severity_10":    severity_10,
        "severity_label": severity_label,
        "alert_level":    alert_level,
        "message":        message,
        "catchup_plan":   catchup
    }


def _generate_message(severity: float, subject: str,
                      days_to_exam: int, exam_name: str) -> str:
    if severity >= 7.5:
        return (f"{subject} is at critical backlog risk. "
                f"Only {days_to_exam} days until {exam_name}. "
                f"Immediate action required.")
    elif severity >= 5.0:
        return (f"{subject} backlog is building up. "
                f"You need to increase your study pace now.")
    elif severity >= 3.0:
        return (f"{subject} is slightly behind. "
                f"A small push this week will keep you on track.")
    else:
        return f"{subject} is looking good — keep the current pace."


def _generate_catchup_plan(study_logs: list, chapters_total: int,
                           days_to_exam: int, severity: float) -> dict:
    """
    Generates a simple catch-up plan based on
    chapters remaining and days to exam.
    """
    # Estimate chapters covered from logs
    covered    = sum(int(log.get("topics_covered", 0)) for log in study_logs)
    remaining  = max(0, chapters_total - covered)

    if days_to_exam <= 0 or remaining <= 0:
        return {
            "chapters_remaining": remaining,
            "days_to_exam":       days_to_exam,
            "chapters_per_day":   0,
            "advice":             "Focus on revision now"
        }

    # How many chapters per day needed
    chapters_per_day = round(remaining / days_to_exam, 1)

    if severity >= 7.5:
        advice = (f"Study {chapters_per_day} chapters per day minimum. "
                  f"Consider skipping non-essential topics.")
    elif severity >= 5.0:
        advice = (f"Cover {chapters_per_day} chapters daily. "
                  f"Focus on high-weightage topics first.")
    elif severity >= 3.0:
        advice = (f"{chapters_per_day} chapters per day will clear your backlog "
                  f"in time. Stay consistent.")
    else:
        advice = f"You are on track. Maintain {chapters_per_day} chapters per day."

    return {
        "chapters_remaining": remaining,
        "days_to_exam":       days_to_exam,
        "chapters_per_day":   chapters_per_day,
        "advice":             advice
    }


# ── Batch inference — all subjects at once ─────────────────
def predict_all_subjects(subjects_data: list) -> list:
    """
    Runs backlog inference on all subjects for a student.
    Used when dashboard loads.

    subjects_data: list of dicts with keys:
        subject, study_logs, chapters_total,
        days_to_exam, exam_name

    Returns list sorted by severity — most critical first
    """
    results = []

    for data in subjects_data:
        result = predict_backlog(
            study_logs     = data.get("study_logs", []),
            subject        = data.get("subject", "Unknown"),
            chapters_total = data.get("chapters_total", 10),
            days_to_exam   = data.get("days_to_exam", 30),
            exam_name      = data.get("exam_name", "your exam")
        )
        results.append(result)

    # Sort critical first
    alert_order = {"critical": 0, "warning": 1, "safe": 2}
    results.sort(key=lambda x: (
        alert_order.get(x["alert_level"], 3),
        -x["severity_10"]
    ))

    return results