# database.py
# SQLite database setup for LearnFlow — v2.0
# Handles all data storage and retrieval

import sqlite3
import hashlib
import secrets
import uuid
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
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────
# Password hashing (SHA-256 with salt — no external dependency)
# ─────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Returns a salted SHA-256 hash of the password."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain: str, stored: str) -> bool:
    """Verifies a plain password against a stored hash."""
    # Support legacy plaintext passwords (backward compat for existing test users)
    if ":" not in stored:
        return plain == stored
    salt, hashed = stored.split(":", 1)
    return hashlib.sha256(f"{salt}{plain}".encode()).hexdigest() == hashed


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
                last_study   DATE,
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

        # ── Quiz attempts (aggregate) ──────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                topic_id      INTEGER NOT NULL,
                score         REAL    NOT NULL,
                time_spent    REAL    DEFAULT 15,
                self_rating   INTEGER DEFAULT 3,
                difficulty    INTEGER DEFAULT 3,
                correct_count INTEGER DEFAULT 0,
                total_count   INTEGER DEFAULT 0,
                timestamp     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)  REFERENCES users(id),
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            )
        """)

        # ── Question-level attempts (per-question detail) ──
        db.execute("""
            CREATE TABLE IF NOT EXISTS question_attempts (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                quiz_attempt_id  INTEGER NOT NULL,
                topic_id         INTEGER NOT NULL,
                question_id      INTEGER NOT NULL,
                chosen_option    TEXT    NOT NULL,
                correct_option   TEXT    NOT NULL,
                is_correct       INTEGER NOT NULL DEFAULT 0,
                time_spent_sec   REAL    DEFAULT 0,
                timestamp        DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)         REFERENCES users(id),
                FOREIGN KEY (quiz_attempt_id) REFERENCES quiz_attempts(id),
                FOREIGN KEY (question_id)     REFERENCES questions(id)
            )
        """)

        # ── Topic mastery (persistent per-user per-topic) ──
        db.execute("""
            CREATE TABLE IF NOT EXISTS topic_mastery (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                topic_id       INTEGER NOT NULL,
                mastery_score  REAL    DEFAULT 0,
                last_quiz_score REAL   DEFAULT 0,
                attempts_count INTEGER DEFAULT 0,
                accuracy_rate  REAL    DEFAULT 0,
                last_reviewed  DATETIME,
                updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, topic_id),
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
                UNIQUE(user_id, topic_id),
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
                UNIQUE(user_id, subject_id),
                FOREIGN KEY (user_id)    REFERENCES users(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

        # ── Copilot conversations ──────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS copilot_conversations (
                id         TEXT    PRIMARY KEY,
                user_id    INTEGER NOT NULL,
                title      TEXT    DEFAULT 'New conversation',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ── Copilot messages ───────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS copilot_messages (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT    NOT NULL,
                role            TEXT    NOT NULL,
                content         TEXT    NOT NULL,
                created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES copilot_conversations(id)
            )
        """)

        # ── Study plans ────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS study_plans (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL,
                subject_id     INTEGER NOT NULL,
                exam_date      DATE    NOT NULL,
                exam_name      TEXT,
                days_to_exam   INTEGER,
                total_topics   INTEGER,
                topics_per_day INTEGER,
                plan_json      TEXT,
                created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)    REFERENCES users(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        """)

        # ── Learning events log ────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS learning_events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                topic_id   INTEGER,
                event_type TEXT    NOT NULL,
                score      REAL,
                time_spent REAL,
                meta_json  TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ── Add missing columns to existing tables (migrations) ──

        # ── RAG sources ────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS rag_sources (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path   TEXT    NOT NULL UNIQUE,
                checksum      TEXT    NOT NULL,
                stream        TEXT,
                subject       TEXT,
                class_level   TEXT,
                board         TEXT,
                chapter       TEXT,
                chunk_count   INTEGER DEFAULT 0,
                last_indexed  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        _migrate(db)

    print("All tables created/verified successfully")


