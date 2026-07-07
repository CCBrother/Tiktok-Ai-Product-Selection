from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp, score_one_to_five


def calculate_copy_score(product: ProductSignal) -> int:
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
    return normalize_score(100 - risk_total)
