from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .aggregation import NORMALIZED_WEIGHTS, RAW_WEIGHTS
from .scheduler.jobs import JOB_REGISTRY


@dataclass(frozen=True)
class SystemModule:
    group: str
    name: str
    responsibility: str
    entrypoints: list[str]
    status: str = "ready"


MODULES: tuple[SystemModule, ...] = (
    SystemModule(
        group="A",
        name="Crawler Layer",
        responsibility="Playwright collection for TikTok Shop product, shop, creator, video, and trend pages.",
        entrypoints=["ai_product_radar.crawler.tiktok_shop", "python3 -m ai_product_radar crawl"],
    ),
    SystemModule(
        group="B",
        name="Data Pipeline",
        responsibility="Raw JSON normalization, product deduplication, and history timeline generation.",
        entrypoints=["ai_product_radar.pipeline.normalize", "ai_product_radar.pipeline.processing", "python3 -m ai_product_radar normalize"],
    ),
    SystemModule(
        group="C",
        name="Database Layer",
        responsibility="PostgreSQL schema and ORM models for products, snapshots, shops, creators, videos, scores, supply, lifecycle, and competition.",
        entrypoints=["sql/schema.sql", "ai_product_radar.db.models", "python3 -m ai_product_radar.db.init_db"],
    ),
    SystemModule(
        group="D",
        name="AI Scoring Engines",
        responsibility="Growth, supply, copy, trend, competition, profit, virality, lifecycle, content, and risk scoring.",
        entrypoints=["ai_product_radar.scoring", "ai_product_radar.scoring_engines", "ai_product_radar.aggregation"],
    ),
    SystemModule(
        group="E",
        name="API Layer",
        responsibility="FastAPI endpoints for products, rankings, scores, lifecycle, opportunity, and dashboard summary.",
        entrypoints=["ai_product_radar.api", "python3 -m uvicorn ai_product_radar.api:app --reload"],
    ),
    SystemModule(
        group="F",
        name="Next.js Dashboard",
        responsibility="Homepage, product explorer, trend view, score bars, lifecycle badge, and AI report UI.",
        entrypoints=["dashboard/app/page.tsx", "dashboard/components", "pnpm dev"],
    ),
    SystemModule(
        group="G",
        name="Decision and Explanation Layer",
        responsibility="Recommendation level, risk analysis, pricing guidance, sourcing guidance, and narrative AI report text.",
        entrypoints=["ai_product_radar.decision", "ai_product_radar.explanations"],
    ),
    SystemModule(
        group="H",
        name="Scheduler and Operations",
        responsibility="Daily crawler, hourly updates, scoring refresh, report generation, monitoring, and recovery jobs.",
        entrypoints=["ai_product_radar.scheduler.jobs", "python3 -m ai_product_radar jobs"],
    ),
)


def system_overview() -> dict[str, Any]:
    return {
        "name": "AI产品雷达",
        "status": "integrated",
        "module_count": len(MODULES),
        "modules": [asdict(module) for module in MODULES],
        "scoring_weights": {
            "raw": RAW_WEIGHTS,
            "normalized": NORMALIZED_WEIGHTS,
            "normalized_total": round(sum(NORMALIZED_WEIGHTS.values()), 6),
        },
        "registered_jobs": sorted(JOB_REGISTRY.keys()),
        "recommended_local_flow": [
            "python3 -m ai_product_radar crawl --dry-run --output raw_events/tiktok_shop.jsonl",
            "python3 -m ai_product_radar normalize --input raw_events/tiktok_shop.jsonl --output data/normalized_product_facts.csv",
            "python3 -m ai_product_radar timeline --facts data/normalized_product_facts.csv --output data/product_history.csv",
            "python3 -m ai_product_radar report --input data/sample_products.csv",
            "python3 -m uvicorn ai_product_radar.api:app --reload",
            "cd dashboard && pnpm dev",
        ],
    }


def verify_local_artifacts(root: Path = Path(".")) -> dict[str, bool]:
    required = {
        "schema": root / "sql/schema.sql",
        "sample_data": root / "data/sample_products.csv",
        "api": root / "ai_product_radar/api.py",
        "dashboard": root / "dashboard/app/page.tsx",
        "scheduler": root / "ai_product_radar/scheduler/jobs.py",
    }
    return {name: path.exists() for name, path in required.items()}
