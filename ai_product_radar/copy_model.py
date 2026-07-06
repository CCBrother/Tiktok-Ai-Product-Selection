from __future__ import annotations

from .models import ProductSignal


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_one_to_five(value: float) -> float:
    return clamp((value - 1) / 4 * 100)


def calculate_copy_score(product: ProductSignal) -> int:
    """Copy Model: risk terms reduce copyability."""
    brand_strength = product.brand_strength or score_one_to_five(product.compliance_risk)
    patent_risk = product.patent_risk or score_one_to_five(product.compliance_risk)
    content_complexity = product.content_complexity or score_one_to_five(product.copy_difficulty)
    production_complexity = product.production_complexity or score_one_to_five(product.shipping_complexity)
    influencer_dependency = product.influencer_dependency or score_one_to_five(product.copy_difficulty)

    risk_total = (
        clamp(brand_strength)
        + clamp(patent_risk)
        + clamp(content_complexity)
        + clamp(production_complexity)
        + clamp(influencer_dependency)
    ) / 5
    return round(100 - risk_total)
