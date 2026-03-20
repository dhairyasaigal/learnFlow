# ml/data_generator.py
# Generates synthetic training data for both LSTM models
# Model A — Forgetting curve LSTM
# Model B — Backlog predictor LSTM
# Uses Indian student behaviour patterns + Ebbinghaus forgetting curve

import numpy as np
import pandas as pd
import os
from pathlib import Path
from ml.indian_curriculum import (
    get_difficulty,
    get_subjects_for_stream,
    get_topics_for_subject,
    get_all_streams
)

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
SYNTH_DIR  = BASE_DIR / "data" / "synthetic"
PROC_DIR   = BASE_DIR / "data" / "processed"

SYNTH_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# MODEL A — Forgetting curve data generator
# Based on Ebbinghaus forgetting curve: R = e^(-t/S)
# R = recall probability
# t = time elapsed since last review (days)
# S = memory stability (personalised per student)
# ─────────────────────────────────────────────────────────────

def generate_forgetting_sequences(
    n_sequences: int = 50000,
    seq_len:     int = 10,
    save:        bool = True
) -> tuple:
    """
    Generates synthetic sequences of student review sessions.

    Each sequence = one student reviewing one topic over time.
    Features per step (5):
        1. normalised quiz score
        2. normalised time spent
        3. normalised days gap since last review
        4. normalised topic difficulty
        5. normalised self rating

    Target (1):
        1 = student will recall topic at next review
        0 = student will forget topic at next review
    """
    print(f"Generating {n_sequences} forgetting sequences...")

    X, y = [], []

    # Indian student retention profiles
    # stability = how many days before recall drops to 37%
    STUDENT_PROFILES = {
        "strong_retainer":   {"stability_range": (15, 30), "weight": 0.15},
        "average_retainer":  {"stability_range": (7,  15), "weight": 0.50},
        "weak_retainer":     {"stability_range": (2,   7), "weight": 0.25},
        "rote_learner":      {"stability_range": (1,   4), "weight": 0.10},
    }

    profile_names = list(STUDENT_PROFILES.keys())
    profile_weights = [
        STUDENT_PROFILES[p]["weight"] for p in profile_names
    ]

    # Typical review gaps Indian students take (days)
    REVIEW_GAPS = [1, 1, 2, 3, 3, 5, 7, 7, 10, 14, 21, 30]

    for _ in range(n_sequences):
        # Pick student profile
        profile_name = np.random.choice(profile_names, p=profile_weights)
        profile      = STUDENT_PROFILES[profile_name]

        # Initialise student parameters
        stability    = np.random.uniform(*profile["stability_range"])
        difficulty   = np.random.uniform(1.0, 5.0)
        recall_prob  = np.random.uniform(0.4, 1.0)  # starting mastery

        sequence = []

        for step in range(seq_len):
            # Time gap since last review
            days_gap = np.random.choice(REVIEW_GAPS)

            # Apply Ebbinghaus decay
            recall_prob = recall_prob * np.exp(-days_gap / stability)
            recall_prob = float(np.clip(recall_prob, 0.05, 1.0))

            # Quiz score with realistic noise
            base_score  = recall_prob * 100
            noise       = np.random.normal(0, 8)
            score       = float(np.clip(base_score + noise, 0, 100))

            # Time spent studying (minutes) — harder topics = more time
            time_spent  = float(np.random.uniform(
                5 + difficulty * 2,
                20 + difficulty * 5
            ))

            # Self confidence rating (1-5)
            # Correlated with score but not perfectly
            if score >= 80:
                self_rating = np.random.choice([4, 5], p=[0.4, 0.6])
            elif score >= 60:
                self_rating = np.random.choice([3, 4], p=[0.6, 0.4])
            elif score >= 40:
                self_rating = np.random.choice([2, 3], p=[0.6, 0.4])
            else:
                self_rating = np.random.choice([1, 2], p=[0.7, 0.3])

            sequence.append([
                score / 100,           # feature 1: normalised score
                time_spent / 45,       # feature 2: normalised time
                days_gap / 30,         # feature 3: normalised gap
                difficulty / 5,        # feature 4: normalised difficulty
                self_rating / 5        # feature 5: normalised self rating
            ])

            # SM-2 principle: stability grows after successful review
            if score >= 60:
                stability = stability * (1.0 + 0.3 * (score / 100))
            else:
                # Failed review — stability drops slightly
                stability = max(1.0, stability * 0.85)

        # Target: will student recall at NEXT review?
        next_gap    = np.random.choice([1, 3, 7, 14, 21])
        next_recall = recall_prob * np.exp(-next_gap / stability)
        label       = 1 if next_recall > 0.7 else 0

        X.append(sequence)
        y.append(label)

    X = np.array(X, dtype=np.float32)  # shape: (n, seq_len, 5)
    y = np.array(y, dtype=np.float32)  # shape: (n,)

    print(f"Forgetting data shape  — X: {X.shape}  y: {y.shape}")
    print(f"Class balance          — recall: {y.mean():.2%}  forget: {1-y.mean():.2%}")

    if save:
        np.save(SYNTH_DIR / "forgetting_X.npy", X)
        np.save(SYNTH_DIR / "forgetting_y.npy", y)
        print(f"Saved to {SYNTH_DIR}")

    return X, y


