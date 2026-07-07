from __future__ import annotations

from backend.app.creative_engine.angle import CreativeAngles
from backend.app.models.product import Product


def generate_script(product: Product, angles: CreativeAngles, hook: str) -> dict:
    return {
        "duration_seconds": 30,
        "scenes": [
            {
                "scene": 1,
                "time": "0-3 sec",
                "camera": "Handheld close-up",
                "action": "Show the problem immediately before showing the product clearly.",
                "voice": hook,
                "text": "Wait, this actually fixes it?",
            },
            {
                "scene": 2,
                "time": "3-8 sec",
                "camera": "Quick POV shot",
                "action": f"Show the pain point: {angles.customer_pain_points[0]}.",
                "voice": f"This is the part that always made {product.category or 'my routine'} annoying.",
                "text": angles.customer_pain_points[0],
            },
            {
                "scene": 3,
                "time": "8-15 sec",
                "camera": "Over-the-shoulder demo",
                "action": f"Introduce the product as a simple solution for {angles.primary_selling_angle.lower()}.",
                "voice": "So I tested the tiny fix everyone keeps talking about.",
                "text": angles.primary_selling_angle,
            },
            {
                "scene": 4,
                "time": "15-25 sec",
                "camera": "Fast cuts with human reaction",
                "action": "Demonstrate setup, result, and reaction before listing any feature.",
                "voice": "The result is the reason this is getting saved and shared.",
                "text": "Before -> after",
            },
            {
                "scene": 5,
                "time": "25-30 sec",
                "camera": "Face reaction + product in hand",
                "action": "Give one honest verdict and a soft CTA.",
                "voice": "I would test this before it gets crowded.",
                "text": "Would you try this?",
            },
        ],
    }
