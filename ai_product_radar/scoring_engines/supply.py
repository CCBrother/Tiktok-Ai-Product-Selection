from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import score_inverse, score_log, score_low_one_to_five


def calculate_supply_score(product: ProductSignal, copy_score: int) -> int:
    if product.supplier_count <= 0 and product.min_order_quantity <= 0 and product.lead_time_days <= 0:
        return normalize_score(score_low_one_to_five(product.shipping_complexity) * 0.55 + copy_score * 0.45)
    return normalize_score(
        score_log(product.supplier_count, scale=80) * 0.34
        + score_inverse(product.min_order_quantity, worst=1000) * 0.24
        + score_inverse(product.lead_time_days, worst=45) * 0.24
        + score_low_one_to_five(product.shipping_complexity) * 0.18
    )
