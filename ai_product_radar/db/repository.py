from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from ai_product_radar.decision import build_decision
from ai_product_radar.io import load_products
from ai_product_radar.models import ProductSignal
from ai_product_radar.scoring import score_product

from .models import AIProductScore, Product, ProductHistory


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


class DatabaseProductRepository(ProductRepository):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def list_products(self, limit: int = 100, category: str | None = None) -> list[dict[str, Any]]:
        with self.session_factory() as session:
            rows = self._latest_rows(session, limit=limit, category=category)
            return [self._serialize(product, history, index + 1) for index, (product, history) in enumerate(rows)]

    def top_products(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.list_products(limit=500)
        return sorted(rows, key=lambda row: row["score"]["ai_score"], reverse=True)[:limit]

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        with self.session_factory() as session:
            product, history = self._get_latest_row(session, product_id)
            if product is None or history is None:
                return None
            return self._serialize(product, history, product.id)

    def ai_scores(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.session_factory() as session:
            stmt = select(AIProductScore, Product).join(
                Product, Product.product_id == AIProductScore.product_id, isouter=True
            ).order_by(AIProductScore.score_time.desc()).limit(limit)
            return [self._score_record(score, product) for score, product in session.execute(stmt).all()]

    def trending(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.list_products(limit=500)
        return sorted(
            rows,
            key=lambda row: (row["score"]["growth_score"], row["score"]["trend_score"], row["score"]["viral_score"]),
            reverse=True,
        )[:limit]

    def blue_ocean(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.list_products(limit=500)
        return sorted(
            rows,
            key=lambda row: (row["score"]["competition_score"], row["score"]["blue_ocean_score"], row["score"]["ai_score"]),
            reverse=True,
        )[:limit]

    def opportunities(self, limit: int = 20) -> list[dict[str, Any]]:
        rows = self.top_products(limit=500)
        return sorted(
            rows,
            key=lambda row: (level_rank(row["decision"]["recommendation_level"]), row["score"]["ai_score"]),
            reverse=True,
        )[:limit]

    def lifecycle(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.list_products(limit=limit)
        return [
            {
                "id": row["id"],
                "product_key": row["product_key"],
                "product_name": row["product_name"],
                "lifecycle_stage": row["score"].get("lifecycle_stage") or infer_lifecycle_stage(row),
                "lifecycle_score": row["score"]["lifecycle_score"],
                "confidence": row["score"].get("lifecycle_confidence", 0) / 100 or lifecycle_confidence(row["score"]["lifecycle_score"]),
            }
            for row in rows
        ]

    def dashboard_summary(self) -> dict[str, Any]:
        rows = self.top_products(limit=500)
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

    def _latest_rows(self, session: Session, limit: int, category: str | None = None) -> list[tuple[Product, ProductHistory]]:
        latest_dates = (
            select(ProductHistory.product_id, func.max(ProductHistory.observed_date).label("observed_date"))
            .group_by(ProductHistory.product_id)
            .subquery()
        )
        stmt = (
            select(Product, ProductHistory)
            .join(ProductHistory, ProductHistory.product_id == Product.id)
            .join(
                latest_dates,
                (latest_dates.c.product_id == ProductHistory.product_id)
                & (latest_dates.c.observed_date == ProductHistory.observed_date),
            )
            .order_by(ProductHistory.ai_score.desc(), Product.last_seen_at.desc())
            .limit(limit)
        )
        if category:
            stmt = stmt.where(func.lower(Product.category) == category.lower())
        return list(session.execute(stmt).all())

    def _get_latest_row(self, session: Session, product_id: str) -> tuple[Product | None, ProductHistory | None]:
        conditions = [Product.product_id == product_id]
        if product_id.isdigit():
            conditions.append(Product.id == int(product_id))
        product = session.scalar(select(Product).where(*conditions[:1])) if len(conditions) == 1 else session.scalar(select(Product).where(conditions[0] | conditions[1]))
        if product is None:
            return None, None
        history = session.scalar(
            select(ProductHistory)
            .where(ProductHistory.product_id == product.id)
            .order_by(ProductHistory.observed_date.desc())
            .limit(1)
        )
        return product, history

    def _serialize(self, product: Product, history: ProductHistory, index: int) -> dict[str, Any]:
        decision_json = history.decision_json or {}
        score = decision_json.get("score") or self._score_from_history(history)
        decision = decision_json.get("decision") or self._decision_from_history(history, score)
        signal = decision_json.get("product_signal") or {}
        product_key = product.product_id
        return {
            "id": product.id or index,
            "product_key": product_key,
            "product_name": product.title or product.product_id,
            "category": product.category or "Unknown",
            "signal_source": signal.get("signal_source", "tiktok_shop_us_public_pages"),
            "gross_margin_pct": round(float(signal.get("gross_margin_pct", 0) or 0), 2),
            "landed_profit_usd": round(float(signal.get("landed_profit_usd", 0) or 0), 2),
            "score": score,
            "decision": decision,
            "observed_date": history.observed_date.isoformat(),
            "raw": signal or {
                "product_name": product.title,
                "category": product.category,
                "price_usd": float(product.price or 0),
                "rating_avg": float(product.rating or 0),
                "rating_count": product.review_count or 0,
            },
        }

    def _score_from_history(self, history: ProductHistory) -> dict[str, Any]:
        score = {
            "growth_score": history.growth_score,
            "trend_score": history.trend_score,
            "competition_score": history.competition_score,
            "profit_score": history.profit_score,
            "review_score": history.review_score,
            "lifecycle_score": history.lifecycle_score,
            "supply_score": history.supply_score,
            "copy_difficulty_score": history.copy_difficulty_score,
            "content_score": history.content_score,
            "viral_score": history.viral_score,
            "risk_score": 0,
            "easy_copy_score": history.copy_difficulty_score,
            "blue_ocean_score": history.competition_score,
            "risk_penalty": 0,
            "weights": history.weights_json or {},
            "ai_score": history.ai_score,
            "explanation": f"AI评分 {history.ai_score}/100，来自 PostgreSQL 最新历史快照。",
            "opportunity_score": history.ai_score,
            "confidence_score": 60,
            "momentum_score": history.growth_score,
            "acceleration_score": 0,
            "decay_score": 0,
            "anomaly_adjustment": 0,
            "lifecycle_stage": "",
            "lifecycle_confidence": 0,
        }
        return score

    def _decision_from_history(self, history: ProductHistory, score: dict[str, Any]) -> dict[str, Any]:
        level = "S" if history.ai_score >= 82 else "A" if history.ai_score >= 72 else "B" if history.ai_score >= 58 else "C"
        return {
            "recommendation_level": level,
            "reasoning": f"{level}级：总分 {history.ai_score}/100。数据库快照生成的推荐。",
            "risk_analysis": "公开页面数据有限，需补充供应链、侵权和履约校验。",
            "suggested_price_min_usd": 0,
            "suggested_price_max_usd": 0,
            "suggested_procurement_cost_usd": 0,
            "explanation_bundle": {
                "gpt_explanation": score.get("explanation", ""),
                "risk_explanation": "公开页面数据有限，风险分析需结合供应链和合规数据复核。",
                "recommendation_text": f"{level}级推荐",
                "pricing_suggestion": "建议接入真实采购成本后再确定价格。",
                "sourcing_suggestion": "建议接入供应商数据丰富 supply_chain。",
                "competition_explanation": "竞争分来自卖家/店铺数量信号。",
                "lifecycle_explanation": "生命周期来自历史快照增长信号。",
                "virality_explanation": "病毒传播分来自互动速度和短视频信号。",
                "summary": f"AI评分 {history.ai_score}/100。",
                "alerts": [],
            },
        }

    def _score_record(self, score: AIProductScore, product: Product | None) -> dict[str, Any]:
        return {
            "id": score.id,
            "product_key": score.product_id,
            "product_name": product.title if product else score.product_id,
            "growth_score": float(score.growth_score or 0),
            "trend_score": float(score.trend_score or 0),
            "competition_score": float(score.competition_score or 0),
            "profit_score": float(score.profit_score or 0),
            "supply_score": float(score.supply_score or 0),
            "copy_score": float(score.copy_score or 0),
            "virality_score": float(score.virality_score or 0),
            "final_score": float(score.final_score or 0),
            "lifecycle_stage": score.lifecycle_stage,
            "recommendation_level": score.recommendation_level,
            "explanation": score.explanation,
        }
