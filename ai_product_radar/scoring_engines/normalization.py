from __future__ import annotations

from .utils import clamp


def normalize_score(value: float) -> int:
    return round(clamp(value))


def normalize_weights(raw_weights: dict[str, float]) -> dict[str, float]:
    total = sum(raw_weights.values())
    if total <= 0:
        raise ValueError("Scoring weights must sum to a positive number.")
    return {key: value / total for key, value in raw_weights.items()}
