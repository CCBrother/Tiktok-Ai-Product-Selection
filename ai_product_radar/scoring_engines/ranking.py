from __future__ import annotations

from ai_product_radar.models import ProductSignal, ScoreBreakdown


ScoredProduct = tuple[ProductSignal, ScoreBreakdown]


def rank_products(scored_products: list[ScoredProduct], field: str = "ai_score", limit: int = 20) -> list[ScoredProduct]:
    return sorted(scored_products, key=lambda item: getattr(item[1], field), reverse=True)[:limit]
