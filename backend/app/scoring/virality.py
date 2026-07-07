from __future__ import annotations

import math

from backend.app.utils.math import clamp


def virality_score(views: float, likes: float, shares: float, comments: float) -> float:
    view_signal = clamp(math.log1p(max(views, 0)) / math.log1p(1_000_000) * 100)
    engagement_rate = ((likes + comments * 2 + shares * 3) / views * 100) if views > 0 else 0
    engagement_signal = clamp(engagement_rate * 12)
    share_signal = clamp((shares / views * 100) * 25) if views > 0 else 0
    return round(clamp(view_signal * 0.3 + engagement_signal * 0.45 + share_signal * 0.25), 2)
