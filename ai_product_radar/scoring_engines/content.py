from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import score_low_one_to_five, score_one_to_five


def calculate_content_score(product: ProductSignal) -> int:
    visual = score_one_to_five(product.visual_demo_score)
    impulse = score_one_to_five(product.impulse_buy_score)
    problem = score_one_to_five(product.problem_intensity)
    content_ease = score_one_to_five(product.content_creation_ease) if product.content_creation_ease > 0 else visual
    return normalize_score(content_ease * 0.45 + impulse * 0.25 + problem * 0.18 + score_low_one_to_five(product.shipping_complexity) * 0.12)
