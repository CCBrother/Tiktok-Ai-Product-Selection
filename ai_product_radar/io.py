from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import ProductSignal


NUMERIC_FIELDS = {
    "tiktok_mentions_7d",
    "mention_growth_pct_7d",
    "creator_count_7d",
    "avg_video_engagement_pct",
    "shop_competitor_count",
    "amazon_review_count",
    "unit_cost_usd",
    "target_price_usd",
    "shipping_complexity",
    "copy_difficulty",
    "problem_intensity",
    "visual_demo_score",
    "impulse_buy_score",
    "compliance_risk",
    "rating_avg",
    "rating_count",
    "days_since_first_seen",
    "supplier_count",
    "inventory_depth",
    "sales_growth_pct_7d",
    "sales_growth_pct_30d",
    "creator_growth_pct",
    "seller_count",
    "review_sentiment_score",
    "min_order_quantity",
    "lead_time_days",
    "avg_price_stability",
    "moq_feasibility",
    "lead_time_speed",
    "shipping_cost_estimation",
    "brand_strength",
    "patent_risk",
    "content_complexity",
    "production_complexity",
    "influencer_dependency",
    "content_creation_ease",
    "interaction_velocity",
}


def load_products(path: Path) -> list[ProductSignal]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_products_csv(path)
    if suffix == ".json":
        return load_products_json(path)
    raise ValueError(f"Unsupported input format: {path.suffix}. Use .csv or .json.")


def load_products_csv(path: Path) -> list[ProductSignal]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    return [row_to_product(row) for row in rows]


def load_products_json(path: Path) -> list[ProductSignal]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JSON input must be a list of product objects.")
    return [row_to_product(row) for row in data]


def row_to_product(row: dict[str, Any]) -> ProductSignal:
    normalized = {key: normalize_value(key, value) for key, value in row.items()}
    missing = [field for field in required_fields() if field not in normalized or normalized[field] == ""]
    if missing:
        name = normalized.get("product_name", "<unknown>")
        raise ValueError(f"{name} is missing required fields: {', '.join(missing)}")

    return ProductSignal(
        product_name=str(normalized["product_name"]),
        category=str(normalized["category"]),
        signal_source=str(normalized["signal_source"]),
        tiktok_mentions_7d=float(normalized["tiktok_mentions_7d"]),
        mention_growth_pct_7d=float(normalized["mention_growth_pct_7d"]),
        creator_count_7d=float(normalized["creator_count_7d"]),
        avg_video_engagement_pct=float(normalized["avg_video_engagement_pct"]),
        shop_competitor_count=float(normalized["shop_competitor_count"]),
        amazon_review_count=float(normalized["amazon_review_count"]),
        unit_cost_usd=float(normalized["unit_cost_usd"]),
        target_price_usd=float(normalized["target_price_usd"]),
        shipping_complexity=float(normalized["shipping_complexity"]),
        copy_difficulty=float(normalized["copy_difficulty"]),
        problem_intensity=float(normalized["problem_intensity"]),
        visual_demo_score=float(normalized["visual_demo_score"]),
        impulse_buy_score=float(normalized["impulse_buy_score"]),
        compliance_risk=float(normalized["compliance_risk"]),
        rating_avg=float(normalized.get("rating_avg", 0.0) or 0.0),
        rating_count=float(normalized.get("rating_count", 0.0) or 0.0),
        days_since_first_seen=float(normalized.get("days_since_first_seen", 0.0) or 0.0),
        supplier_count=float(normalized.get("supplier_count", 0.0) or 0.0),
        inventory_depth=float(normalized.get("inventory_depth", 0.0) or 0.0),
        sales_growth_pct_7d=float(normalized.get("sales_growth_pct_7d", 0.0) or 0.0),
        sales_growth_pct_30d=float(normalized.get("sales_growth_pct_30d", 0.0) or 0.0),
        creator_growth_pct=float(normalized.get("creator_growth_pct", 0.0) or 0.0),
        seller_count=float(normalized.get("seller_count", 0.0) or 0.0),
        review_sentiment_score=float(normalized.get("review_sentiment_score", 0.0) or 0.0),
        lifecycle_stage=str(normalized.get("lifecycle_stage", "") or ""),
        min_order_quantity=float(normalized.get("min_order_quantity", 0.0) or 0.0),
        lead_time_days=float(normalized.get("lead_time_days", 0.0) or 0.0),
        avg_price_stability=float(normalized.get("avg_price_stability", 0.0) or 0.0),
        moq_feasibility=float(normalized.get("moq_feasibility", 0.0) or 0.0),
        lead_time_speed=float(normalized.get("lead_time_speed", 0.0) or 0.0),
        shipping_cost_estimation=float(normalized.get("shipping_cost_estimation", 0.0) or 0.0),
        brand_strength=float(normalized.get("brand_strength", 0.0) or 0.0),
        patent_risk=float(normalized.get("patent_risk", 0.0) or 0.0),
        content_complexity=float(normalized.get("content_complexity", 0.0) or 0.0),
        production_complexity=float(normalized.get("production_complexity", 0.0) or 0.0),
        influencer_dependency=float(normalized.get("influencer_dependency", 0.0) or 0.0),
        content_creation_ease=float(normalized.get("content_creation_ease", 0.0) or 0.0),
        interaction_velocity=float(normalized.get("interaction_velocity", 0.0) or 0.0),
        notes=str(normalized.get("notes", "")),
        raw=dict(row),
    )


def normalize_value(key: str, value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, str):
        value = value.strip()
    if key in NUMERIC_FIELDS:
        if value == "":
            return 0.0
        return float(value)
    return value


def required_fields() -> list[str]:
    return [
        "product_name",
        "category",
        "signal_source",
        "tiktok_mentions_7d",
        "mention_growth_pct_7d",
        "creator_count_7d",
        "avg_video_engagement_pct",
        "shop_competitor_count",
        "amazon_review_count",
        "unit_cost_usd",
        "target_price_usd",
        "shipping_complexity",
        "copy_difficulty",
        "problem_intensity",
        "visual_demo_score",
        "impulse_buy_score",
        "compliance_risk",
    ]
