from __future__ import annotations

from ai_product_radar.models import ProductSignal

from .normalization import normalize_score
from .utils import clamp


def calculate_profit_score(product: ProductSignal) -> int:
    return normalize_score(clamp(product.gross_margin_pct / 75 * 100))
