# LearnFlow AI Enterprise

An enterprise-grade, AI-powered study companion built for students. LearnFlow uses LSTM neural networks trained on student behavior patterns combined with Advanced Large Language Models (LLMs) to personalize the study experience. It helps students remember what they've learned, avoid silent backlogs, study the right topics at the right time, and clarify doubts instantly using an AI Study Copilot.

---

## 🚀 The Problem It Solves

Every student faces three core problems:
1. **Forgetting** — You understand a topic today but forget it before the exam.
2. **Silent backlogs** — Topics pile up unnoticed until it's too late.
3. **Wrong priorities** — Spending time on easy topics while hard ones are ignored.

LearnFlow addresses all three with predictive AI (LSTMs) and provides real-time conceptual help using Generative AI (LLMs).

---

## ✨ Features

### 🤖 AI Study Copilot (New!)
- Instant doubt-resolution and tutoring via a conversational interface.
- Context-aware: the LLM knows your upcoming schedule, past quiz performance, and active backlogs to give highly personalized advice.
- Dynamically generates variant quiz questions for endless practice.

### 📊 Advanced Analytics & Dashboard (New!)
- **Retention Curves**: Simulates Ebbinghaus forgetting curves based on your recent topics.
- **Subject Heatmaps**: Visualizes your performance across different subjects.
- **Exam Prediction**: Estimates your final score and rank based on completion progress and average quiz performance.

### 🧠 Forgetting Curve (Review Scheduler)
- After each quiz, the LSTM model predicts when you'll forget the topic.
- Schedules a review on the optimal day — not too early, not too late.
- Dashboard review queue sorted by urgency/recall probability.

### 📉 Backlog Predictor
- Predicts backlog severity (0–10 scale) using 14-day study logs.
- Safe / Warning / Critical severity alerts.
- Provides actionable catch-up plans (chapters/day recommendations).

### 📅 AI Study Plan
- Input exam dates and the AI generates a day-by-day study schedule.
- Prioritizes hardest topics first to ensure maximum revision time.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI |
| **Frontend** | React 19, Vite, Tailwind CSS / Vanilla CSS |
| **Database** | SQLite (`learnflow.db`) |
| **Predictive ML** | TensorFlow, Scikit-learn, Pandas (LSTMs) |
| **Generative AI** | OpenRouter (Mistral / Llama), `openai` SDK |
| **Authentication** | Custom JWT/Session based |

---

## 📂 Project Structure

```
learnFlow/
├── .env                    # Environment variables (Add your OPENROUTER_API_KEY here)
├── app.py                  # FastAPI backend — all API routes & server setup
├── database.py             # SQLite schema and query logic
├── llm.py                  # Generative AI integration (Copilot, dynamic quiz generation)
├── requirements.txt        # Python dependencies
├── seed_questions.py       # Initial offline question bank seeder
├── learnflow.db            # SQLite database (auto-created on startup)
│
├── ml/
│   ├── indian_curriculum.py    # Standardized curriculum topics & difficulty maps
│   ├── forgetting_inference.py # Forgetting curve LSTM inference logic
│   └── backlog_inference.py    # Backlog severity LSTM inference logic
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx             # React Router & Auth Provider
│       ├── components/
│       │   └── CopilotWidget.jsx # AI Chat interface overlay
│       └── pages/
│           ├── Analytics.jsx   # Advanced reporting & curve simulation
│           ├── Dashboard.jsx   # Main view with queue and alerts
│           ├── Quiz.jsx        # Quiz rendering & dynamic question loading
│           └── ...
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| **POST** | `/auth/register` | Register new user |
| **POST** | `/auth/login` | Login user |
| **GET** | `/dashboard/{user_id}` | Fetch summary, review queue, backlog alerts |
| **GET** | `/analytics/{user_id}` | Advanced ML metrics (retention, heatmap, predictions) |
| **POST** | `/copilot/chat/{user_id}`| Stream chat with AI Copilot (Context-aware) |
| **GET** | `/quiz/{topic_id}/questions` | Get quiz questions (Falls back to LLM to generate more) |
| **POST** | `/quiz/submit/{user_id}` | Submit quiz, trigger LSTM, schedule next review |
| **POST** | `/study-plan/{user_id}` | Generate AI-driven exam schedule |
| **POST** | `/study-log/{user_id}` | Log study time, trigger Backlog predictor |

---

## ⚙️ Running Locally

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **OpenRouter API Key** (for advanced Copilot features)

### 1. Environment Setup

Create a `.env` file in the root `learnFlow` directory:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 2. Backend Setup

Open a terminal in the root directory:

```bash
# Optional: Create a virtual environment
python -m venv .venv
# Activate it (Windows)
.venv\\Scripts\\activate
# Activate it (Mac/Linux)
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed initial static questions
python seed_questions.py

# Start the API server
python app.py
```
> The API will run on `http://localhost:8000`. The DB (`learnflow.db`) is auto-created.

### 3. Frontend Setup

Open a new terminal in the `frontend/` directory:

```bash
cd frontend
npm install
npm run dev
```
> The React app will run on `http://localhost:5173`.

---

## 🧪 Testing the LLM Features
The project features an intelligent Copilot. When a user asks a question, the backend automatically attaches context like:
- Student's Name and Stream
- Current Backlog Risk
- Topics urgently needing review
The LLM will utilize this data to advise the user appropriately.

## 💾 Database Schema Overview
- **`users`**: Auth, XP, Streaks.
- **`subjects` & `topics`**: User curriculum structure.
- **`questions`**: Offline and AI-generated question cache.
- **`quiz_attempts`**: Real-time attempt metrics (score, time spent).
- **`study_logs`**: Daily aggregation.
- **`review_schedule` & `backlog_alerts`**: Directly updated by backend LSTM inferences.
