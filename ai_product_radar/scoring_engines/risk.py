from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import score_one_to_five


def calculate_risk_score(product: ProductSignal, decay_score: int) -> int:
    saturation = 100 if (product.seller_count or product.shop_competitor_count) >= 180 else 0
    return normalize_score(
        score_one_to_five(product.compliance_risk) * 0.34
        + score_one_to_five(product.shipping_complexity) * 0.16
        + score_one_to_five(product.copy_difficulty) * 0.16
        + saturation * 0.16
        + decay_score * 0.18
    )


def calculate_risk_penalty(product: ProductSignal) -> int:
    return normalize_score(
        score_one_to_five(product.compliance_risk) * 0.60
        + score_one_to_five(product.shipping_complexity) * 0.20
        + score_one_to_five(product.copy_difficulty) * 0.20
    )
