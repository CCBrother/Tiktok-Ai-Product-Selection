from __future__ import annotations

from .models import ProductSignal


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def calculate_growth_score(product: ProductSignal) -> int:
    """Growth Model: 0.4 sales 7d + 0.3 sales 30d + 0.3 creator growth."""
    sales_growth_7d = normalize_growth(product.sales_growth_pct_7d or product.mention_growth_pct_7d)
    sales_growth_30d = normalize_growth(product.sales_growth_pct_30d or product.mention_growth_pct_7d)
    creator_growth = normalize_growth(product.creator_growth_pct or product.mention_growth_pct_7d)
    return round(sales_growth_7d * 0.4 + sales_growth_30d * 0.3 + creator_growth * 0.3)


def normalize_growth(value: float) -> float:
    return clamp(value / 300 * 100)
