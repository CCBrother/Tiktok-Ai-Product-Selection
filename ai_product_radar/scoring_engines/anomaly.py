from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score


def calculate_anomaly_adjustment(product: ProductSignal) -> int:
    adjustment = 0
    if product.mention_growth_pct_7d >= 500 and product.creator_count_7d < 5:
        adjustment -= 10
    if product.avg_video_engagement_pct >= 18 and product.tiktok_mentions_7d < 20:
        adjustment -= 6
    if product.seller_count >= 180 or product.shop_competitor_count >= 180:
        adjustment -= 5
    if product.review_sentiment_score and product.review_sentiment_score < 25:
        adjustment -= 8
    return adjustment


def apply_anomaly_adjustment(score: int, adjustment: int) -> int:
    return normalize_score(score + adjustment)
