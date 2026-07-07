from __future__ import annotations


def calculate_prediction_accuracy(prediction: dict, actual: dict) -> float:
    predicted_roi = float(prediction.get("roi", prediction.get("expected_roi", 0)))
    actual_roi = float(actual.get("roi", 0))
    if predicted_roi <= 0 and actual_roi <= 0:
        return 100.0
    error = abs(predicted_roi - actual_roi) / max(abs(predicted_roi), 1)
    return round(max(0, 100 - error * 100), 2)
