from __future__ import annotations

from backend.app.models.product import Product


def generate_hashtags(product: Product, angles) -> dict[str, list[str]]:
    category = (product.category or "finds").lower().replace("+", "").replace(" ", "")
    title_words = [word.lower().strip("#") for word in product.title.split()[:3]]
    problem_word = angles.customer_pain_points[0].split()[0].lower()
    return {
        "primary": [f"#{category}finds", "#tiktokshopfinds"],
        "secondary": ["#amazonfinds", "#musthaves", "#productreview"],
        "niche": [f"#{problem_word}hack", f"#{''.join(title_words)}", "#lifehack"],
        "trend": ["#founditonTikTok", "#thingsyoudidntknowyouneeded"],
    }
