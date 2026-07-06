from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import score_low_one_to_five


def calculate_copy_score(product: ProductSignal) -> int:
    return normalize_score(
        score_low_one_to_five(product.compliance_risk) * 0.55
        + score_low_one_to_five(product.copy_difficulty) * 0.30
        + score_low_one_to_five(product.shipping_complexity) * 0.15
    )
