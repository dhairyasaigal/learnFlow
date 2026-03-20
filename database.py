# database.py
# SQLite database setup for LearnFlow
# Handles all data storage and retrieval

import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "learnflow.db"


# ─────────────────────────────────────────────────────────────
# Connection manager
# ─────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    """
    Context manager for database connections.
    Automatically commits and closes connection.
    Usage:
        with get_db() as db:
            db.execute("SELECT ...")
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────
# Schema creation
# ─────────────────────────────────────────────────────────────

def create_tables():
    """Creates all tables if they don't exist."""
    with get_db() as db:

        # ── Users ──────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT    NOT NULL,
                email        TEXT    NOT NULL UNIQUE,
                password     TEXT    NOT NULL,
                stream       TEXT    NOT NULL,
                streak       INTEGER DEFAULT 0,
                xp           INTEGER DEFAULT 0,
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ── Subjects ───────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                name           TEXT    NOT NULL,
                stream         TEXT    NOT NULL,
                exam_name      TEXT,
                exam_date      DATE,
                chapters_total INTEGER DEFAULT 10,
                created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ── Topics ─────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id  INTEGER NOT NULL,
                user_id     INTEGER NOT NULL,
                name        TEXT    NOT NULL,
                difficulty  REAL    DEFAULT 3.0,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id),
                FOREIGN KEY (user_id)    REFERENCES users(id)
            )
        """)

        # ── Questions bank ─────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id    INTEGER NOT NULL,
                question    TEXT    NOT NULL,
                option_a    TEXT    NOT NULL,
                option_b    TEXT    NOT NULL,
                option_c    TEXT    NOT NULL,
                option_d    TEXT    NOT NULL,
                answer      TEXT    NOT NULL,
                explanation TEXT,
                difficulty  INTEGER DEFAULT 3,
                source      TEXT    DEFAULT 'hardcoded',
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)

        # ── Quiz attempts ──────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                topic_id    INTEGER NOT NULL,
                score       REAL    NOT NULL,
                time_spent  REAL    DEFAULT 15,
                self_rating INTEGER DEFAULT 3,
                difficulty  INTEGER DEFAULT 3,
                timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)  REFERENCES users(id),
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)

        # ── Study logs ─────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS study_logs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                subject_id      INTEGER NOT NULL,
                topics_covered  INTEGER DEFAULT 0,
                study_time      REAL    DEFAULT 0,
                quiz_score      REAL    DEFAULT 0,
                days_skipped    INTEGER DEFAULT 0,
                self_rating     INTEGER DEFAULT 3,
                notes           TEXT,
                date            DATE    DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id)    REFERENCES users(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

        # ── Review schedule ────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS review_schedule (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                topic_id     INTEGER NOT NULL,
                next_review  DATE    NOT NULL,
                recall_prob  REAL    DEFAULT 0.5,
                days_until   INTEGER DEFAULT 1,
                urgency      TEXT    DEFAULT 'soon',
                message      TEXT,
                updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)  REFERENCES users(id),
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)

        # ── Backlog alerts ─────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS backlog_alerts (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                subject_id     INTEGER NOT NULL,
                severity_10    REAL    NOT NULL,
                severity_label TEXT    NOT NULL,
                alert_level    TEXT    NOT NULL,
                message        TEXT,
                catchup_plan   TEXT,
                created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)    REFERENCES users(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

    print("All tables created successfully")


# ─────────────────────────────────────────────────────────────
# User queries
# ─────────────────────────────────────────────────────────────

def create_user(name: str, email: str,
                password: str, stream: str) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO users (name, email, password, stream)
            VALUES (?, ?, ?, ?)
        """, (name, email, password, stream))
        return cursor.lastrowid


def get_user_by_email(email: str) -> dict:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def update_streak_xp(user_id: int, streak: int, xp: int):
    with get_db() as db:
        db.execute("""
            UPDATE users SET streak = ?, xp = xp + ?
            WHERE id = ?
        """, (streak, xp, user_id))


# ─────────────────────────────────────────────────────────────
# Subject queries
# ─────────────────────────────────────────────────────────────