def _migrate(db):
    """Safe column additions and indexes for existing databases."""
    migrations = [
        ("users",         "last_study",     "DATE"),
        ("quiz_attempts", "correct_count",  "INTEGER DEFAULT 0"),
        ("quiz_attempts", "total_count",    "INTEGER DEFAULT 0"),
    ]
    for table, col, col_type in migrations:
        try:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except Exception:
            pass  # column already exists

    indexes = [
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_backlog_alerts_user_subject ON backlog_alerts(user_id, subject_id)",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_review_schedule_user_topic ON review_schedule(user_id, topic_id)",
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_topic_mastery_user_topic ON topic_mastery(user_id, topic_id)",
    ]
    for idx_sql in indexes:
        try:
            db.execute(idx_sql)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────
# User queries
# ─────────────────────────────────────────────────────────────

def create_user(name: str, email: str,
                password: str, stream: str) -> int:
    hashed = _hash_password(password)
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO users (name, email, password, stream)
            VALUES (?, ?, ?, ?)
        """, (name, email, hashed, stream))
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


def update_streak_and_xp(user_id: int, xp_earned: int):
    """Updates XP and streak based on last study date."""
    with get_db() as db:
        user = db.execute(
            "SELECT streak, last_study FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return

        today      = datetime.now().date()
        last_study = None
        if user["last_study"]:
            try:
                last_study = datetime.strptime(str(user["last_study"]), "%Y-%m-%d").date()
            except Exception:
                pass

        if last_study is None:
            new_streak = 1
        elif (today - last_study).days == 1:
            new_streak = user["streak"] + 1   # consecutive day
        elif (today - last_study).days == 0:
            new_streak = user["streak"]        # already studied today
        else:
            new_streak = 1                     # streak broken

        db.execute("""
            UPDATE users SET streak = ?, xp = xp + ?, last_study = ?
            WHERE id = ?
        """, (new_streak, xp_earned, today.isoformat(), user_id))


# Legacy compat
def update_streak_xp(user_id: int, streak: int, xp: int):
    with get_db() as db:
        db.execute("""
            UPDATE users SET streak = streak + ?, xp = xp + ?
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
                      self_rating: int, difficulty: int,
                      correct_count: int = 0,
                      total_count: int = 0) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO quiz_attempts
            (user_id, topic_id, score, time_spent,
             self_rating, difficulty, correct_count, total_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, topic_id, score, time_spent,
              self_rating, difficulty, correct_count, total_count))
        return cursor.lastrowid


def save_question_attempt(user_id: int, quiz_attempt_id: int,
                          topic_id: int, question_id: int,
                          chosen_option: str, correct_option: str,
                          is_correct: bool, time_spent_sec: float = 0.0) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO question_attempts
            (user_id, quiz_attempt_id, topic_id, question_id,
             chosen_option, correct_option, is_correct, time_spent_sec)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, quiz_attempt_id, topic_id, question_id,
              chosen_option, correct_option, int(is_correct), time_spent_sec))
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


def get_recent_quiz_attempts(user_id: int, limit: int = 20) -> list:
    """Returns recent quiz attempts with topic name for the dashboard."""
    with get_db() as db:
        rows = db.execute("""
            SELECT qa.*, t.name as topic_name, s.name as subject_name
            FROM quiz_attempts qa
            JOIN topics   t ON qa.topic_id   = t.id
            JOIN subjects s ON t.subject_id  = s.id
            WHERE qa.user_id = ?
            ORDER BY qa.timestamp DESC LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]


def get_last_score(user_id: int, topic_id: int) -> float:
    with get_db() as db:
        row = db.execute("""
            SELECT score FROM quiz_attempts
            WHERE user_id = ? AND topic_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id, topic_id)).fetchone()
        return float(row["score"]) if row else 50.0


