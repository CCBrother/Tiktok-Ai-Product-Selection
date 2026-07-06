from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from ai_product_radar.decision import build_decision
from ai_product_radar.io import load_products
from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import score_product


class ProductRepository:
    def list_products(self, limit: int = 100, category: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def top_products(self, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    def ai_scores(self, limit: int = 100) -> list[dict[str, Any]]:
        raise NotImplementedError

    def trending(self, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    def blue_ocean(self, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    def opportunities(self, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    def lifecycle(self, limit: int = 100) -> list[dict[str, Any]]:
        raise NotImplementedError

    def dashboard_summary(self) -> dict[str, Any]:
        raise NotImplementedError


class CsvProductRepository(ProductRepository):
    def __init__(self, path: Path = Path("data/sample_products.csv")) -> None:
        self.path = path

    def list_products(self, limit: int = 100, category: str | None = None) -> list[dict[str, Any]]:
        products = self._load()
        if category:
            products = [product for product in products if product.category.lower() == category.lower()]
        return [self._serialize(index + 1, product) for index, product in enumerate(products[:limit])]

    def top_products(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = [self._serialize(index + 1, product) for index, product in enumerate(self._load())]
        return sorted(rows, key=lambda row: row["score"]["ai_score"], reverse=True)[:limit]

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        for index, product in enumerate(self._load(), start=1):
            row = self._serialize(index, product)
            if str(row["id"]) == str(product_id) or row["product_key"] == str(product_id):
                return row
        return None

    def ai_scores(self, limit: int = 100) -> list[dict[str, Any]]:
        return [self._score_record(row) for row in self.top_products(limit=limit)]

    def trending(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = [self._serialize(index + 1, product) for index, product in enumerate(self._load())]
        return sorted(
            rows,
            key=lambda row: (row["score"]["growth_score"], row["score"]["trend_score"], row["score"]["viral_score"]),
            reverse=True,
        )[:limit]

    def blue_ocean(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = [self._serialize(index + 1, product) for index, product in enumerate(self._load())]
        return sorted(
            rows,
            key=lambda row: (row["score"]["competition_score"], row["score"]["blue_ocean_score"], row["score"]["ai_score"]),
            reverse=True,
        )[:limit]

    def opportunities(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.top_products(limit=100)
        return sorted(
            rows,
            key=lambda row: (level_rank(row["decision"]["recommendation_level"]), row["score"]["ai_score"]),
            reverse=True,
        )[:limit]

    def lifecycle(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = [self._serialize(index + 1, product) for index, product in enumerate(self._load())][:limit]
        return [
            {
                "id": row["id"],
                "product_key": row["product_key"],
                "product_name": row["product_name"],
                "lifecycle_stage": infer_lifecycle_stage(row),
                "lifecycle_score": row["score"]["lifecycle_score"],
                "confidence": lifecycle_confidence(row["score"]["lifecycle_score"]),
            }
            for row in rows
        ]

    def dashboard_summary(self) -> dict[str, Any]:
        rows = self.top_products(limit=100)
        total = len(rows)
        if total == 0:
            return {"total_products": 0, "average_ai_score": 0, "s_level_count": 0, "top_product": None}
        return {
            "total_products": total,
            "average_ai_score": round(sum(row["score"]["ai_score"] for row in rows) / total, 2),
            "s_level_count": sum(1 for row in rows if row["decision"]["recommendation_level"] == "S"),
            "top_product": rows[0],
            "top_growth_score": max(row["score"]["growth_score"] for row in rows),
            "top_virality_score": max(row["score"]["viral_score"] for row in rows),
        }

    def _load(self) -> list[ProductSignal]:
        return load_products(self.path)

    def _serialize(self, index: int, product: ProductSignal) -> dict[str, Any]:
        score = score_product(product)
        decision = build_decision(product, score)
        product_key = product.product_name.lower().replace(" ", "-")
        return {
            "id": index,
            "product_key": product_key,
            "product_name": product.product_name,
            "category": product.category,
            "signal_source": product.signal_source,
            "gross_margin_pct": round(product.gross_margin_pct, 2),
            "landed_profit_usd": round(product.landed_profit_usd, 2),
            "score": asdict(score),
            "decision": asdict(decision),
            "observed_date": date.today().isoformat(),
            "raw": asdict(product),
        }

    def _score_record(self, row: dict[str, Any]) -> dict[str, Any]:
        score = row["score"]
        decision = row["decision"]
        return {
            "id": row["id"],
            "product_key": row["product_key"],
            "product_name": row["product_name"],
            "growth_score": score["growth_score"],
            "trend_score": score["trend_score"],
            "competition_score": score["competition_score"],
            "profit_score": score["profit_score"],
            "supply_score": score["supply_score"],
            "copy_score": score["copy_difficulty_score"],
            "virality_score": score["viral_score"],
            "final_score": score["ai_score"],
            "lifecycle_stage": infer_lifecycle_stage(row),
            "recommendation_level": decision["recommendation_level"],
            "explanation": score["explanation"],
        }


def level_rank(level: str) -> int:
    return {"S": 4, "A": 3, "B": 2, "C": 1}.get(level, 0)


def infer_lifecycle_stage(row: dict[str, Any]) -> str:
    raw_stage = row["raw"].get("lifecycle_stage")
    if raw_stage:
        return raw_stage
    score = row["score"]["lifecycle_score"]
    if score >= 90:
        return "新兴"
    if score >= 76:
        return "上升"
    if score >= 50:
        return "高峰"
    return "下降"


def lifecycle_confidence(lifecycle_score: int) -> float:
    if lifecycle_score >= 90 or lifecycle_score <= 35:
        return 0.86
    if lifecycle_score >= 76:
        return 0.78
    return 0.66
