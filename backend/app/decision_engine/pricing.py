from __future__ import annotations

from dataclasses import dataclass


PSYCHOLOGICAL_PRICES = [9.99, 14.99, 19.99, 24.99, 29.99, 34.99, 39.99, 49.99, 59.99, 79.99, 99.99]


@dataclass(frozen=True)
class PricingRecommendation:
    estimated_cost: float
    multiplier: float
    recommended_price_low: float
    recommended_price_main: float
    recommended_price_high: float


def recommend_pricing(price: float, estimated_cost: float, competition_score: float, perceived_value_score: float = 60) -> PricingRecommendation:
    cost = estimated_cost if estimated_cost > 0 else max(price * 0.35, 1)
    if competition_score >= 70:
        multiplier = 4.0
    elif competition_score >= 40:
        multiplier = 3.2
    else:
        multiplier = 2.4

    if perceived_value_score >= 80:
        multiplier += 0.3
    elif perceived_value_score < 45:
        multiplier -= 0.2

    main = _psych_price(cost * multiplier)
    low = _psych_price(max(cost * (multiplier - 0.5), cost * 1.6))
    high = _psych_price(cost * (multiplier + 0.6))
    return PricingRecommendation(
        estimated_cost=round(cost, 2),
        multiplier=round(multiplier, 2),
        recommended_price_low=low,
        recommended_price_main=main,
        recommended_price_high=max(high, main),
    )


def _psych_price(target: float) -> float:
    if target <= PSYCHOLOGICAL_PRICES[0]:
        return PSYCHOLOGICAL_PRICES[0]
    return min(PSYCHOLOGICAL_PRICES, key=lambda price: abs(price - target))
