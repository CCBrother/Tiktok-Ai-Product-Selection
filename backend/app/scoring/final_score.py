from __future__ import annotations

from dataclasses import dataclass

from backend.app.utils.math import clamp


@dataclass(frozen=True)
class ScoreResult:
    growth_score: float
    trend_score: float
    competition_score: float
    profit_score: float
    supply_score: float
    copy_score: float
    virality_score: float
    lifecycle_score: float
    final_score: float
    recommendation_level: str
    ai_explanation: str


WEIGHTS = {
    "growth_score": 0.20,
    "trend_score": 0.15,
    "competition_score": 0.15,
    "profit_score": 0.10,
    "supply_score": 0.10,
    "copy_score": 0.10,
    "virality_score": 0.10,
    "lifecycle_score": 0.10,
}


def recommendation_level(score: float) -> str:
    if score >= 90:
        return "S"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    return "C"


def final_score(**scores: float) -> ScoreResult:
    lifecycle = scores.get("lifecycle_score", 60)
    weighted = sum(scores.get(key, 0) * weight for key, weight in WEIGHTS.items())
    total = round(clamp(weighted), 2)
    level = recommendation_level(total)
    return ScoreResult(
        growth_score=round(scores.get("growth_score", 0), 2),
        trend_score=round(scores.get("trend_score", 0), 2),
        competition_score=round(scores.get("competition_score", 0), 2),
        profit_score=round(scores.get("profit_score", 0), 2),
        supply_score=round(scores.get("supply_score", 0), 2),
        copy_score=round(scores.get("copy_score", 0), 2),
        virality_score=round(scores.get("virality_score", 0), 2),
        lifecycle_score=round(lifecycle, 2),
        final_score=total,
        recommendation_level=level,
        ai_explanation=(
            f"{level}级机会，最终分 {total}/100。"
            f"增长 {scores.get('growth_score', 0):.0f}，趋势 {scores.get('trend_score', 0):.0f}，"
            f"竞争 {scores.get('competition_score', 0):.0f}，病毒传播 {scores.get('virality_score', 0):.0f}。"
        ),
    )