# ─────────────────────────────────────────────────────────────
# MODEL B — Backlog predictor data generator
# Simulates 14 days of study behaviour per student per subject
# Models 5 Indian student archetypes
# ─────────────────────────────────────────────────────────────

def generate_backlog_sequences(
    n_sequences: int = 40000,
    seq_len:     int = 14,
    save:        bool = True
) -> tuple:
    """
    Generates synthetic sequences of student daily study logs.

    Each sequence = 14 days of one student studying one subject.
    Features per day (6):
        1. topics covered today (normalised)
        2. study time in minutes (normalised)
        3. quiz score today (normalised)
        4. days skipped streak (normalised)
        5. chapters remaining (normalised)
        6. days to exam (normalised)

    Target (1):
        Backlog severity score 0.0 - 1.0
        (0 = no backlog, 1 = severe backlog crisis)
    """
    print(f"Generating {n_sequences} backlog sequences...")

    X, y = [], []

    # Indian student archetypes with realistic weights
    ARCHETYPES = {
        "consistent_studier": {
            "weight":          0.15,
            "description":     "Studies every day, covers planned chapters",
        },
        "last_minute_crammer": {
            "weight":          0.35,
            "description":     "Does nothing until 2 weeks before exam",
        },
        "chapter_skipper": {
            "weight":          0.20,
            "description":     "Skips hard chapters, does easy ones only",
        },
        "coaching_dependent": {
            "weight":          0.15,
            "description":     "Only studies on coaching class days",
        },
        "burnout_student": {
            "weight":          0.15,
            "description":     "Starts strong, collapses mid-semester",
        },
    }

    archetype_names   = list(ARCHETYPES.keys())
    archetype_weights = [ARCHETYPES[a]["weight"] for a in archetype_names]

    for _ in range(n_sequences):
        archetype         = np.random.choice(archetype_names, p=archetype_weights)
        chapters_total    = np.random.randint(8, 25)
        chapters_left     = float(chapters_total)
        days_to_exam      = np.random.randint(20, 90)
        avg_difficulty    = np.random.uniform(2.0, 5.0)

        sequence = []

        for day in range(seq_len):
            days_remaining = max(1, days_to_exam - day)

            # ── Consistent studier ──────────────────────────
            if archetype == "consistent_studier":
                covered   = np.random.randint(1, 3)
                time      = np.random.uniform(90, 150)
                score     = np.random.uniform(65, 92)
                skipped   = 0

            # ── Last minute crammer ─────────────────────────
            elif archetype == "last_minute_crammer":
                if days_remaining > 14:
                    covered = int(np.random.choice(
                        [0, 0, 0, 1, 2],
                        p=[0.45, 0.25, 0.10, 0.15, 0.05]
                    ))
                    time    = np.random.uniform(0, 30)
                    score   = np.random.uniform(25, 50)
                    skipped = int(np.random.choice([0, 1, 2, 3]))
                else:
                    # Panic mode kicks in
                    covered = np.random.randint(2, 6)
                    time    = np.random.uniform(180, 360)
                    score   = np.random.uniform(50, 75)
                    skipped = 0

            # ── Chapter skipper ─────────────────────────────
            elif archetype == "chapter_skipper":
                # Skips hard chapters (difficulty > 4)
                skip_chance = (avg_difficulty - 2) / 3
                if np.random.random() < skip_chance:
                    covered = 0
                    time    = np.random.uniform(0, 20)
                    score   = np.random.uniform(15, 35)
                    skipped = 1
                else:
                    covered = np.random.randint(1, 3)
                    time    = np.random.uniform(30, 80)
                    score   = np.random.uniform(55, 78)
                    skipped = 0

            # ── Coaching dependent ──────────────────────────
            elif archetype == "coaching_dependent":
                # Studies only 3 days a week (coaching days)
                is_coaching_day = (day % 3 == 0)
                if is_coaching_day:
                    covered = np.random.randint(1, 3)
                    time    = np.random.uniform(60, 120)
                    score   = np.random.uniform(55, 78)
                    skipped = 0
                else:
                    covered = 0
                    time    = np.random.uniform(0, 15)
                    score   = np.random.uniform(20, 40)
                    skipped = 1

            # ── Burnout student ─────────────────────────────
            else:
                decay_factor = max(0.0, 1.0 - (day / seq_len) * 1.8)
                covered = max(0, int(
                    np.random.randint(2, 4) * decay_factor
                ))
                time    = max(0.0, float(
                    np.random.uniform(80, 140) * decay_factor
                ))
                score   = max(15.0, float(
                    np.random.uniform(65, 88) * decay_factor
                    + np.random.normal(0, 5)
                ))
                skipped = 0 if day < 6 else int(
                    np.random.choice([0, 1], p=[0.4, 0.6])
                )

            # Update chapters remaining
            chapters_left = max(0.0, chapters_left - covered)

            sequence.append([
                min(covered, 6) / 6,            # feature 1
                min(time, 360) / 360,            # feature 2
                float(np.clip(score, 0, 100)) / 100,  # feature 3
                min(skipped, 7) / 7,             # feature 4
                chapters_left / chapters_total,  # feature 5
                min(days_remaining, 90) / 90,    # feature 6
            ])

        # ── Compute backlog severity ────────────────────────
        # Factors:
        # 1. How many chapters are left vs total
        # 2. How close is the exam
        # 3. Average difficulty of subject
        completion_ratio = 1 - (chapters_left / chapters_total)
        days_factor      = 1 / max(1, days_to_exam - seq_len) * 10
        diff_factor      = avg_difficulty / 5

        severity = (
            (1 - completion_ratio) * 5     # uncovered chapters
            + days_factor * 3              # exam proximity
            + diff_factor * 2              # subject difficulty
        )
        severity = float(np.clip(severity, 0, 10)) / 10  # normalise 0-1

        X.append(sequence)
        y.append(severity)

    X = np.array(X, dtype=np.float32)  # shape: (n, seq_len, 6)
    y = np.array(y, dtype=np.float32)  # shape: (n,)

    print(f"Backlog data shape     — X: {X.shape}  y: {y.shape}")
    print(f"Severity distribution  — mean: {y.mean():.3f}  std: {y.std():.3f}")

    if save:
        np.save(SYNTH_DIR / "backlog_X.npy", X)
        np.save(SYNTH_DIR / "backlog_y.npy", y)
        print(f"Saved to {SYNTH_DIR}")

    return X, y


