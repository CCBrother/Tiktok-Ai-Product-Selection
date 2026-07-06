from __future__ import annotations

from .models import Decision, ProductSignal, ScoreBreakdown
from .scoring import decide_product


def build_decision(product: ProductSignal, score: ScoreBreakdown | None = None) -> Decision:
    return decide_product(product, score)