def get_weak_topics(user_id: int, limit: int = 5) -> list:
    """Returns topics with lowest mastery scores."""
    with get_db() as db:
        rows = db.execute("""
            SELECT tm.*, t.name as topic_name, s.name as subject_name, t.difficulty
            FROM topic_mastery tm
            JOIN topics   t ON tm.topic_id  = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE tm.user_id = ? AND tm.attempts_count > 0
            ORDER BY tm.mastery_score ASC LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]


def get_subject_performance(user_id: int) -> list:
    """Returns real per-subject average scores from quiz_attempts."""
    with get_db() as db:
        rows = db.execute("""
            SELECT s.name as subject, AVG(qa.score) as score, COUNT(qa.id) as attempts
            FROM quiz_attempts qa
            JOIN topics   t ON qa.topic_id  = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE qa.user_id = ?
            GROUP BY s.id, s.name
            ORDER BY score ASC
        """, (user_id,)).fetchall()
        return [{"subject": r["subject"],
                 "score":   round(r["score"] or 0, 1),
                 "attempts": r["attempts"]} for r in rows]


def get_question_mistakes(user_id: int, topic_id: int = None, limit: int = 20) -> list:
    """Returns questions the user got wrong, for Copilot context."""
    with get_db() as db:
        if topic_id:
            rows = db.execute("""
                SELECT qa.*, q.question, q.option_a, q.option_b, q.option_c,
                       q.option_d, q.answer, q.explanation, t.name as topic_name
                FROM question_attempts qa
                JOIN questions q ON qa.question_id = q.id
                JOIN topics    t ON qa.topic_id    = t.id
                WHERE qa.user_id = ? AND qa.topic_id = ? AND qa.is_correct = 0
                ORDER BY qa.timestamp DESC LIMIT ?
            """, (user_id, topic_id, limit)).fetchall()
        else:
            rows = db.execute("""
                SELECT qa.*, q.question, q.option_a, q.option_b, q.option_c,
                       q.option_d, q.answer, q.explanation, t.name as topic_name
                FROM question_attempts qa
                JOIN questions q ON qa.question_id = q.id
                JOIN topics    t ON qa.topic_id    = t.id
                WHERE qa.user_id = ? AND qa.is_correct = 0
                ORDER BY qa.timestamp DESC LIMIT ?
            """, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Topic mastery queries
# ─────────────────────────────────────────────────────────────

def upsert_topic_mastery(user_id: int, topic_id: int,
                         score: float, difficulty: float = 3.0):
    """
    Updates the persistent topic mastery score for a user+topic pair.
    Mastery = weighted average of recent scores, dampened by difficulty.
    """
    with get_db() as db:
        existing = db.execute("""
            SELECT mastery_score, attempts_count, accuracy_rate
            FROM topic_mastery
            WHERE user_id = ? AND topic_id = ?
        """, (user_id, topic_id)).fetchone()

        if existing:
            n       = existing["attempts_count"]
            old_mas = existing["mastery_score"]
            # Exponential moving average — recent scores weighted more
            alpha   = 0.3
            new_mas = alpha * score + (1 - alpha) * old_mas
            new_acc = (existing["accuracy_rate"] * n + (1 if score >= 60 else 0)) / (n + 1)
            db.execute("""
                UPDATE topic_mastery
                SET mastery_score = ?, last_quiz_score = ?, attempts_count = ?,
                    accuracy_rate = ?, last_reviewed = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND topic_id = ?
            """, (round(new_mas, 2), score, n + 1,
                  round(new_acc, 3), datetime.now().isoformat(),
                  user_id, topic_id))
        else:
            db.execute("""
                INSERT INTO topic_mastery
                (user_id, topic_id, mastery_score, last_quiz_score,
                 attempts_count, accuracy_rate, last_reviewed)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (user_id, topic_id, round(score, 2), score,
                  round(1.0 if score >= 60 else 0.0, 3),
                  datetime.now().isoformat()))


