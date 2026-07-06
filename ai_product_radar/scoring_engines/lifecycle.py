from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LifecycleClassification:
    stage: str
    score: int
    confidence: int


def classify_lifecycle(stage: str, days_since_first_seen: float) -> LifecycleClassification:
    normalized = stage.strip().lower()
    stage_scores = {
        "emerging": ("新兴", 92, 92),
        "新兴": ("新兴", 92, 92),
        "rising": ("上升", 86, 88),
        "上升": ("上升", 86, 88),
        "peak": ("高峰", 64, 78),
        "高峰": ("高峰", 64, 78),
        "declining": ("下降", 28, 82),
        "下降": ("下降", 28, 82),
    }
    if normalized in stage_scores:
        stage_name, score, confidence = stage_scores[normalized]
        return LifecycleClassification(stage_name, score, confidence)
    if days_since_first_seen <= 0:
        return LifecycleClassification("未知", 62, 45)
    if days_since_first_seen <= 21:
        return LifecycleClassification("新兴", 92, 70)
    if days_since_first_seen <= 60:
        return LifecycleClassification("上升", 86, 68)
    if days_since_first_seen <= 120:
        return LifecycleClassification("高峰", 64, 62)
    return LifecycleClassification("下降", 28, 66)