# ─────────────────────────────────────────────────────────────
# Preprocessing — normalise and split for training
# ─────────────────────────────────────────────────────────────

def preprocess_and_split(
    X: np.ndarray,
    y: np.ndarray,
    val_split:  float = 0.15,
    test_split: float = 0.05,
    prefix:     str   = "forgetting",
    save:       bool  = True
) -> dict:
    """
    Splits data into train / val / test sets.
    Data is already normalised during generation
    so no further scaling needed.

    Returns dict with keys:
        X_train, y_train
        X_val,   y_val
        X_test,  y_test
    """
    n         = len(X)
    n_test    = int(n * test_split)
    n_val     = int(n * val_split)
    n_train   = n - n_val - n_test

    # Shuffle before splitting
    indices   = np.random.permutation(n)
    X, y      = X[indices], y[indices]

    splits = {
        "X_train": X[:n_train],
        "y_train": y[:n_train],
        "X_val":   X[n_train:n_train + n_val],
        "y_val":   y[n_train:n_train + n_val],
        "X_test":  X[n_train + n_val:],
        "y_test":  y[n_train + n_val:],
    }

    print(f"\n{prefix} splits:")
    print(f"  Train : {splits['X_train'].shape}")
    print(f"  Val   : {splits['X_val'].shape}")
    print(f"  Test  : {splits['X_test'].shape}")

    if save:
        for key, arr in splits.items():
            path = PROC_DIR / f"{prefix}_{key}.npy"
            np.save(path, arr)
        print(f"Saved processed splits to {PROC_DIR}")

    return splits


