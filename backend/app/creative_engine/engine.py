from __future__ import annotations

from dataclasses import dataclass

from backend.app.creative_engine.angle import CreativeAngles, analyze_angles
from backend.app.creative_engine.evaluator import evaluate_competitor_videos
from backend.app.creative_engine.hashtag import generate_hashtags
from backend.app.creative_engine.hooks import generate_hooks
from backend.app.creative_engine.scripts import generate_script
from backend.app.creative_engine.storyboard import generate_storyboard
from backend.app.creative_engine.testing import generate_testing_plan
from backend.app.creative_engine.ugc_templates import recommend_ugc_style
from backend.app.models.product import Product
from backend.app.models.video import Video


@dataclass(frozen=True)
class CreativeReport:
    product_id: str
    product: str
    recommended_angle: str
    target_audience: str
    hooks: list[dict[str, str]]
    scripts: list[dict]
    storyboard: list[dict]
    hashtags: dict[str, list[str]]
    shooting_plan: dict
    testing_plan: dict
    competitor_analysis: dict
    ai_reasoning: str

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "product": self.product,
            "recommended_angle": self.recommended_angle,
            "target_audience": self.target_audience,
            "hooks": self.hooks,
            "scripts": self.scripts,
            "storyboard": self.storyboard,
            "hashtags": self.hashtags,
            "shooting_plan": self.shooting_plan,
            "testing_plan": self.testing_plan,
            "competitor_analysis": self.competitor_analysis,
            "ai_reasoning": self.ai_reasoning,
        }


def generate_creative_report(product: Product, lifecycle: str | None = None, videos: list[Video] | None = None) -> CreativeReport:
    angles = analyze_angles(product, lifecycle)
    hooks = generate_hooks(product, angles)
    script = generate_script(product, angles, hooks[0]["text"])
    storyboard = generate_storyboard(script)
    ugc_style = recommend_ugc_style(angles, lifecycle)
    hashtags = generate_hashtags(product, angles)
    testing_plan = generate_testing_plan(hooks, ugc_style)
    competitor_analysis = evaluate_competitor_videos(videos or [])
    reasoning = _reasoning(product, angles, lifecycle, ugc_style)
    return CreativeReport(
        product_id=product.product_id,
        product=product.title,
        recommended_angle=angles.primary_selling_angle,
        target_audience=angles.target_audience,
        hooks=hooks,
        scripts=[script],
        storyboard=storyboard,
        hashtags=hashtags,
        shooting_plan={"ugc_style": ugc_style, "angles": _angles_payload(angles), "required_assets": ["phone camera", "natural light", "real demo surface"]},
        testing_plan=testing_plan,
        competitor_analysis=competitor_analysis,
        ai_reasoning=reasoning,
    )


def _angles_payload(angles: CreativeAngles) -> dict:
    return {
        "primary_selling_angle": angles.primary_selling_angle,
        "secondary_selling_angles": angles.secondary_selling_angles,
        "emotional_triggers": angles.emotional_triggers,
        "customer_pain_points": angles.customer_pain_points,
    }


def _reasoning(product: Product, angles: CreativeAngles, lifecycle: str | None, ugc_style: dict) -> str:
    stage_text = f" The lifecycle stage is {lifecycle}, so the plan prioritizes speed and variation." if lifecycle else ""
    return (
        f"{product.title} should lead with '{angles.primary_selling_angle}' because TikTok US shoppers respond to visible problem solving, "
        f"human reaction, and fast demonstration. Recommended format: {ugc_style['recommended_format']}.{stage_text}"
    )
