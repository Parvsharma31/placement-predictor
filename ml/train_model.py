import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
N_SAMPLES = 1000
NOISE_FRACTION = 0.02
SIGMOID_STEEPNESS = 0.25
MODEL_PATH = Path(__file__).parent / "model.pkl"

FEATURE_COLUMNS = [
    "cgpa",
    "aptitude_score",
    "communication_score",
    "dsa_score",
    "projects",
    "internship_experience",
]
TARGET_COLUMN = "placed"


def generate_dataset(n_samples: int = N_SAMPLES, random_state: int = RANDOM_STATE) -> pd.DataFrame:
    np.random.seed(random_state)

    cgpa = np.random.uniform(4.0, 10.0, size=n_samples).round(2)
    aptitude_score = np.random.randint(40, 101, size=n_samples)
    communication_score = np.random.randint(40, 101, size=n_samples)
    dsa_score = np.random.randint(40, 101, size=n_samples)
    projects = np.random.randint(0, 9, size=n_samples)
    internship_experience = np.random.randint(0, 2, size=n_samples)

    placement_score = (
        (cgpa / 10.0) * 35
        + (aptitude_score / 100.0) * 20
        + (communication_score / 100.0) * 15
        + (dsa_score / 100.0) * 15
        + (projects / 8.0) * 10
        + internship_experience * 5
    )
    placement_prob = 1 / (1 + np.exp(-SIGMOID_STEEPNESS * (placement_score - 50)))
    placed = (np.random.random(n_samples) < placement_prob).astype(int)

    noise_count = int(n_samples * NOISE_FRACTION)
    noise_indices = np.random.choice(n_samples, size=noise_count, replace=False)
    placed[noise_indices] = 1 - placed[noise_indices]

    return pd.DataFrame(
        {
            "cgpa": cgpa,
            "aptitude_score": aptitude_score,
            "communication_score": communication_score,
            "dsa_score": dsa_score,
            "projects": projects,
            "internship_experience": internship_experience,
            "placed": placed,
        }
    )


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train_and_evaluate() -> Pipeline:
    dataset = generate_dataset()
    X = dataset[FEATURE_COLUMNS]
    y = dataset[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

    return pipeline


def save_model(pipeline: Pipeline, model_path: Path = MODEL_PATH) -> None:
    with model_path.open("wb") as model_file:
        pickle.dump(pipeline, model_file)
    print("Model saved to ml/model.pkl")


if __name__ == "__main__":
    trained_pipeline = train_and_evaluate()
    save_model(trained_pipeline)
