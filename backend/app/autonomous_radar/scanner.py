from __future__ import annotations

from dataclasses import dataclass

from backend.app.autonomous_radar.agent import AgentDecision, decide_candidate
from backend.app.autonomous_radar.opportunity import discover_opportunity
from backend.app.autonomous_radar.ranking import RankedOpportunity, rank_opportunities
from backend.app.models.ai_score import AIScore
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot


@dataclass(frozen=True)
class RadarRunResult:
    scanned_count: int
    filtered_count: int
    deep_analysis_count: int
    recommendations: list[tuple[RankedOpportunity, AgentDecision]]


def scan_market(candidates: list[tuple[Product, AIScore, list[ProductSnapshot]]], limit: int = 20) -> RadarRunResult:
    discovered = [(product, score, discover_opportunity(product, score, history)) for product, score, history in candidates]
    filtered = [item for item in discovered if item[2].opportunity_score >= 45]
    ranked = rank_opportunities(filtered)
    deep = ranked[: min(100, len(ranked))]
    recommendations = [(item, decide_candidate(item)) for item in deep[:limit]]
    return RadarRunResult(
        scanned_count=len(candidates),
        filtered_count=len(filtered),
        deep_analysis_count=len(deep),
        recommendations=recommendations,
    )
