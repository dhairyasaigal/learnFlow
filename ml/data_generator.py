# ml/data_generator.py
import numpy as np
import pandas as pd
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
BASE_DIR  = Path(__file__).resolve().parent.parent
SYNTH_DIR = BASE_DIR / "data" / "synthetic"
PROC_DIR  = BASE_DIR / "data" / "processed"

SYNTH_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────
# MODEL A — Forgetting curve data generator
# ─────────────────────────────────────────────────────────────

def generate_forgetting_sequences(
    n_sequences: int  = 50000,
    seq_len:     int  = 10,
    save:        bool = True
) -> tuple:
    """
    Generates synthetic sequences of student review sessions.
    Features per step (5):
        1. normalised quiz score
        2. normalised time spent
        3. normalised days gap since last review
        4. normalised topic difficulty
        5. normalised self rating
    Target: 1 = will recall, 0 = will forget
    """
    print(f"Generating {n_sequences} forgetting sequences...")

    X, y = [], []

    STUDENT_PROFILES = {
        "strong_retainer":  {"stability_range": (15, 30), "weight": 0.15},
        "average_retainer": {"stability_range": (7,  15), "weight": 0.50},
        "weak_retainer":    {"stability_range": (2,   7), "weight": 0.25},
        "rote_learner":     {"stability_range": (1,   4), "weight": 0.10},
    }

    profile_names   = list(STUDENT_PROFILES.keys())
    profile_weights = [STUDENT_PROFILES[p]["weight"] for p in profile_names]
    REVIEW_GAPS     = [1, 1, 2, 3, 3, 5, 7, 7, 10, 14, 21, 30]

    for _ in range(n_sequences):
        profile_name = np.random.choice(profile_names, p=profile_weights)
        profile      = STUDENT_PROFILES[profile_name]
        stability    = np.random.uniform(*profile["stability_range"])
        difficulty   = np.random.uniform(1.0, 5.0)
        recall_prob  = np.random.uniform(0.4, 1.0)
        sequence     = []

        for step in range(seq_len):
            days_gap    = np.random.choice(REVIEW_GAPS)
            recall_prob = recall_prob * np.exp(-days_gap / stability)
            recall_prob = float(np.clip(recall_prob, 0.05, 1.0))

            base_score  = recall_prob * 100
            score       = float(np.clip(base_score + np.random.normal(0, 8), 0, 100))
            time_spent  = float(np.random.uniform(5 + difficulty * 2, 20 + difficulty * 5))

            if score >= 80:
                self_rating = np.random.choice([4, 5], p=[0.4, 0.6])
            elif score >= 60:
                self_rating = np.random.choice([3, 4], p=[0.6, 0.4])
            elif score >= 40:
                self_rating = np.random.choice([2, 3], p=[0.6, 0.4])
            else:
                self_rating = np.random.choice([1, 2], p=[0.7, 0.3])

            sequence.append([
                score / 100,
                time_spent / 45,
                days_gap / 30,
                difficulty / 5,
                self_rating / 5
            ])

            if score >= 60:
                stability = stability * (1.0 + 0.3 * (score / 100))
            else:
                stability = max(1.0, stability * 0.85)

        next_gap    = np.random.choice([1, 3, 7, 14, 21])
        next_recall = recall_prob * np.exp(-next_gap / stability)
        label       = 1 if next_recall > 0.7 else 0

        X.append(sequence)
        y.append(label)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    print(f"Forgetting data — X: {X.shape}  y: {y.shape}")
    print(f"Class balance   — recall: {y.mean():.2%}  forget: {1-y.mean():.2%}")

    if save:
        np.save(SYNTH_DIR / "forgetting_X.npy", X)
        np.save(SYNTH_DIR / "forgetting_y.npy", y)
        print(f"Saved to {SYNTH_DIR}")

    return X, y


# ─────────────────────────────────────────────────────────────
# MODEL B — Backlog predictor data generator
# ─────────────────────────────────────────────────────────────

