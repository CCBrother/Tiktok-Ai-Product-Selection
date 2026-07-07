from __future__ import annotations


def initial_order_quantity(expected_daily_sales: int, lead_time_days: int, safety_stock: int) -> int:
    return max(0, int(expected_daily_sales * lead_time_days + safety_stock))
