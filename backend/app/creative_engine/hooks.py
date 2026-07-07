from __future__ import annotations

from backend.app.creative_engine.angle import CreativeAngles
from backend.app.models.product import Product


HOOK_TYPES = ["problem", "shock", "comparison", "discovery"]


def generate_hooks(product: Product, angles: CreativeAngles) -> list[dict[str, str]]:
    short_name = _short_name(product.title)
    pain = angles.customer_pain_points[0]
    primary = angles.primary_selling_angle.lower()
    raw_hooks = [
        ("problem", f"I didn't realize {pain.lower()} was this fixable..."),
        ("shock", "I didn't expect this tiny thing to work this well..."),
        ("comparison", f"I replaced my expensive setup with this {short_name}..."),
        ("discovery", "TikTok made me try this and now I get it..."),
        ("problem", f"If your routine feels chaotic, watch this {short_name} test."),
        ("shock", "I thought this was a gimmick until the first five seconds."),
        ("comparison", f"Before this: messy. After this: {primary}."),
        ("discovery", "Nobody told me this existed for everyday problems."),
        ("problem", f"This solves the part of {product.category or 'daily life'} that annoys me most."),
        ("shock", "Wait for the result at the end, because I was not ready."),
    ]
    return [{"type": hook_type, "text": text} for hook_type, text in raw_hooks[:10]]


def _short_name(title: str) -> str:
    words = [word for word in title.split() if not word.startswith("#")]
    return " ".join(words[:3]).lower() or "product"
