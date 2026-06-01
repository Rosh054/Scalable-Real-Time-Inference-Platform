#!/usr/bin/env python3
"""Train Iris classifier and save joblib artifact."""

import argparse
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def train(output_path: Path) -> float:
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    accuracy = float(model.score(X_test, y_test))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"Model saved to {output_path} (test accuracy: {accuracy:.4f})")
    return accuracy


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Iris classifier")
    parser.add_argument(
        "--output",
        default="models/model.joblib",
        help="Output path for joblib model",
    )
    args = parser.parse_args()
    train(Path(args.output))


if __name__ == "__main__":
    main()
