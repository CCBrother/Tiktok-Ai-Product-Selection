from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp, score_log


def calculate_review_score(product: ProductSignal) -> int:
    if product.review_sentiment_score:
        return normalize_score(product.review_sentiment_score)
    if product.rating_avg > 0:
        return normalize_score(clamp((product.rating_avg - 3.2) / 1.8 * 100))
    return normalize_score(score_log(product.amazon_review_count, scale=2500) * 0.50)
