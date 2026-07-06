from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import score_log


def calculate_confidence_score(product: ProductSignal, lifecycle_confidence: int) -> int:
    observed_sources = 0
    observed_sources += 1 if product.tiktok_mentions_7d > 0 else 0
    observed_sources += 1 if product.creator_count_7d > 0 else 0
    observed_sources += 1 if product.rating_count > 0 or product.amazon_review_count > 0 else 0
    observed_sources += 1 if product.supplier_count > 0 else 0
    source_score = observed_sources / 4 * 100
    volume_score = score_log(product.tiktok_mentions_7d + product.rating_count + product.amazon_review_count, scale=6000)
    return normalize_score(source_score * 0.45 + volume_score * 0.35 + lifecycle_confidence * 0.20)
