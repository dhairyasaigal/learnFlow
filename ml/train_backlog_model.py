#!/usr/bin/env python3
"""
ml/train_backlog_model.py
Trains the LSTM backlog severity prediction model for LearnFlow.
Generates synthetic data, trains, evaluates, and saves the model.

Usage:
    python -m ml.train_backlog_model
    python -m ml.train_backlog_model --epochs 30 --samples 60000
"""
import os
import sys
import argparse
import numpy as np
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "saved"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = MODELS_DIR / "backlog_model.h5"


def train(n_samples: int = 40000, epochs: int = 20, batch_size: int = 256):
    print("=" * 60)
    print("LearnFlow — Backlog Severity LSTM Training")
    print("=" * 60)

    # ── Import TensorFlow ──────────────────────────────────────
    try:
        import tensorflow as tf
        from tensorflow import keras
    except ImportError:
        print("ERROR: TensorFlow is not installed.")
        print("Install it with: pip install tensorflow")
        sys.exit(1)

    tf.get_logger().setLevel("ERROR")
    print(f"TensorFlow version: {tf.__version__}")

    # ── Generate data ──────────────────────────────────────────
    from ml.data_generator import generate_backlog_sequences
    X, y = generate_backlog_sequences(n_sequences=n_samples, save=True)

    # Shuffle
    idx = np.random.permutation(len(X))
    X, y = X[idx], y[idx]

    # Split
    n_train = int(len(X) * 0.80)
    n_val   = int(len(X) * 0.15)
    X_train, y_train = X[:n_train],              y[:n_train]
    X_val,   y_val   = X[n_train:n_train+n_val], y[n_train:n_train+n_val]
    X_test,  y_test  = X[n_train+n_val:],        y[n_train+n_val:]

    print(f"\nSplits — Train: {X_train.shape}  Val: {X_val.shape}  Test: {X_test.shape}")
    print(f"Target dist   — mean: {y_train.mean():.3f}  std: {y_train.std():.3f}")

    # ── Build model ────────────────────────────────────────────
    model = keras.Sequential([
        keras.layers.Input(shape=(X_train.shape[1], X_train.shape[2])),   # (14, 6)

        keras.layers.LSTM(64, return_sequences=True,
                          kernel_regularizer=keras.regularizers.l2(1e-4)),
        keras.layers.Dropout(0.2),

        keras.layers.LSTM(32, return_sequences=False,
                          kernel_regularizer=keras.regularizers.l2(1e-4)),
        keras.layers.Dropout(0.2),

        keras.layers.Dense(16, activation="relu"),
        keras.layers.Dense(1,  activation="sigmoid"),   # severity 0-1
    ], name="backlog_model")

    model.compile(
        optimizer = keras.optimizers.Adam(learning_rate=1e-3),
        loss      = "mse",                       # regression — severity is continuous
        metrics   = ["mae", keras.metrics.RootMeanSquaredError(name="rmse")]
    )
    model.summary()

    # ── Callbacks ──────────────────────────────────────────────
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor  = "val_mae",
            patience = 5,
            mode     = "min",
            restore_best_weights = True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor  = "val_loss",
            factor   = 0.5,
            patience = 3,
            min_lr   = 1e-6
        ),
    ]

    # ── Train ──────────────────────────────────────────────────
    print(f"\nTraining for up to {epochs} epochs...")
    history = model.fit(
        X_train, y_train,
        epochs          = epochs,
        batch_size      = batch_size,
        validation_data = (X_val, y_val),
        callbacks       = callbacks,
        verbose         = 1
    )

    # ── Evaluate ───────────────────────────────────────────────
    print("\nEvaluating on test set...")
    loss, mae, rmse = model.evaluate(X_test, y_test, verbose=0)
    print(f"\n{'='*60}")
    print(f"Test MSE      : {loss:.4f}")
    print(f"Test MAE      : {mae:.4f}  (~= {mae*10:.2f} severity points on 0-10 scale)")
    print(f"Test RMSE     : {rmse:.4f}")
    print("=" * 60)

    # ── Save model ───────────────────────────────────────────
    model.save(str(OUTPUT_PATH))
    print(f"Model saved to: {OUTPUT_PATH}")

    # ── Save training curves ───────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        axes[0].plot(history.history["loss"],     label="Train MSE")
        axes[0].plot(history.history["val_loss"], label="Val MSE")
        axes[0].set_title("Loss (MSE)")
        axes[0].legend()
        axes[0].set_xlabel("Epoch")

        axes[1].plot(history.history["mae"],     label="Train MAE")
        axes[1].plot(history.history["val_mae"], label="Val MAE")
        axes[1].set_title("Mean Absolute Error")
        axes[1].legend()
        axes[1].set_xlabel("Epoch")

        plt.tight_layout()
        plt.savefig(str(MODELS_DIR / "backlog_training_curves.png"), dpi=120)
        plt.close()
        print("Training curves saved to models/saved/backlog_training_curves.png")
    except Exception as e:
        print(f"(Could not save training curves: {e})")

    return model, history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the LearnFlow backlog model")
    parser.add_argument("--samples",    type=int, default=40000, help="Training samples")
    parser.add_argument("--epochs",     type=int, default=20,    help="Max epochs")
    parser.add_argument("--batch-size", type=int, default=256,   help="Batch size")
    args = parser.parse_args()
    train(
        n_samples  = args.samples,
        epochs     = args.epochs,
        batch_size = args.batch_size
    )
