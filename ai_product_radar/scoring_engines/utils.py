from __future__ import annotations

import math


def clamp(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def score_log(value: float, scale: float, cap: float = 100) -> float:
    if value <= 0:
        return 0
    return clamp(math.log1p(value) / math.log1p(scale) * cap)


def score_inverse(value: float, worst: float) -> float:
    return clamp((1 - min(value, worst) / worst) * 100)


def score_one_to_five(value: float) -> float:
    return clamp((value - 1) / 4 * 100)


def score_low_one_to_five(value: float) -> float:
    return clamp((5 - value) / 4 * 100)
