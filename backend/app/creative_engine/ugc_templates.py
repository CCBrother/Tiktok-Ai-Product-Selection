from __future__ import annotations

from backend.app.creative_engine.angle import CreativeAngles


def recommend_ugc_style(angles: CreativeAngles, lifecycle: str | None = None) -> dict:
    if lifecycle == "RISING":
        return {
            "recommended_format": "POV + Before After",
            "reason": "Rising products need fast comprehension and visible transformation before competitors crowd the feed.",
            "alternatives": ["Problem Solution", "Review reaction", "Comparison"],
        }
    return {
        "recommended_format": "Problem Solution + Review reaction",
        "reason": f"The angle '{angles.primary_selling_angle}' benefits from human reaction and quick proof.",
        "alternatives": ["Unboxing", "Day in my life", "Before / After"],
    }