def generate_backlog_sequences(
    n_sequences: int  = 40000,
    seq_len:     int  = 14,
    save:        bool = True
) -> tuple:
    """
    Generates synthetic sequences of student daily study logs.
    Features per day (6):
        1. topics covered today (normalised)
        2. study time in minutes (normalised)
        3. quiz score today (normalised)
        4. days skipped streak (normalised)
        5. chapters remaining (normalised)
        6. days to exam (normalised)
    Target: backlog severity 0.0 - 1.0
    """
    print(f"Generating {n_sequences} backlog sequences...")

    X, y = [], []

    ARCHETYPES = {
        "consistent_studier":  {"weight": 0.15},
        "last_minute_crammer": {"weight": 0.35},
        "chapter_skipper":     {"weight": 0.20},
        "coaching_dependent":  {"weight": 0.15},
        "burnout_student":     {"weight": 0.15},
    }

    archetype_names   = list(ARCHETYPES.keys())
    archetype_weights = [ARCHETYPES[a]["weight"] for a in archetype_names]

    for _ in range(n_sequences):
        archetype      = np.random.choice(archetype_names, p=archetype_weights)
        chapters_total = np.random.randint(8, 25)
        chapters_left  = float(chapters_total)
        days_to_exam   = np.random.randint(20, 90)
        avg_difficulty = np.random.uniform(2.0, 5.0)
        sequence       = []

        for day in range(seq_len):
            days_remaining = max(1, days_to_exam - day)

            if archetype == "consistent_studier":
                covered = np.random.randint(1, 3)
                time    = np.random.uniform(90, 150)
                score   = np.random.uniform(65, 92)
                skipped = 0

            elif archetype == "last_minute_crammer":
                if days_remaining > 14:
                    covered = int(np.random.choice(
                        [0, 0, 0, 1, 2], p=[0.45, 0.25, 0.10, 0.15, 0.05]
                    ))
                    time    = np.random.uniform(0, 30)
                    score   = np.random.uniform(25, 50)
                    skipped = int(np.random.choice([0, 1, 2, 3]))
                else:
                    covered = np.random.randint(2, 6)
                    time    = np.random.uniform(180, 360)
                    score   = np.random.uniform(50, 75)
                    skipped = 0

            elif archetype == "chapter_skipper":
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

            elif archetype == "coaching_dependent":
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

            else:  # burnout_student
                decay_factor = max(0.0, 1.0 - (day / seq_len) * 1.8)
                covered = max(0, int(np.random.randint(2, 4) * decay_factor))
                time    = max(0.0, float(np.random.uniform(80, 140) * decay_factor))
                score   = max(15.0, float(
                    np.random.uniform(65, 88) * decay_factor
                    + np.random.normal(0, 5)
                ))
                skipped = 0 if day < 6 else int(
                    np.random.choice([0, 1], p=[0.4, 0.6])
                )

            chapters_left = max(0.0, chapters_left - covered)

            sequence.append([
                min(covered, 6) / 6,
                min(time, 360) / 360,
                float(np.clip(score, 0, 100)) / 100,
                min(skipped, 7) / 7,
                chapters_left / chapters_total,
                min(days_remaining, 90) / 90,
            ])

        completion_ratio = 1 - (chapters_left / chapters_total)
        days_factor      = 1 / max(1, days_to_exam - seq_len) * 10
        diff_factor      = avg_difficulty / 5

        severity = (
            (1 - completion_ratio) * 5
            + days_factor * 3
            + diff_factor * 2
        )
        severity = float(np.clip(severity, 0, 10)) / 10

        X.append(sequence)
        y.append(severity)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    print(f"Backlog data    — X: {X.shape}  y: {y.shape}")
    print(f"Severity dist   — mean: {y.mean():.3f}  std: {y.std():.3f}")

    if save:
        np.save(SYNTH_DIR / "backlog_X.npy", X)
        np.save(SYNTH_DIR / "backlog_y.npy", y)
        print(f"Saved to {SYNTH_DIR}")

    return X, y


