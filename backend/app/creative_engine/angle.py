from __future__ import annotations

from dataclasses import dataclass

from backend.app.models.product import Product


@dataclass(frozen=True)
class CreativeAngles:
    primary_selling_angle: str
    secondary_selling_angles: list[str]
    emotional_triggers: list[str]
    customer_pain_points: list[str]
    target_audience: str


def analyze_angles(product: Product, lifecycle: str | None = None) -> CreativeAngles:
    title = product.title.lower()
    category = (product.category or "daily life").lower()

    if "blender" in title:
        return CreativeAngles(
            primary_selling_angle="Healthy drinks anywhere",
            secondary_selling_angles=["Office fitness hack", "Travel essential", "Five-second smoothie routine"],
            emotional_triggers=["relief", "surprise", "self-improvement"],
            customer_pain_points=["No time for healthy drinks", "Big blender cleanup", "Eating poorly while traveling"],
            target_audience="fitness beginners, office workers, travelers",
        )
    if "lamp" in title or "led" in title:
        return CreativeAngles(
            primary_selling_angle="Instantly fix a dark corner",
            secondary_selling_angles=["Rental-friendly upgrade", "Tiny tool that changes the room", "Night routine helper"],
            emotional_triggers=["satisfaction", "comfort", "before-after surprise"],
            customer_pain_points=["Poor lighting", "Messy cables", "No-drill setup needed"],
            target_audience="renters, desk setup fans, home organizers",
        )
    if "massager" in title:
        return CreativeAngles(
            primary_selling_angle="Relief you can use while doing anything",
            secondary_selling_angles=["Desk pain fix", "After-work recovery", "Giftable self-care find"],
            emotional_triggers=["relief", "curiosity", "comfort"],
            customer_pain_points=["Neck tension", "Long workdays", "Expensive appointments"],
            target_audience="office workers, parents, self-care shoppers",
        )

    return CreativeAngles(
        primary_selling_angle=f"Make {category} feel easier in seconds",
        secondary_selling_angles=["Small problem fix", "Before-after transformation", "Unexpected everyday upgrade"],
        emotional_triggers=["curiosity", "relief", "surprise"],
        customer_pain_points=["Wasting time", "Messy routine", "Buying overcomplicated tools"],
        target_audience=f"TikTok US shoppers interested in {category}",
    )
