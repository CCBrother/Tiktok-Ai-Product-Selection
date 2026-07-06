from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score


def calculate_growth_score(product: ProductSignal) -> int:
    growth_pct = product.sales_growth_pct_7d or product.mention_growth_pct_7d
    return normalize_score(growth_pct / 300 * 100)
