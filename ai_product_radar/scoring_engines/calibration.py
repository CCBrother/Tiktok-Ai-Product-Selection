from __future__ import annotations

from .normalization import normalize_score


def calibrate_score(score: int, midpoint: float = 50, slope: float = 0.92) -> int:
    """Pull extreme scores slightly toward the midpoint to reduce overconfidence."""
    return normalize_score(midpoint + (score - midpoint) * slope)
