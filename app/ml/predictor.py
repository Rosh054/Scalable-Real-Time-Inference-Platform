"""Model inference."""

from typing import Any

import numpy as np

from app.ml.loader import get_model

FEATURE_NAMES = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
CLASS_NAMES = {0: "setosa", 1: "versicolor", 2: "virginica"}


def predict(features: dict[str, float]) -> int:
    model = get_model()
    row = np.array([[features[name] for name in FEATURE_NAMES]], dtype=np.float64)
    prediction: Any = model.predict(row)
    return int(prediction[0])


def get_input_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "required": FEATURE_NAMES,
        "properties": {
            name: {"type": "number", "description": f"Iris {name.replace('_', ' ')}"}
            for name in FEATURE_NAMES
        },
    }