def create_subject(user_id: int, name: str, stream: str,
                   exam_name: str, exam_date: str,
                   chapters_total: int) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO subjects
            (user_id, name, stream, exam_name, exam_date, chapters_total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, stream, exam_name, exam_date, chapters_total))
        return cursor.lastrowid


def get_subjects(user_id: int) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM subjects WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


def get_subject_by_id(subject_id: int) -> dict:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM subjects WHERE id = ?", (subject_id,)
        ).fetchone()
        return dict(row) if row else None


# ─────────────────────────────────────────────────────────────
# Topic queries
# ─────────────────────────────────────────────────────────────

def create_topic(subject_id: int, user_id: int,
                 name: str, difficulty: float) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO topics (subject_id, user_id, name, difficulty)
            VALUES (?, ?, ?, ?)
        """, (subject_id, user_id, name, difficulty))
        return cursor.lastrowid


def get_topics(subject_id: int) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM topics WHERE subject_id = ?
            ORDER BY difficulty DESC
        """, (subject_id,)).fetchall()
        return [dict(r) for r in rows]


def get_topic_by_id(topic_id: int) -> dict:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM topics WHERE id = ?", (topic_id,)
        ).fetchone()
        return dict(row) if row else None


# ─────────────────────────────────────────────────────────────
# Question queries
# ─────────────────────────────────────────────────────────────

def add_question(topic_id: int, question: str,
                 option_a: str, option_b: str,
                 option_c: str, option_d: str,
                 answer: str, explanation: str,
                 difficulty: int, source: str = "hardcoded") -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO questions
            (topic_id, question, option_a, option_b,
             option_c, option_d, answer, explanation,
             difficulty, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic_id, question, option_a, option_b,
              option_c, option_d, answer, explanation,
              difficulty, source))
        return cursor.lastrowid


def get_questions(topic_id: int,
                  difficulty: int = None,
                  limit: int = 10) -> list:
    with get_db() as db:
        if difficulty:
            rows = db.execute("""
                SELECT * FROM questions
                WHERE topic_id = ? AND difficulty = ?
                ORDER BY RANDOM() LIMIT ?
            """, (topic_id, difficulty, limit)).fetchall()
        else:
            rows = db.execute("""
                SELECT * FROM questions
                WHERE topic_id = ?
                ORDER BY RANDOM() LIMIT ?
            """, (topic_id, limit)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Quiz attempt queries
# ─────────────────────────────────────────────────────────────

def save_quiz_attempt(user_id: int, topic_id: int,
                      score: float, time_spent: float,
                      self_rating: int, difficulty: int) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO quiz_attempts
            (user_id, topic_id, score, time_spent,
             self_rating, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, topic_id, score,
              time_spent, self_rating, difficulty))
        return cursor.lastrowid


def get_quiz_attempts(user_id: int,
                      topic_id: int,
                      limit: int = 10) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM quiz_attempts
            WHERE user_id = ? AND topic_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, topic_id, limit)).fetchall()
        return [dict(r) for r in rows]


