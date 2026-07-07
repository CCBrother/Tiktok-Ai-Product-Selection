from __future__ import annotations


def generate_testing_plan(hooks: list[dict], ugc_style: dict) -> dict:
    return {
        "window": "7 days",
        "days": [
            {"day": 1, "focus": "Test 3 hooks", "action": [hook["text"] for hook in hooks[:3]]},
            {"day": 2, "focus": "Test creator style", "action": [ugc_style["recommended_format"], "Face reaction", "Hands-only demo"]},
            {"day": 3, "focus": "Test price angle", "action": ["value anchor", "bundle angle", "impulse buy angle"]},
            {"day": "4-7", "focus": "Scale winner", "action": ["duplicate best hook", "shoot 3 variations", "increase posting frequency"]},
        ],
        "success_metrics": {
            "hook_hold_rate": "35%+ at 3 seconds",
            "save_share_rate": "4%+",
            "comment_signal": "people ask where to buy or tag friends",
        },
    }
