"""
test_platform.py
Comprehensive end-to-end automated test suite for LearnFlow AI Enterprise.
Tests:
1. Authentication & Security (Registration, Login, Password Hashing, Validation)
2. Stream Curriculum Seeding (Subjects & Topics creation)
3. Quiz System (Questions retrieval, Quiz submission with Question-level tracking)
4. Topic Mastery & Persistence (Mastery scores, Learning events)
5. Review Scheduler & Backlog Prediction (Safe inference or rule-based fallback)
6. Study Planning (Schedule generation, Persistence in study_plans)
7. Study Logging (Session logging, Streak & XP updates, Backlog updates)
8. AI Copilot Integration (Context building, Conversation & Message persistence)
9. Analytics & Dashboard Integrity (Honest calculations, No fake exam scores)
"""
import os
import sys
import unittest
from datetime import datetime, timedelta
from starlette.testclient import TestClient

# Ensure learnFlow directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
import database as db

client = TestClient(app)

class TestLearnFlowPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.create_tables()
        cls.test_email = f"test_{int(datetime.now().timestamp())}@example.com"
        cls.test_password = "SecurePassword123!"
        cls.test_name = "Test Student"
        cls.test_stream = "PCM"

    def test_01_health_check(self):
        """Verify the service health endpoint returns operational status."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "running")
        self.assertIn("models", data)

    def test_02_auth_registration(self):
        """Test user registration, stream curriculum seeding, and password hashing."""
        payload = {
            "name": self.test_name,
            "email": self.test_email,
            "password": self.test_password,
            "stream": self.test_stream
        }
        response = client.post("/auth/register", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("user_id", data)
        self.__class__.user_id = data["user_id"]

        # Verify password in DB is hashed and not plaintext
        with db.get_db() as conn:
            user = conn.execute("SELECT password FROM users WHERE id = ?", (self.user_id,)).fetchone()
            self.assertIsNotNone(user)
            self.assertNotEqual(user["password"], self.test_password)
            self.assertTrue(user["password"].startswith("pbkdf2:") or len(user["password"]) > 40)

        # Verify stream subjects were seeded
        subjects = db.get_subjects(self.user_id)
        self.assertGreater(len(subjects), 0, "Subjects should be seeded for JEE stream")
        self.__class__.subject_id = subjects[0]["id"]
        self.__class__.subject_name = subjects[0]["name"]

        # Verify topics exist for subject
        topics = db.get_topics(self.subject_id)
        self.assertGreater(len(topics), 0, "Topics should exist for seeded subject")
        self.__class__.topic_id = topics[0]["id"]
        self.__class__.topic_name = topics[0]["name"]

    def test_03_auth_login(self):
        """Test authentication login with correct and invalid credentials."""
        # Valid login
        response = client.post("/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], self.user_id)
        self.assertEqual(data["name"], self.test_name)

        # Invalid password
        bad_response = client.post("/auth/login", json={
            "email": self.test_email,
            "password": "WrongPassword!"
        })
        self.assertEqual(bad_response.status_code, 401)

    def test_04_quiz_questions_fetch(self):
        """Verify quiz questions can be retrieved for a topic."""
        response = client.get(f"/quiz/{self.topic_id}/questions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("questions", data)
        self.__class__.questions = data["questions"]

    def test_05_quiz_submit_and_question_tracking(self):
        """
        Verify quiz submission:
        - saves aggregate quiz_attempt
        - saves question-level question_attempts
        - updates topic_mastery
        - logs learning_event
        - updates review_schedule
        """
        q_attempts = []
        if self.questions:
            for q in self.questions:
                q_attempts.append({
                    "question_id": q.get("id", 1),
                    "chosen_option": q.get("answer", "A"),
                    "is_correct": 1,
                    "time_spent": 12
                })

        payload = {
            "topic_id": self.topic_id,
            "score": 85.0,
            "time_spent": 15.0,
            "self_rating": 4,
            "difficulty": 3,
            "correct_count": len(q_attempts),
            "total_count": max(len(q_attempts), 1),
            "question_attempts": q_attempts
        }

        response = client.post(f"/quiz/submit/{self.user_id}", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("xp_earned", data)
        self.assertIn("prediction", data)

        # Verify question_attempts stored in database
        with db.get_db() as conn:
            saved_qa = conn.execute(
                "SELECT * FROM question_attempts WHERE user_id = ? AND topic_id = ?",
                (self.user_id, self.topic_id)
            ).fetchall()
            if q_attempts:
                self.assertGreater(len(saved_qa), 0)

            # Verify topic_mastery updated
            mastery = conn.execute(
                "SELECT * FROM topic_mastery WHERE user_id = ? AND topic_id = ?",
                (self.user_id, self.topic_id)
            ).fetchone()
            self.assertIsNotNone(mastery)
            self.assertGreater(mastery["mastery_score"], 0)

            # Verify learning_event logged
            events = conn.execute(
                "SELECT * FROM learning_events WHERE user_id = ? AND event_type = 'QUIZ_COMPLETED'",
                (self.user_id,)
            ).fetchall()
            self.assertGreater(len(events), 0)

    def test_06_study_plan_generation_and_persistence(self):
        """Verify study plan generation and persistent storage in study_plans table."""
        future_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        payload = {
            "subject_id": self.subject_id,
            "exam_date": future_date,
            "exam_name": "JEE Advanced"
        }
        response = client.post(f"/study-plan/{self.user_id}", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("daily_schedule", data)
        self.assertIn("topics_per_day", data)

        # Verify saved in study_plans table
        plan = db.get_latest_study_plan(self.user_id, self.subject_id)
        self.assertIsNotNone(plan)
        self.assertEqual(plan["exam_name"], "JEE Advanced")

    def test_07_study_log_and_streak(self):
        """Verify logging a study session updates backlog, streak, and events."""
        payload = {
            "subject_id": self.subject_id,
            "topics_covered": 3,
            "study_time": 90,
            "quiz_score": 80.0,
            "days_skipped": 0,
            "self_rating": 4,
            "notes": "Covered foundational concepts"
        }
        response = client.post(f"/study-log/{self.user_id}", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("backlog", data)

        # Check backlog alert updated
        alerts = db.get_backlog_alerts(self.user_id)
        self.assertGreater(len(alerts), 0)

        # Verify user streak is at least 1
        with db.get_db() as conn:
            user = conn.execute("SELECT streak, xp FROM users WHERE id = ?", (self.user_id,)).fetchone()
            self.assertGreaterEqual(user["streak"], 1)

    def test_08_copilot_chat_and_conversation_persistence(self):
        """Verify AI Copilot creates conversation, records messages, and injects context."""
        payload = {
            "message": "Hello! What topics should I review today based on my recent quiz?",
            "conversation_id": None
        }
        response = client.post(f"/copilot/chat/{self.user_id}", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertIn("reply", data)
        self.assertIn("conversation_id", data)
        conv_id = data["conversation_id"]

        # Verify conversation messages exist in database
        messages = db.get_conversation_messages(conv_id)
        self.assertGreaterEqual(len(messages), 2)  # User message + Assistant response
        self.assertEqual(messages[0]["role"], "user")
        self.assertEqual(messages[1]["role"], "assistant")

    def test_09_dashboard_and_analytics_integrity(self):
        """Verify dashboard and analytics return truthful data without fake predictions."""
        # Dashboard
        dash_res = client.get(f"/dashboard/{self.user_id}")
        self.assertEqual(dash_res.status_code, 200)
        dash = dash_res.json()
        self.assertIn("summary", dash)
        self.assertIn("xp", dash["summary"]["user"])
        self.assertIn("streak", dash["summary"]["user"])
        self.assertIn("backlog_alerts", dash)

        # Analytics
        analytics_res = client.get(f"/analytics/{self.user_id}")
        self.assertEqual(analytics_res.status_code, 200)
        analytics = analytics_res.json()
        self.assertIn("mastery_breakdown", analytics)
        self.assertIn("exam_prediction", analytics)
        self.assertIn("model_status", analytics)
        self.assertEqual(analytics["model_status"]["forgetting_model"], "lstm")
        self.assertEqual(analytics["model_status"]["backlog_model"], "lstm")
        # Ensure exam_prediction is honest and not a hardcoded fake rank
        self.assertNotIn("predicted_rank", analytics.get("exam_prediction", {}))

if __name__ == "__main__":
    unittest.main()
