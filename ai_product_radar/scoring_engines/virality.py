from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp, score_log


def calculate_virality_score(product: ProductSignal) -> int:
    engagement = clamp(product.avg_video_engagement_pct / 12 * 100)
    interaction_velocity = product.interaction_velocity or (product.avg_video_engagement_pct * product.tiktok_mentions_7d / 100)
    return normalize_score(score_log(interaction_velocity, scale=120) * 0.62 + engagement * 0.38)
