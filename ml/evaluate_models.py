#!/usr/bin/env python3
"""
ml/evaluate_models.py
Evaluates both trained LearnFlow models and prints a comprehensive report.
Run this on the training machine after training to confirm model quality.

Usage:
    python -m ml.evaluate_models
"""
import sys
import numpy as np
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models" / "saved"


def evaluate_forgetting_model():
    print("\n" + "=" * 60)
    print("Forgetting Model Evaluation")
    print("=" * 60)

    model_path = MODELS_DIR / "forgetting_model.h5"
    if not model_path.exists():
        print("  ERROR: forgetting_model.h5 not found. Train first.")
        return

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(str(model_path))
        print(f"  Model loaded: {model_path}")
    except Exception as e:
        print(f"  ERROR loading model: {e}")
        return

    X_test_path = PROC_DIR / "forgetting_X_test.npy"
    y_test_path = PROC_DIR / "forgetting_y_test.npy"

    if not X_test_path.exists():
        print("  No test data found. Generating fresh samples...")
        from ml.data_generator import generate_forgetting_sequences
        X, y = generate_forgetting_sequences(n_sequences=5000, save=False)
        idx   = np.random.permutation(len(X))[:500]
        X_test, y_test = X[idx], y[idx]
    else:
        X_test = np.load(str(X_test_path))
        y_test = np.load(str(y_test_path))

    loss, acc, auc = model.evaluate(X_test, y_test, verbose=0)
    preds = model.predict(X_test, verbose=0).flatten()

    # Confusion metrics
    pred_binary = (preds >= 0.5).astype(int)
    tp = int(((pred_binary == 1) & (y_test == 1)).sum())
    tn = int(((pred_binary == 0) & (y_test == 0)).sum())
    fp = int(((pred_binary == 1) & (y_test == 0)).sum())
    fn = int(((pred_binary == 0) & (y_test == 1)).sum())

    precision = tp / max(1, tp + fp)
    recall    = tp / max(1, tp + fn)
    f1        = 2 * precision * recall / max(0.001, precision + recall)

    print(f"\n  Test Accuracy  : {acc:.4f}  ({acc*100:.1f}%)")
    print(f"  Test AUC       : {auc:.4f}")
    print(f"  Test Loss      : {loss:.4f}")
    print(f"\n  Precision      : {precision:.4f}")
    print(f"  Recall         : {recall:.4f}")
    print(f"  F1 Score       : {f1:.4f}")
    print(f"\n  TP:{tp}  TN:{tn}  FP:{fp}  FN:{fn}")
    print(f"  Samples evaluated: {len(X_test)}")

    print(f"\n  Prediction distribution:")
    print(f"    Will Recall (>=0.5): {(preds >= 0.5).sum()} / {len(preds)}")
    print(f"    Will Forget (<0.5): {(preds < 0.5).sum()} / {len(preds)}")

    quality = "GOOD" if acc >= 0.82 else "ACCEPTABLE" if acc >= 0.75 else "NEEDS IMPROVEMENT"
    print(f"\n  Quality: {quality}")


def evaluate_backlog_model():
    print("\n" + "=" * 60)
    print("Backlog Model Evaluation")
    print("=" * 60)

    model_path = MODELS_DIR / "backlog_model.h5"
    if not model_path.exists():
        print("  ERROR: backlog_model.h5 not found. Train first.")
        return

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(str(model_path), compile=False)
        print(f"  Model loaded: {model_path}")
    except Exception as e:
        print(f"  ERROR loading model: {e}")
        return

    X_test_path = PROC_DIR / "backlog_X_test.npy"
    y_test_path = PROC_DIR / "backlog_y_test.npy"

    if not X_test_path.exists():
        print("  No test data found. Generating fresh samples...")
        from ml.data_generator import generate_backlog_sequences
        X, y = generate_backlog_sequences(n_sequences=5000, save=False)
        idx   = np.random.permutation(len(X))[:500]
        X_test, y_test = X[idx], y[idx]
    else:
        X_test = np.load(str(X_test_path))
        y_test = np.load(str(y_test_path))

    preds = model.predict(X_test, verbose=0).flatten()
    loss  = float(((preds - y_test) ** 2).mean())
    mae   = float(np.abs(preds - y_test).mean())
    rmse  = float(np.sqrt(loss))

    # Severity in 0-10 scale
    pred_10  = preds * 10
    true_10  = y_test * 10
    mae_10   = float(np.abs(pred_10 - true_10).mean())
    rmse_10  = float(np.sqrt(((pred_10 - true_10) ** 2).mean()))

    # Categorical accuracy (On Track / Low / Moderate / High / Critical)
    def categorize(s):
        if s < 1.5:  return 0   # On Track
        if s < 3.0:  return 1   # Low
        if s < 5.0:  return 2   # Moderate
        if s < 7.5:  return 3   # High
        return 4                 # Critical

    pred_cats = np.array([categorize(p) for p in pred_10])
    true_cats = np.array([categorize(t) for t in true_10])
    cat_acc   = float((pred_cats == true_cats).mean())
    within_1  = float((np.abs(pred_cats - true_cats) <= 1).mean())

    print(f"\n  Test MSE       : {loss:.4f}")
    print(f"  Test MAE (0-1) : {mae:.4f}  (~= {mae_10:.2f} on 0-10 scale)")
    print(f"  Test RMSE(0-1) : {rmse:.4f}")
    print(f"\n  Severity MAE   : {mae_10:.2f} / 10")
    print(f"  Severity RMSE  : {rmse_10:.2f} / 10")
    print(f"\n  Category Accuracy (exact): {cat_acc:.3f}  ({cat_acc*100:.1f}%)")
    print(f"  Within-1 Category        : {within_1:.3f}  ({within_1*100:.1f}%)")
    print(f"\n  Samples evaluated: {len(X_test)}")
    print(f"\n  Prediction distribution (0-10):")
    for label, lo, hi in [("On Track", 0, 1.5), ("Low", 1.5, 3), ("Moderate", 3, 5), ("High", 5, 7.5), ("Critical", 7.5, 11)]:
        cnt = int(((pred_10 >= lo) & (pred_10 < hi)).sum())
        pct = cnt / len(pred_10) * 100
        print(f"    {label:10}: {cnt:4d}  ({pct:.1f}%)")

    quality = "GOOD" if mae_10 <= 1.5 else "ACCEPTABLE" if mae_10 <= 2.0 else "NEEDS IMPROVEMENT"
    print(f"\n  Quality: {quality}")


if __name__ == "__main__":
    evaluate_forgetting_model()
    evaluate_backlog_model()
    print("\n" + "=" * 60)
    print("Evaluation complete.")
    print("=" * 60)