# ─────────────────────────────────────────────────────────────
# Preprocessing
# ─────────────────────────────────────────────────────────────

def preprocess_and_split(
    X:          np.ndarray,
    y:          np.ndarray,
    val_split:  float = 0.15,
    test_split: float = 0.05,
    prefix:     str   = "forgetting",
    save:       bool  = True
) -> dict:
    """Splits data into train / val / test and saves."""
    n       = len(X)
    n_test  = int(n * test_split)
    n_val   = int(n * val_split)
    n_train = n - n_val - n_test

    indices = np.random.permutation(n)
    X, y    = X[indices], y[indices]

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
            np.save(PROC_DIR / f"{prefix}_{key}.npy", arr)
        print(f"Saved to {PROC_DIR}")

    return splits


# ─────────────────────────────────────────────────────────────
# Augmentation — Zenodo dataset
# ─────────────────────────────────────────────────────────────

def augment_with_zenodo(
    X: np.ndarray,
    y: np.ndarray,
    zenodo_path: str = None
) -> tuple:
    """Augments backlog sequences with Zenodo Indian student dataset."""
    if zenodo_path is None:
        zenodo_path = BASE_DIR / "data" / "raw" / "zenodo" / "merged_dataset.csv"

    if not Path(zenodo_path).exists():
        print("Zenodo dataset not found — skipping")
        return X, y

    print("Augmenting with Zenodo dataset...")
    df             = pd.read_csv(zenodo_path)
    augmented_X, augmented_y = [], []

    for _, row in df.iterrows():
        try:
            study_hours = float(row.get("StudyTimeWeekly", 14)) / 7
            stress      = float(row.get("StressLevel",      3))
            motivation  = float(row.get("Motivation",        3))
            gpa         = float(row.get("GPA",              2.5))
            exam_score  = (gpa / 4.0) * 100
            sequence    = []
            chapters_left = 15.0

            for day in range(14):
                covered = max(0, np.random.poisson(
                    max(0.1, (motivation / 3) * 1.5 - (stress / 5))
                ))
                time    = max(0, study_hours * 60 + np.random.normal(0, 15))
                score   = max(0, min(100, exam_score + np.random.normal(0, 10)))
                skipped = 1 if stress > 3.5 and np.random.random() > 0.65 else 0
                chapters_left = max(0, chapters_left - covered)

                sequence.append([
                    min(covered, 6) / 6,
                    min(time, 360) / 360,
                    score / 100,
                    float(skipped),
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


# ─────────────────────────────────────────────────────────────
# Augmentation — Study Hours dataset
# ─────────────────────────────────────────────────────────────

def augment_with_study_hours(
    X:    np.ndarray,
    y:    np.ndarray,
    path: str = None
) -> tuple:
    """Augments backlog sequences with StudentPerformanceFactors dataset."""
    if path is None:
        path = BASE_DIR / "data" / "raw" / "study_hours" / "StudentPerformanceFactors.csv"

    if not Path(path).exists():
        print("Study hours dataset not found — skipping")
        return X, y

    print("Augmenting with Study Hours dataset...")
    df             = pd.read_csv(path)
    augmented_X, augmented_y = [], []

    for _, row in df.iterrows():
        try:
            study_hours = float(row.get("Hours_Studied",    14)) / 7
            attendance  = float(row.get("Attendance",       75)) / 100
            motivation  = float(row.get("Motivation_Level",  3))
            exam_score  = float(row.get("Exam_Score",       60))
            prev_scores = float(row.get("Previous_Scores",  60))
            sequence    = []
            chapters_left = 15.0

            for day in range(14):
                skipped = 1 if attendance < 0.75 and np.random.random() > 0.6 else 0
                covered = max(0, int(np.random.poisson(
                    max(0.1, study_hours * motivation / 3)
                ))) if not skipped else 0
                time    = max(0, study_hours * 60 + np.random.normal(0, 10))
                score   = max(0, min(100,
                    (exam_score + prev_scores) / 2 + np.random.normal(0, 8)
                ))
                chapters_left = max(0, chapters_left - covered)

                sequence.append([
                    min(covered, 6) / 6,
                    min(time, 360) / 360,
                    score / 100,
                    float(skipped),
                    chapters_left / 15,
                    max(0, (90 - day)) / 90,
                ])

            severity = float(np.clip(
                (chapters_left / 15) * 6
                + (1 - attendance) * 3
                + (1 - exam_score / 100) * 1,
                0, 10
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
        print(f"Added {len(aug_X)} study hours sequences → total: {len(X)}")

    return X, y


# ─────────────────────────────────────────────────────────────
# Augmentation — Duolingo (skips if file not present)
# ─────────────────────────────────────────────────────────────

def augment_with_duolingo(
    X: np.ndarray,
    y: np.ndarray,
    duolingo_path: str = None
) -> tuple:
    """Augments forgetting sequences with Duolingo SLAM dataset."""
    if duolingo_path is None:
        duolingo_path = BASE_DIR / "data" / "raw" / "duolingo" / "train.jsonl"

    if not Path(duolingo_path).exists():
        print("Duolingo dataset not found — skipping")
        return X, y

    print("Augmenting with Duolingo dataset...")
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
                    seq_arr = np.array(sequence[-10:], dtype=np.float32)
                    label   = 1 if sequence[-1][0] > 0.7 else 0
                    augmented_X.append(seq_arr)
                    augmented_y.append(float(label))
                    sequence = []

                prev_user   = user
                p_recall    = float(entry.get("p_recall",        0.7))
                delta       = float(entry.get("delta",           1))
                h_seen      = float(entry.get("history_seen",    1))
                h_correct   = float(entry.get("history_correct", 1))
                score       = p_recall * 100
                gap         = min(delta, 30)
                difficulty  = max(1, min(5, 6 - (h_correct / max(1, h_seen)) * 5))
                self_rating = max(1, min(5, round(p_recall * 5)))

                sequence.append([
                    score / 100,
                    0.5,
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
    Generates both datasets, augments with real data
    if CSVs are present, saves all processed splits.
    Call this from the Colab training notebook.
    """
    print("=" * 55)
    print("LearnFlow — Synthetic Data Generator")
    print("=" * 55)

    # ── Model A ─────────────────────────────────────────────
    print("\n[1/4] Generating forgetting sequences...")
    X_f, y_f = generate_forgetting_sequences(n_forgetting, save=True)

    if augment_real:
        X_f, y_f = augment_with_duolingo(X_f, y_f)
        np.save(SYNTH_DIR / "forgetting_X.npy", X_f)
        np.save(SYNTH_DIR / "forgetting_y.npy", y_f)

    print("\n[2/4] Preprocessing forgetting data...")
    forgetting_splits = preprocess_and_split(X_f, y_f, prefix="forgetting", save=True)

    # ── Model B ─────────────────────────────────────────────
    print("\n[3/4] Generating backlog sequences...")
    X_b, y_b = generate_backlog_sequences(n_backlog, save=True)

    if augment_real:
        X_b, y_b = augment_with_zenodo(X_b, y_b)
        X_b, y_b = augment_with_study_hours(X_b, y_b)
        np.save(SYNTH_DIR / "backlog_X.npy", X_b)
        np.save(SYNTH_DIR / "backlog_y.npy", y_b)

    print("\n[4/4] Preprocessing backlog data...")
    backlog_splits = preprocess_and_split(X_b, y_b, prefix="backlog", save=True)

    print("\n" + "=" * 55)
    print("Data generation complete!")
    print(f"Synthetic → {SYNTH_DIR}")
    print(f"Processed → {PROC_DIR}")
    print("=" * 55)

    return forgetting_splits, backlog_splits


if __name__ == "__main__":
    generate_all_data()