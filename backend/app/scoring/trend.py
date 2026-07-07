from __future__ import annotations

from backend.app.utils.math import clamp


def trend_score(video_growth: float, creator_growth: float, engagement_growth: float) -> float:
    raw = video_growth * 0.35 + creator_growth * 0.35 + engagement_growth * 0.3
    return round(clamp(raw), 2)