# ─────────────────────────────────────────────────────────────
# Augment with real datasets (optional)
# Called only if real CSVs are present in data/raw/
# ─────────────────────────────────────────────────────────────

def augment_with_zenodo(
    X: np.ndarray,
    y: np.ndarray,
    zenodo_path: str = None
) -> tuple:
    """
    Optionally augments backlog sequences with patterns
    derived from the Zenodo Indian student dataset.
    Only runs if the CSV file is present.
    """
    if zenodo_path is None:
        zenodo_path = BASE_DIR / "data" / "raw" / "zenodo" / "student_data.csv"

    if not Path(zenodo_path).exists():
        print("Zenodo dataset not found — skipping augmentation")
        return X, y

    print("Augmenting with Zenodo dataset...")
    df = pd.read_csv(zenodo_path)

    # Map Zenodo columns to our feature space
    # Zenodo has: StudyTimeWeekly, StressLevel, Motivation, GPA etc.
    augmented_X, augmented_y = [], []

    for _, row in df.iterrows():
        try:
            study_hours  = float(row.get("StudyTimeWeekly", 14)) / 7
            stress       = float(row.get("StressLevel",       3))
            motivation   = float(row.get("Motivation",         3))
            gpa          = float(row.get("GPA",               2.5))
            exam_score   = (gpa / 4.0) * 100

            # Build a 14-day sequence from aggregate stats
            sequence = []
            chapters_left = 15.0

            for day in range(14):
                # More stress = fewer chapters covered
                covered   = max(0, np.random.poisson(
                    max(0.1, (motivation / 3) * 1.5 - (stress / 5))
                ))
                time      = max(0, study_hours * 60 + np.random.normal(0, 15))
                score     = max(0, min(100,
                    exam_score + np.random.normal(0, 10)
                ))
                skipped   = 1 if stress > 3.5 and np.random.random() > 0.65 else 0
                chapters_left = max(0, chapters_left - covered)

                sequence.append([
                    min(covered, 6) / 6,
                    min(time, 360) / 360,
                    score / 100,
                    skipped,
                    chapters_left / 15,
                    max(0, (90 - day)) / 90,
                ])

            severity = float(np.clip(
                (chapters_left / 15) * 5 + (stress / 5) * 3, 0, 10
            )) / 10

            augmented_X.append(sequence)
            augmented_y.append(severity)

        except Exception:
            continue

    if augmented_X:
        aug_X = np.array(augmented_X, dtype=np.float32)
        aug_y = np.array(augmented_y, dtype=np.float32)
        X     = np.concatenate([X, aug_X], axis=0)
        y     = np.concatenate([y, aug_y], axis=0)
        print(f"Added {len(aug_X)} Zenodo sequences → total: {len(X)}")

    return X, y


