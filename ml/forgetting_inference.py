# ml/forgetting_inference.py
import numpy as np
import tensorflow as tf
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR   = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "saved" / "forgetting_model.h5"

# ── Load model once at startup ─────────────────────────────
_model = None

def get_model():
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(str(MODEL_PATH))
    return _model


# ── Feature builder ────────────────────────────────────────
def build_sequence(attempts: list, topic_difficulty: float) -> np.ndarray:
    """
    Converts last 10 quiz attempts into LSTM input sequence.

    attempts: list of dicts with keys:
        score       : float 0-100
        time_spent  : float minutes
        timestamp   : datetime
        self_rating : int 1-5

    topic_difficulty: float 1-5 from indian_curriculum.py

    Returns: np.ndarray shape (1, 10, 5)
    """
    SEQ_LEN = 10
    sequence = []

    # Pad with zeros if fewer than 10 attempts
    if len(attempts) < SEQ_LEN:
        pad_len = SEQ_LEN - len(attempts)
        for _ in range(pad_len):
            sequence.append([0.5, 0.3, 0.1, topic_difficulty / 5, 0.5])

    # Sort attempts oldest first
    sorted_attempts = sorted(attempts, key=lambda x: x["timestamp"])

    for i, attempt in enumerate(sorted_attempts[-SEQ_LEN:]):
        # Calculate days gap from previous attempt
        if i == 0:
            days_gap = 1
        else:
            prev_ts  = sorted_attempts[max(0, i-1)]["timestamp"]
            curr_ts  = attempt["timestamp"]
            days_gap = max(1, (curr_ts - prev_ts).days)

        score       = float(attempt.get("score", 50))
        time_spent  = float(attempt.get("time_spent", 15))
        self_rating = int(attempt.get("self_rating", 3))

        sequence.append([
            np.clip(score, 0, 100) / 100,
            np.clip(time_spent, 0, 45) / 45,
            np.clip(days_gap, 1, 30) / 30,
            np.clip(topic_difficulty, 1, 5) / 5,
            np.clip(self_rating, 1, 5) / 5
        ])

    arr = np.array(sequence[-SEQ_LEN:], dtype=np.float32)
    return np.expand_dims(arr, axis=0)  # shape (1, 10, 5)


# ── Main inference function ────────────────────────────────
def predict_next_review(
    attempts:          list,
    topic_difficulty:  float,
    last_score:        float
) -> dict:
    """
    Predicts when student should next review a topic.

    Returns dict with:
        recall_prob   : float 0-1
        next_review   : datetime
        days_until    : int
        urgency       : str  "today" / "soon" / "later"
        message       : str  human readable message
    """
    model    = get_model()
    sequence = build_sequence(attempts, topic_difficulty)

    # Raw prediction — probability of recall
    recall_prob = float(model.predict(sequence, verbose=0)[0][0])
    recall_prob = np.clip(recall_prob, 0.0, 1.0)

    # Convert recall probability to review interval
    # High recall → review later
    # Low recall  → review sooner
    days_until = _recall_prob_to_days(recall_prob, last_score, topic_difficulty)
    next_review = datetime.now() + timedelta(days=days_until)

    # Urgency level
    if days_until <= 1:
        urgency = "today"
        message = f"Review this topic today — your recall is dropping fast"
    elif days_until <= 3:
        urgency = "soon"
        message = f"Review in {days_until} days to stay on track"
    else:
        urgency = "later"
        message = f"You are on track — next review in {days_until} days"

    return {
        "recall_prob": round(recall_prob, 3),
        "next_review": next_review.strftime("%Y-%m-%d"),
        "days_until":  days_until,
        "urgency":     urgency,
        "message":     message
    }


def _recall_prob_to_days(
    recall_prob:      float,
    last_score:       float,
    topic_difficulty: float
) -> int:
    """
    Converts recall probability to recommended review interval in days.
    Harder topics get shorter intervals even at the same recall probability.
    """
    # Base interval from recall probability
    if recall_prob >= 0.85:
        base_days = 14
    elif recall_prob >= 0.75:
        base_days = 10
    elif recall_prob >= 0.65:
        base_days = 7
    elif recall_prob >= 0.55:
        base_days = 5
    elif recall_prob >= 0.45:
        base_days = 3
    elif recall_prob >= 0.35:
        base_days = 2
    else:
        base_days = 1

    # Difficulty penalty — hard topics reviewed sooner
    diff_penalty = (topic_difficulty - 1) / 4  # 0 to 1
    adjusted     = base_days * (1 - diff_penalty * 0.4)

    # Score boost — high recent score → slight extension
    if last_score >= 85:
        adjusted *= 1.2
    elif last_score < 50:
        adjusted *= 0.7

    return max(1, round(adjusted))


# ── Batch inference — for dashboard load ──────────────────
def predict_all_topics(topic_history: dict) -> list:
    """
    Runs inference on all topics for a student at once.
    Used when the dashboard loads.

    topic_history: dict of {topic_id: {attempts, difficulty, last_score}}

    Returns list of topics sorted by urgency (most urgent first)
    """
    results = []

    for topic_id, data in topic_history.items():
        attempts    = data.get("attempts", [])
        difficulty  = data.get("difficulty", 3.0)
        last_score  = data.get("last_score", 50.0)

        if not attempts:
            # Never studied — mark as urgent
            results.append({
                "topic_id":   topic_id,
                "recall_prob": 0.0,
                "next_review": datetime.now().strftime("%Y-%m-%d"),
                "days_until":  0,
                "urgency":     "today",
                "message":     "You have never studied this topic"
            })
            continue

        prediction = predict_next_review(attempts, difficulty, last_score)
        results.append({"topic_id": topic_id, **prediction})

    # Sort by urgency — today first, later last
    urgency_order = {"today": 0, "soon": 1, "later": 2}
    results.sort(key=lambda x: (
        urgency_order.get(x["urgency"], 3),
        x["days_until"]
    ))

    return results