from backend.app.scoring.competition import competition_score
from backend.app.scoring.copy import copy_score
from backend.app.scoring.final_score import final_score
from backend.app.scoring.growth import growth_score
from backend.app.scoring.profit import profit_score
from backend.app.scoring.supply import supply_score
from backend.app.scoring.trend import trend_score
from backend.app.scoring.virality import virality_score


def test_backend_scoring_engine_returns_expected_level():
    result = final_score(
        growth_score=growth_score(120, 90, 80),
        trend_score=trend_score(88, 80, 76),
        competition_score=competition_score(1200, 18),
        profit_score=profit_score(29.99, 8.5),
        supply_score=supply_score(90, 100, 7),
        copy_score=copy_score(12, 10, 25),
        virality_score=virality_score(500_000, 45_000, 8_000, 5_000),
        lifecycle_score=82,
    )

    assert 0 <= result.final_score <= 100
    assert result.recommendation_level in {"S", "A", "B", "C"}
    assert result.growth_score > 80
    assert result.ai_explanation