def augment_with_duolingo(
    X: np.ndarray,
    y: np.ndarray,
    duolingo_path: str = None
) -> tuple:
    """
    Optionally augments forgetting sequences with patterns
    from the Duolingo SLAM dataset.
    Only runs if the file is present.
    """
    if duolingo_path is None:
        duolingo_path = BASE_DIR / "data" / "raw" / "duolingo" / "train.jsonl"

    if not Path(duolingo_path).exists():
        print("Duolingo dataset not found — skipping augmentation")
        return X, y

    print("Augmenting with Duolingo SLAM dataset...")
    import json

    augmented_X, augmented_y = [], []
    sequence                 = []
    prev_user                = None

    with open(duolingo_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                user  = entry.get("user_id", "unknown")

                if user != prev_user and len(sequence) >= 10:
                    # Save completed sequence
                    seq_arr  = np.array(sequence[-10:], dtype=np.float32)
                    label    = 1 if sequence[-1][0] > 0.7 else 0
                    augmented_X.append(seq_arr)
                    augmented_y.append(float(label))
                    sequence = []

                prev_user = user

                # Map Duolingo fields to our 5 features
                p_recall  = float(entry.get("p_recall",        0.7))
                delta     = float(entry.get("delta",           1))
                h_seen    = float(entry.get("history_seen",    1))
                h_correct = float(entry.get("history_correct", 1))
                score     = p_recall * 100
                gap       = min(delta, 30)
                difficulty = max(1, min(5, 6 - (h_correct / max(1, h_seen)) * 5))
                self_rating = max(1, min(5, round(p_recall * 5)))

                sequence.append([
                    score / 100,
                    0.5,            # time unknown in Duolingo data
                    gap / 30,
                    difficulty / 5,
                    self_rating / 5,
                ])

            except Exception:
                continue

    if augmented_X:
        aug_X = np.array(augmented_X, dtype=np.float32)
        aug_y = np.array(augmented_y, dtype=np.float32)
        X     = np.concatenate([X, aug_X], axis=0)
        y     = np.concatenate([y, aug_y], axis=0)
        print(f"Added {len(aug_X)} Duolingo sequences → total: {len(X)}")

    return X, y


# ─────────────────────────────────────────────────────────────
# Main runner — call this from Colab
# ─────────────────────────────────────────────────────────────

def generate_all_data(
    n_forgetting: int  = 50000,
    n_backlog:    int  = 40000,
    augment_real: bool = True
):
    """
    Generates both datasets, optionally augments with
    real data if CSVs are present, saves all splits.
    Call this from the Colab training notebook.
    """
    print("=" * 55)
    print("LearnFlow — Synthetic Data Generator")
    print("=" * 55)

    # ── Model A data ────────────────────────────────────────
    print("\n[1/4] Generating forgetting curve sequences...")
    X_f, y_f = generate_forgetting_sequences(
        n_sequences=n_forgetting, save=True
    )

    if augment_real:
        X_f, y_f = augment_with_duolingo(X_f, y_f)
        # Re-save augmented version
        np.save(SYNTH_DIR / "forgetting_X.npy", X_f)
        np.save(SYNTH_DIR / "forgetting_y.npy", y_f)

    print("\n[2/4] Preprocessing forgetting data...")
    forgetting_splits = preprocess_and_split(
        X_f, y_f, prefix="forgetting", save=True
    )

    # ── Model B data ────────────────────────────────────────
    print("\n[3/4] Generating backlog sequences...")
    X_b, y_b = generate_backlog_sequences(
        n_sequences=n_backlog, save=True
    )

    if augment_real:
        X_b, y_b = augment_with_zenodo(X_b, y_b)
        # Re-save augmented version
        np.save(SYNTH_DIR / "backlog_X.npy", X_b)
        np.save(SYNTH_DIR / "backlog_y.npy", y_b)

    print("\n[4/4] Preprocessing backlog data...")
    backlog_splits = preprocess_and_split(
        X_b, y_b, prefix="backlog", save=True
    )

    print("\n" + "=" * 55)
    print("Data generation complete!")
    print(f"Synthetic files → {SYNTH_DIR}")
    print(f"Processed files → {PROC_DIR}")
    print("=" * 55)

    return forgetting_splits, backlog_splits


if __name__ == "__main__":
    generate_all_data()