from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp, score_inverse, score_log, score_low_one_to_five


def calculate_supply_score(product: ProductSignal, copy_score: int | None = None) -> int:
    supplier_count = score_log(product.supplier_count, scale=80)
    avg_price_stability = product.avg_price_stability
    moq_feasibility = product.moq_feasibility
    lead_time_speed = product.lead_time_speed
    shipping_cost_estimation = product.shipping_cost_estimation

    return normalize_score(
        supplier_count * 0.3
        + clamp(avg_price_stability) * 0.2
        + clamp(moq_feasibility) * 0.2
        + clamp(lead_time_speed) * 0.2
        + clamp(shipping_cost_estimation) * 0.1
    )
