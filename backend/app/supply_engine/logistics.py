from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogisticsOption:
    shipping_method: str
    origin: str
    destination: str
    cost_per_unit: float
    shipping_days: int


def default_logistics_options(origin: str = "China", destination: str = "US") -> list[LogisticsOption]:
    return [
        LogisticsOption("air express", origin, destination, 4.2, 7),
        LogisticsOption("air freight", origin, destination, 2.4, 12),
        LogisticsOption("sea freight", origin, destination, 0.9, 28),
    ]


def choose_logistics(price: float, urgency: str = "test") -> LogisticsOption:
    options = default_logistics_options()
    if urgency == "launch" or price >= 35:
        return options[1]
    return options[0] if price < 15 else options[2]