def get_all_topic_mastery(user_id: int) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT tm.*, t.name as topic_name, t.difficulty,
                   s.name as subject_name
            FROM topic_mastery tm
            JOIN topics   t ON tm.topic_id  = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE tm.user_id = ?
            ORDER BY tm.mastery_score ASC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


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
    """Insert or update review schedule — uses UNIQUE constraint for upsert."""
    with get_db() as db:
        db.execute("""
            INSERT INTO review_schedule
            (user_id, topic_id, next_review, recall_prob,
             days_until, urgency, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, topic_id) DO UPDATE SET
                next_review = excluded.next_review,
                recall_prob = excluded.recall_prob,
                days_until  = excluded.days_until,
                urgency     = excluded.urgency,
                message     = excluded.message,
                updated_at  = CURRENT_TIMESTAMP
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


def get_all_review_schedule(user_id: int) -> list:
    """Returns all review schedule entries for a user (for analytics)."""
    with get_db() as db:
        rows = db.execute("""
            SELECT rs.*, t.name as topic_name, s.name as subject_name
            FROM review_schedule rs
            JOIN topics   t ON rs.topic_id  = t.id
            JOIN subjects s ON t.subject_id = s.id
            WHERE rs.user_id = ?
            ORDER BY rs.recall_prob ASC
        """, (user_id,)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Backlog alert queries
# ─────────────────────────────────────────────────────────────

def upsert_backlog_alert(user_id: int, subject_id: int,
                         severity_10: float, severity_label: str,
                         alert_level: str, message: str,
                         catchup_plan: str):
    """Insert or update backlog alert — uses UNIQUE constraint for upsert."""
    with get_db() as db:
        db.execute("""
            INSERT INTO backlog_alerts
            (user_id, subject_id, severity_10, severity_label,
             alert_level, message, catchup_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, subject_id) DO UPDATE SET
                severity_10    = excluded.severity_10,
                severity_label = excluded.severity_label,
                alert_level    = excluded.alert_level,
                message        = excluded.message,
                catchup_plan   = excluded.catchup_plan,
                created_at     = CURRENT_TIMESTAMP
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
# Copilot conversation queries
# ─────────────────────────────────────────────────────────────

def create_conversation(user_id: int, title: str = "New conversation") -> str:
    conv_id = str(uuid.uuid4())
    with get_db() as db:
        db.execute("""
            INSERT INTO copilot_conversations (id, user_id, title)
            VALUES (?, ?, ?)
        """, (conv_id, user_id, title))
    return conv_id


def conversation_belongs_to_user(conversation_id: str, user_id: int) -> bool:
    with get_db() as db:
        row = db.execute("""
            SELECT id FROM copilot_conversations
            WHERE id = ? AND user_id = ?
        """, (conversation_id, user_id)).fetchone()
        return row is not None


def save_message(conversation_id: str, role: str, content: str) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO copilot_messages (conversation_id, role, content)
            VALUES (?, ?, ?)
        """, (conversation_id, role, content))
        # Update conversation updated_at
        db.execute("""
            UPDATE copilot_conversations SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (conversation_id,))
        return cursor.lastrowid


def get_conversation_messages(conversation_id: str, limit: int = 20) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM copilot_messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            LIMIT ?
        """, (conversation_id, limit)).fetchall()
        return [dict(r) for r in rows]


def get_user_conversations(user_id: int, limit: int = 20) -> list:
    with get_db() as db:
        rows = db.execute("""
            SELECT cc.*,
                   (SELECT content FROM copilot_messages
                    WHERE conversation_id = cc.id
                    ORDER BY created_at DESC LIMIT 1) as last_message
            FROM copilot_conversations cc
            WHERE cc.user_id = ?
            ORDER BY cc.updated_at DESC LIMIT ?
        """, (user_id, limit)).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Study plan queries
# ─────────────────────────────────────────────────────────────

def save_study_plan(user_id: int, subject_id: int, exam_date: str,
                    exam_name: str, days_to_exam: int, total_topics: int,
                    topics_per_day: int, plan_json: str) -> int:
    with get_db() as db:
        cursor = db.execute("""
            INSERT INTO study_plans
            (user_id, subject_id, exam_date, exam_name, days_to_exam,
             total_topics, topics_per_day, plan_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, subject_id, exam_date, exam_name, days_to_exam,
              total_topics, topics_per_day, plan_json))
        return cursor.lastrowid


