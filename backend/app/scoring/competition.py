from __future__ import annotations

import math

from backend.app.utils.math import clamp


def competition_score(sales_count: float, seller_count: float) -> float:
    sales_signal = clamp(math.log1p(max(sales_count, 0)) / math.log1p(5000) * 100)
    seller_pressure = clamp(100 - seller_count * 2.2)
    return round(clamp(sales_signal * 0.45 + seller_pressure * 0.55), 2)
