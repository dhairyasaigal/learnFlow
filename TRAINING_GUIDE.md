# LearnFlow — Model Training Guide

This directory contains the ML training pipeline for LearnFlow's two LSTM models:
1. **Forgetting Model** — Predicts recall probability (binary: recall vs forget)
2. **Backlog Model** — Predicts study backlog severity (regression: 0–10)

---

## Quick Start (Training Machine)

### 1. Clone/copy the repository
```bash
git clone <repo_url>
cd learnFlow/learnFlow
```

### 2. Set up Python environment
```bash
python -m venv train_env
source train_env/bin/activate      # Linux/macOS
# OR
train_env\Scripts\activate         # Windows
```

### 3. Install training dependencies
```bash
pip install -r requirements_training.txt
```

### 4. Generate synthetic training data
```bash
python -m ml.data_generator
```
This creates:
- `data/synthetic/forgetting_X.npy` — 50,000 sequences × (10 timesteps × 5 features)
- `data/synthetic/forgetting_y.npy` — 50,000 binary labels (recall/forget)
- `data/synthetic/backlog_X.npy` — 40,000 sequences × (14 timesteps × 6 features)
- `data/synthetic/backlog_y.npy` — 40,000 severity scores (0–1)

### 5. Train both models
```bash
# Train forgetting model (binary classification)
python -m ml.train_forgetting_model

# Train backlog model (severity regression)
python -m ml.train_backlog_model
```

Both scripts support arguments:
```bash
python -m ml.train_forgetting_model --samples 80000 --epochs 30
python -m ml.train_backlog_model    --samples 60000 --epochs 30
```

### 6. Evaluate the models
```bash
python -m ml.evaluate_models
```

### 7. Copy trained models to deployment
After training, copy the `.h5` files to the deployment machine:
```
models/saved/forgetting_model.h5
models/saved/backlog_model.h5
```

---

## Model Architecture

### Forgetting Model (Binary Classification)
```
Input: (batch, 10, 5)  — 10 quiz attempts × [score, time, days_gap, difficulty, self_rating]
       ↓
LSTM(64, return_sequences=True) + Dropout(0.2)
       ↓
LSTM(32) + Dropout(0.2)
       ↓
Dense(16, relu)
       ↓
Dense(1, sigmoid)  → Recall probability 0–1
```
- Loss: Binary cross-entropy
- Target: 1=will recall, 0=will forget (threshold: recall_prob > 0.7)
- Expected test accuracy: ≥82%

### Backlog Model (Regression)
```
Input: (batch, 14, 6)  — 14 days × [topics_covered, study_time, quiz_score, days_skipped, chapters_left, days_remaining]
       ↓
LSTM(64, return_sequences=True) + Dropout(0.2)
       ↓
LSTM(32) + Dropout(0.2)
       ↓
Dense(16, relu)
       ↓
Dense(1, sigmoid)  → Severity 0–1 (multiply by 10 for 0–10 scale)
```
- Loss: Mean squared error
- Target: Severity 0–1 (derived from completion rate, pace, difficulty)
- Expected test MAE: ≤1.5 on 0–10 scale

---

## Data Format

### Forgetting sequences (50,000 × 10 × 5)
Each sample = 10 most recent quiz attempts for a topic:
| Feature | Description | Normalisation |
|---------|-------------|---------------|
| score | Quiz score 0-100 | / 100 |
| time_spent | Minutes spent | / 45 |
| days_gap | Days since last review | / 30 |
| difficulty | Topic difficulty 1-5 | / 5 |
| self_rating | Student self-rating 1-5 | / 5 |

### Backlog sequences (40,000 × 14 × 6)
Each sample = 14-day study log for a subject:
| Feature | Description | Normalisation |
|---------|-------------|---------------|
| topics_covered | Topics studied this day | / 6 |
| study_time | Minutes studied | / 360 |
| quiz_score | Quiz score 0-100 | / 100 |
| days_skipped | Consecutive skip streak | / 7 |
| chapters_left | Chapters remaining | / chapters_total |
| days_remaining | Days to exam | / 90 |

---

## Student Archetypes (Backlog data)
The backlog generator simulates 5 realistic Indian student study patterns:
1. **consistent_studier** (15%) — Studies daily, maintains good pace
2. **last_minute_crammer** (35%) — Procrastinates then studies intensely before exam
3. **chapter_skipper** (20%) — Skips difficult topics, rushes through easy ones
4. **coaching_dependent** (15%) — Studies only on coaching class days
5. **burnout_student** (15%) — Starts strong, gradually loses momentum

---

## Deployment
Once trained, the `.h5` files are loaded in:
- `ml/forgetting_inference.py` — loaded at `app.py` startup
- `ml/backlog_inference.py` — loaded at `app.py` startup

If model files are missing, the app falls back to rule-based predictions
(clearly labelled as `model_source: "rule_based_fallback"` in all API responses).

---

## Google Colab (Recommended Training Environment)

For free GPU access, use Google Colab:

```python
# In a Colab notebook:
!git clone <repo_url>
%cd learnFlow/learnFlow
!pip install -r requirements_training.txt

# Run training
!python -m ml.train_forgetting_model --samples 80000 --epochs 30
!python -m ml.train_backlog_model    --samples 60000 --epochs 30

# Download models
from google.colab import files
files.download('models/saved/forgetting_model.h5')
files.download('models/saved/backlog_model.h5')
```

Expected training time on Colab GPU:
- Forgetting model: ~5–10 minutes
- Backlog model: ~4–8 minutes
