from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ROIPrediction:
    testing_budget: float
    expected_orders: int
    expected_profit: float
    roi: float
    conversion_rate: float
    estimated_traffic: int


def predict_roi(price: float, cost: float, virality_score: float, final_score: float, traffic: int | None = None) -> ROIPrediction:
    testing_budget = 500 if final_score >= 90 else 300 if final_score >= 80 else 150 if final_score >= 70 else 75
    estimated_traffic = traffic or round(testing_budget * (18 + virality_score / 6))
    conversion_rate = min(0.065, 0.012 + virality_score / 100 * 0.028)
    expected_orders = max(0, round(estimated_traffic * conversion_rate))
    unit_profit = max(price - cost, 0)
    expected_profit = round(expected_orders * unit_profit, 2)
    roi = round(expected_profit / testing_budget, 2) if testing_budget else 0
    return ROIPrediction(
        testing_budget=testing_budget,
        expected_orders=expected_orders,
        expected_profit=expected_profit,
        roi=roi,
        conversion_rate=round(conversion_rate, 4),
        estimated_traffic=estimated_traffic,
    )
