from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostBreakdown:
    product_cost: float
    packaging_cost: float
    domestic_shipping: float
    sea_freight: float
    us_warehouse_cost: float
    last_mile_shipping: float
    tiktok_fees: float
    advertising_cost: float
    total_cost: float


def calculate_total_cost(
    product_cost: float,
    selling_price: float,
    packaging_cost: float = 0.45,
    domestic_shipping: float = 0.35,
    sea_freight: float = 0.9,
    us_warehouse_cost: float = 0.75,
    last_mile_shipping: float = 3.2,
    tiktok_fee_rate: float = 0.08,
    advertising_cost: float = 1.8,
) -> CostBreakdown:
    tiktok_fees = selling_price * tiktok_fee_rate
    total = product_cost + packaging_cost + domestic_shipping + sea_freight + us_warehouse_cost + last_mile_shipping + tiktok_fees + advertising_cost
    return CostBreakdown(
        product_cost=round(product_cost, 2),
        packaging_cost=round(packaging_cost, 2),
        domestic_shipping=round(domestic_shipping, 2),
        sea_freight=round(sea_freight, 2),
        us_warehouse_cost=round(us_warehouse_cost, 2),
        last_mile_shipping=round(last_mile_shipping, 2),
        tiktok_fees=round(tiktok_fees, 2),
        advertising_cost=round(advertising_cost, 2),
        total_cost=round(total, 2),
    )
