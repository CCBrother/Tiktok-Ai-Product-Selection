from __future__ import annotations


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def pct_growth(current: float, previous: float) -> float:
    if previous <= 0:
        return 100.0 if current > 0 else 0.0
    return (current - previous) / previous * 100
