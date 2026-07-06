from __future__ import annotations

import math

from .models import ProductSignal


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_log(value: float, scale: float) -> float:
    if value <= 0:
        return 0
    return clamp(math.log1p(value) / math.log1p(scale) * 100)


def score_inverse(value: float, worst: float) -> float:
    return clamp((1 - min(value, worst) / worst) * 100)


def score_low_one_to_five(value: float) -> float:
    return clamp((5 - value) / 4 * 100)


def calculate_supply_score(product: ProductSignal) -> int:
    """Supply Model: supplier availability, price stability, MOQ, lead time, shipping cost."""
    supplier_count = score_log(product.supplier_count, scale=80)
    avg_price_stability = product.avg_price_stability or score_low_one_to_five(product.shipping_complexity)
    moq_feasibility = product.moq_feasibility or score_inverse(product.min_order_quantity, worst=1000)
    lead_time_speed = product.lead_time_speed or score_inverse(product.lead_time_days, worst=45)
    shipping_cost_estimation = product.shipping_cost_estimation or score_low_one_to_five(product.shipping_complexity)

    return round(
        supplier_count * 0.3
        + clamp(avg_price_stability) * 0.2
        + clamp(moq_feasibility) * 0.2
        + clamp(lead_time_speed) * 0.2
        + clamp(shipping_cost_estimation) * 0.1
    )
