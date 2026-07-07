from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarginResult:
    gross_margin: float
    net_margin: float
    roi: float
    unit_profit: float


def calculate_margin(selling_price: float, total_cost: float, supplier_price: float, advertising_cost: float = 0) -> MarginResult:
    if selling_price <= 0:
        return MarginResult(0, 0, 0, 0)
    gross_profit = selling_price - supplier_price
    unit_profit = selling_price - total_cost
    gross_margin = gross_profit / selling_price * 100
    net_margin = unit_profit / selling_price * 100
    roi = unit_profit / max(total_cost, 0.01)
    return MarginResult(round(gross_margin, 2), round(net_margin, 2), round(roi, 2), round(unit_profit, 2))
