from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp, score_log


def calculate_trend_score(product: ProductSignal) -> int:
    heat = score_log(product.tiktok_mentions_7d, scale=800)
    mention_growth = clamp(product.mention_growth_pct_7d / 300 * 100)
    creator_spread = score_log(product.creator_count_7d, scale=80)
    engagement = clamp(product.avg_video_engagement_pct / 12 * 100)
    return normalize_score(creator_spread * 0.42 + heat * 0.28 + mention_growth * 0.18 + engagement * 0.12)