def get_last_score(user_id: int, topic_id: int) -> float:
    with get_db() as db:
        row = db.execute("""
            SELECT score FROM quiz_attempts
            WHERE user_id = ? AND topic_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id, topic_id)).fetchone()
        return float(row["score"]) if row else 50.0


# ─────────────────────────────────────────────────────────────
# Study log queries
# ─────────────────────────────────────────────────────────────

def save_study_log(user_id: int, subject_id: int,
                   topics_covered: int, study_time: float,
                   quiz_score: float, days_skipped: int,
                   self_rating: int, notes: str = "") -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO study_logs
            (user_id, subject_id, topics_covered, study_time,
             quiz_score, days_skipped, self_rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, subject_id, topics_covered,
              study_time, quiz_score, days_skipped,
              self_rating, notes))
        return cursor.lastrowid


def get_study_logs(user_id: int,
                   subject_id: int,
                   limit: int = 14) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM study_logs
            WHERE user_id = ? AND subject_id = ?
            ORDER BY date DESC LIMIT ?
        """, (user_id, subject_id, limit)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Review schedule queries
# ─────────────────────────────────────────────────────────────

def upsert_review_schedule(user_id: int, topic_id: int,
                           next_review: str, recall_prob: float,
                           days_until: int, urgency: str,
                           message: str):
    """Insert or update review schedule for a topic."""
    with get_db() as db:
        existing = db.execute("""
            SELECT id FROM review_schedule
            WHERE user_id = ? AND topic_id = ?
        """, (user_id, topic_id)).fetchone()

        if existing:
            db.execute("""
                UPDATE review_schedule
                SET next_review = ?, recall_prob = ?,
                    days_until = ?, urgency = ?,
                    message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND topic_id = ?
            """, (next_review, recall_prob, days_until,
                  urgency, message, user_id, topic_id))
        else:
            db.execute("""
                INSERT INTO review_schedule
                (user_id, topic_id, next_review, recall_prob,
                 days_until, urgency, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, topic_id, next_review,
                  recall_prob, days_until, urgency, message))


def get_todays_review(user_id: int) -> list:
    """Returns all topics due for review today or overdue."""
    with get_db() as db:
        rows = db.execute("""
            SELECT rs.*, t.name as topic_name,
                   s.name as subject_name
            FROM review_schedule rs
            JOIN topics   t ON rs.topic_id  = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE rs.user_id    = ?
              AND rs.next_review <= DATE('now')
            ORDER BY rs.urgency ASC, rs.recall_prob ASC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Backlog alert queries
# ─────────────────────────────────────────────────────────────

def upsert_backlog_alert(user_id: int, subject_id: int,
                         severity_10: float, severity_label: str,
                         alert_level: str, message: str,
                         catchup_plan: str):
    """Insert or update backlog alert for a subject."""
    with get_db() as db:
        existing = db.execute("""
            SELECT id FROM backlog_alerts
            WHERE user_id = ? AND subject_id = ?
        """, (user_id, subject_id)).fetchone()

        if existing:
            db.execute("""
                UPDATE backlog_alerts
                SET severity_10 = ?, severity_label = ?,
                    alert_level = ?, message = ?,
                    catchup_plan = ?,
                    created_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND subject_id = ?
            """, (severity_10, severity_label, alert_level,
                  message, catchup_plan, user_id, subject_id))
        else:
            db.execute("""
                INSERT INTO backlog_alerts
                (user_id, subject_id, severity_10, severity_label,
                 alert_level, message, catchup_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, subject_id, severity_10,
                  severity_label, alert_level,
                  message, catchup_plan))


def get_backlog_alerts(user_id: int) -> list:
    """Returns all backlog alerts for a student sorted by severity."""
    with get_db() as db:
        rows = db.execute("""
            SELECT ba.*, s.name as subject_name,
                   s.exam_date, s.exam_name
            FROM backlog_alerts ba
            JOIN subjects s ON ba.subject_id = s.id
            WHERE ba.user_id = ?
            ORDER BY ba.severity_10 DESC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Dashboard summary query
# ─────────────────────────────────────────────────────────────

def get_dashboard_summary(user_id: int) -> dict:
    """
    Single query that fetches everything needed
    for the dashboard in one shot.
    """
    with get_db() as db:
        # User info
        user = dict(db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone())

        # Today's review count
        review_count = db.execute("""
            SELECT COUNT(*) as cnt FROM review_schedule
            WHERE user_id = ? AND next_review <= DATE('now')
        """, (user_id,)).fetchone()["cnt"]

        # Critical backlog count
        critical_count = db.execute("""
            SELECT COUNT(*) as cnt FROM backlog_alerts
            WHERE user_id = ? AND alert_level = 'critical'
        """, (user_id,)).fetchone()["cnt"]

        # Total quiz attempts today
        quiz_today = db.execute("""
            SELECT COUNT(*) as cnt FROM quiz_attempts
            WHERE user_id = ?
              AND DATE(timestamp) = DATE('now')
        """, (user_id,)).fetchone()["cnt"]

        # Average score across all attempts
        avg_score = db.execute("""
            SELECT AVG(score) as avg FROM quiz_attempts
            WHERE user_id = ?
        """, (user_id,)).fetchone()["avg"]

    return {
        "user":          user,
        "review_count":  review_count,
        "critical_count": critical_count,
        "quiz_today":    quiz_today,
        "avg_score":     round(avg_score or 0, 1)
    }


# ─────────────────────────────────────────────────────────────
# Initialise on import
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    create_tables()
    print(f"Database initialised at {DB_PATH}")