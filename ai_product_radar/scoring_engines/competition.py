from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp, score_inverse, score_log


def calculate_competition_score(product: ProductSignal) -> int:
    seller_count = product.seller_count or product.shop_competitor_count
    return normalize_score(score_inverse(seller_count, worst=180))


def calculate_blue_ocean_score(product: ProductSignal) -> int:
    seller_count = product.seller_count or product.shop_competitor_count
    low_competition = score_inverse(seller_count, worst=180)
    heat = score_log(product.tiktok_mentions_7d, scale=800)
    mention_growth = clamp(product.mention_growth_pct_7d / 300 * 100)
    mature_elsewhere = score_log(product.amazon_review_count, scale=2500)
    return normalize_score(mention_growth * 0.35 + heat * 0.25 + mature_elsewhere * 0.15 + low_competition * 0.25)
