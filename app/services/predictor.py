import logging
import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import settings
from app.schemas.request_schema import StudentRequest

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "cgpa",
    "aptitude_score",
    "communication_score",
    "dsa_score",
    "projects",
    "internship_experience",
]

model: Any | None = None


def load_model() -> Any:
    model_path = Path(settings.MODEL_PATH)

    try:
        with model_path.open("rb") as model_file:
            pipeline = pickle.load(model_file)
        logger.info("Model loaded successfully from %s", model_path)
        return pipeline
    except FileNotFoundError as exc:
        message = f"Model file not found at {model_path}"
        logger.error(message)
        raise RuntimeError(message) from exc
    except Exception as exc:
        message = f"Failed to load model from {model_path}: {exc}"
        logger.error(message)
        raise


def predict(student_request: StudentRequest) -> dict[str, str | float]:
    if model is None:
        raise RuntimeError("Model is not loaded. Call load_model() before making predictions.")

    features = pd.DataFrame(
        [
            [
                student_request.academic.cgpa,
                student_request.academic.aptitude_score,
                student_request.skills.communication_score,
                student_request.skills.dsa_score,
                student_request.skills.projects,
                1 if student_request.internship_experience else 0,
            ]
        ],
        columns=FEATURE_COLUMNS,
    )

    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]

    return {
        "placement_prediction": "Placed" if prediction == 1 else "Not Placed",
        "confidence": float(round(max(probabilities) * 100, 2)),
        "placed_probability": float(round(probabilities[1] * 100, 2)),
        "not_placed_probability": float(round(probabilities[0] * 100, 2)),
    }
