from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score


def calculate_growth_score(product: ProductSignal) -> int:
    sales_growth_7d = normalize_growth(product.sales_growth_pct_7d or product.mention_growth_pct_7d)
    sales_growth_30d = normalize_growth(product.sales_growth_pct_30d)
    creator_growth = normalize_growth(product.creator_growth_pct)
    return normalize_score(sales_growth_7d * 0.4 + sales_growth_30d * 0.3 + creator_growth * 0.3)


def normalize_growth(value: float) -> float:
    return min(100, max(0, value / 300 * 100))
