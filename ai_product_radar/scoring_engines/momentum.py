from __future__ import annotations

from dataclasses import dataclass

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import score_log


@dataclass(frozen=True)
class MomentumSignals:
    momentum_score: int
    acceleration_score: int
    decay_score: int


def detect_momentum(product: ProductSignal) -> int:
    return normalize_score(
        min(product.mention_growth_pct_7d, 400) / 400 * 55
        + score_log(product.creator_count_7d, scale=80) * 0.25
        + score_log(product.tiktok_mentions_7d, scale=800) * 0.20
    )


def detect_acceleration(product: ProductSignal) -> int:
    sales_growth = product.sales_growth_pct_7d or product.mention_growth_pct_7d
    spread_gap = max(0.0, product.mention_growth_pct_7d - sales_growth)
    return normalize_score(min(spread_gap, 250) / 250 * 50 + score_log(product.creator_count_7d, scale=80) * 0.50)


def detect_decay(product: ProductSignal) -> int:
    if product.mention_growth_pct_7d >= 0 and (product.sales_growth_pct_7d >= 0 or product.sales_growth_pct_7d == 0):
        if product.days_since_first_seen <= 120:
            return 0
    age_pressure = max(0.0, product.days_since_first_seen - 120) / 180 * 60
    engagement_pressure = max(0.0, 4 - product.avg_video_engagement_pct) / 4 * 40
    return normalize_score(age_pressure + engagement_pressure)


def detect_momentum_signals(product: ProductSignal) -> MomentumSignals:
    return MomentumSignals(
        momentum_score=detect_momentum(product),
        acceleration_score=detect_acceleration(product),
        decay_score=detect_decay(product),
    )