def get_latest_study_plan(user_id: int, subject_id: int) -> dict | None:
    with get_db() as db:
        row = db.execute("""
            SELECT * FROM study_plans
            WHERE user_id = ? AND subject_id = ?
            ORDER BY id DESC LIMIT 1
        """, (user_id, subject_id)).fetchone()
        return dict(row) if row else None


# ─────────────────────────────────────────────────────────────
# Learning event log
# ─────────────────────────────────────────────────────────────

def log_learning_event(user_id: int, topic_id, event_type: str,
                       score: float = None, time_spent: float = None,
                       meta: dict = None):
    import json as _json
    with get_db() as db:
        db.execute("""
            INSERT INTO learning_events
            (user_id, topic_id, event_type, score, time_spent, meta_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, topic_id, event_type, score, time_spent,
              _json.dumps(meta) if meta else None))

# RAG source queries
# ─────────────────────────────────────────────────────────────

def get_rag_source(source_path: str) -> dict:
    with get_db() as db:
        row = db.execute("""
            SELECT * FROM rag_sources
            WHERE source_path = ?
        """, (source_path,)).fetchone()
        return dict(row) if row else None


def upsert_rag_source(source_path: str, checksum: str,
                      stream: str = None, subject: str = None,
                      class_level: str = None, board: str = None,
                      chapter: str = None, chunk_count: int = 0):
    with get_db() as db:
        db.execute("""
            INSERT INTO rag_sources
            (source_path, checksum, stream, subject, class_level,
             board, chapter, chunk_count, last_indexed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(source_path) DO UPDATE SET
                checksum = excluded.checksum,
                stream = excluded.stream,
                subject = excluded.subject,
                class_level = excluded.class_level,
                board = excluded.board,
                chapter = excluded.chapter,
                chunk_count = excluded.chunk_count,
                last_indexed = CURRENT_TIMESTAMP
        """, (source_path, checksum, stream, subject,
              class_level, board, chapter, chunk_count))


# ─────────────────────────────────────────────────────────────
# Dashboard summary query
# ─────────────────────────────────────────────────────────────

def get_dashboard_summary(user_id: int) -> dict:
    """Fetches everything needed for the dashboard summary."""
    with get_db() as db:
        user = dict(db.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone())

        review_count = db.execute("""
            SELECT COUNT(*) as cnt FROM review_schedule
            WHERE user_id = ? AND next_review <= DATE('now')
        """, (user_id,)).fetchone()["cnt"]

        critical_count = db.execute("""
            SELECT COUNT(*) as cnt FROM backlog_alerts
            WHERE user_id = ? AND alert_level = 'critical'
        """, (user_id,)).fetchone()["cnt"]

        quiz_today = db.execute("""
            SELECT COUNT(*) as cnt FROM quiz_attempts
            WHERE user_id = ?
              AND DATE(timestamp) = DATE('now')
        """, (user_id,)).fetchone()["cnt"]

        avg_score = db.execute("""
            SELECT AVG(score) as avg FROM quiz_attempts
            WHERE user_id = ?
        """, (user_id,)).fetchone()["avg"]

        total_attempts = db.execute("""
            SELECT COUNT(*) as cnt FROM quiz_attempts WHERE user_id = ?
        """, (user_id,)).fetchone()["cnt"]

    return {
        "user":               user,
        "review_count":       review_count,
        "critical_count":     critical_count,
        "quiz_today":         quiz_today,
        "avg_score":          round(avg_score or 0, 1),
        "total_quiz_attempts": total_attempts
    }


# ─────────────────────────────────────────────────────────────
# Initialise on import
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    create_tables()
    print(f"Database initialised at {DB_PATH}")
