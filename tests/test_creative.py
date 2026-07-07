from __future__ import annotations

from decimal import Decimal

from backend.app.creative_engine.angle import analyze_angles
from backend.app.creative_engine.engine import generate_creative_report
from backend.app.creative_engine.hashtag import generate_hashtags
from backend.app.creative_engine.hooks import generate_hooks
from backend.app.creative_engine.scripts import generate_script
from backend.app.creative_engine.storyboard import generate_storyboard
from backend.app.models.product import Product


def make_product(**overrides) -> Product:
    base = dict(
        product_id="creative-1",
        title="Portable Mini Blender",
        category="Kitchen + Wellness",
        price=Decimal("24.99"),
        description="Portable blender for smoothies",
    )
    base.update(overrides)
    return Product(**base)


def test_hook_generation_returns_ten_hooks():
    product = make_product()
    angles = analyze_angles(product, lifecycle="RISING")
    hooks = generate_hooks(product, angles)

    assert len(hooks) == 10
    assert {hook["type"] for hook in hooks} >= {"problem", "shock", "comparison", "discovery"}
    assert all(hook["text"] for hook in hooks)


def test_script_generation_has_30_second_structure():
    product = make_product()
    angles = analyze_angles(product)
    script = generate_script(product, angles, "I didn't expect this to work...")

    assert script["duration_seconds"] == 30
    assert [scene["time"] for scene in script["scenes"]] == ["0-3 sec", "3-8 sec", "8-15 sec", "15-25 sec", "25-30 sec"]
    assert script["scenes"][0]["voice"]


def test_storyboard_generation_uses_script_scenes():
    product = make_product()
    angles = analyze_angles(product)
    script = generate_script(product, angles, "I wish I bought this sooner...")
    storyboard = generate_storyboard(script)

    assert len(storyboard) == 5
    assert storyboard[0]["camera"] == "Handheld close-up"
    assert storyboard[0]["text_overlay"]


def test_hashtag_generation_returns_hashtag_groups():
    product = make_product()
    angles = analyze_angles(product)
    hashtags = generate_hashtags(product, angles)

    assert "#tiktokshopfinds" in hashtags["primary"]
    assert hashtags["niche"]
    assert hashtags["trend"]


def test_creative_report_output_contains_content_plan():
    report = generate_creative_report(make_product(), lifecycle="RISING")
    payload = report.to_dict()

    assert payload["recommended_angle"] == "Healthy drinks anywhere"
    assert len(payload["hooks"]) == 10
    assert payload["scripts"][0]["scenes"][0]["time"] == "0-3 sec"
    assert payload["storyboard"][0]["emotion"]
    assert payload["testing_plan"]["window"] == "7 days"
