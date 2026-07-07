from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.utils.math import clamp, pct_growth


@dataclass(frozen=True)
class LifecycleMetrics:
    sales_growth_7d: float
    sales_growth_30d: float
    sales_acceleration: float
    sales_velocity_change: float
    creator_growth_rate: float
    video_growth_rate: float
    competition_increase_rate: float
    engagement_growth_rate: float
    engagement_decay: float


@dataclass(frozen=True)
class LifecyclePrediction:
    stage: str
    confidence: int
    metrics: LifecycleMetrics


def predict_lifecycle(history: list[ProductSnapshot]) -> LifecyclePrediction:
    snapshots = sorted(history, key=lambda item: item.snapshot_time)
    if not snapshots:
        return LifecyclePrediction("DEAD", 50, _empty_metrics())

    latest = snapshots[-1]
    snap_7 = _nearest(snapshots, latest.snapshot_time - timedelta(days=7))
    snap_14 = _nearest(snapshots, latest.snapshot_time - timedelta(days=14))
    snap_30 = _nearest(snapshots, latest.snapshot_time - timedelta(days=30))

    sales_growth_7d = pct_growth(latest.sales_count, snap_7.sales_count)
    prior_sales_growth = pct_growth(snap_7.sales_count, snap_14.sales_count)
    metrics = LifecycleMetrics(
        sales_growth_7d=round(sales_growth_7d, 2),
        sales_growth_30d=round(pct_growth(latest.sales_count, snap_30.sales_count), 2),
        sales_acceleration=round(sales_growth_7d - prior_sales_growth, 2),
        sales_velocity_change=round((latest.sales_count - snap_7.sales_count) - (snap_7.sales_count - snap_14.sales_count), 2),
        creator_growth_rate=round(pct_growth(latest.creator_count, snap_7.creator_count), 2),
        video_growth_rate=round(pct_growth(latest.video_count, snap_7.video_count), 2),
        competition_increase_rate=round(pct_growth(latest.shop_count, snap_7.shop_count), 2),
        engagement_growth_rate=round(pct_growth(float(latest.engagement_score), float(snap_7.engagement_score)), 2),
        engagement_decay=round(max(0, -pct_growth(float(latest.engagement_score), float(snap_7.engagement_score))), 2),
    )

    stage = _stage_from_metrics(latest, metrics)
    return LifecyclePrediction(stage, _confidence(stage, latest, metrics), metrics)


def lifecycle_score(stage: str) -> float:
    return {
        "NEW": 78,
        "RISING": 88,
        "HOT": 92,
        "PEAK": 62,
        "DECLINING": 35,
        "DEAD": 10,
    }.get(stage, 60)


def _stage_from_metrics(latest: ProductSnapshot, metrics: LifecycleMetrics) -> str:
    if metrics.sales_growth_30d <= -30 and latest.creator_count <= 2:
        return "DEAD"
    if metrics.sales_growth_7d < 0 and metrics.engagement_growth_rate < 0:
        return "DECLINING"
    if metrics.sales_acceleration < 0 and metrics.competition_increase_rate >= 25:
        return "PEAK"
    if (metrics.sales_acceleration > 0 or metrics.sales_velocity_change > 0) and metrics.creator_growth_rate > 10 and (latest.shop_count < 60 or metrics.competition_increase_rate < 30):
        return "RISING"
    if latest.sales_count >= 800 and float(latest.engagement_score) >= 75 and metrics.creator_growth_rate >= 20:
        return "HOT"
    if latest.sales_count < 150 and (metrics.sales_growth_7d > 30 or metrics.creator_growth_rate > 20 or metrics.video_growth_rate > 20):
        return "NEW"
    return "HOT" if latest.sales_count >= 500 else "RISING"


def _confidence(stage: str, latest: ProductSnapshot, metrics: LifecycleMetrics) -> int:
    evidence = 55
    if abs(metrics.sales_growth_7d) > 30:
        evidence += 10
    if abs(metrics.sales_acceleration) > 25:
        evidence += 10
    if abs(metrics.sales_velocity_change) > 10:
        evidence += 8
    if abs(metrics.creator_growth_rate) > 15:
        evidence += 8
    if abs(metrics.video_growth_rate) > 15:
        evidence += 6
    if abs(metrics.competition_increase_rate) > 20:
        evidence += 6
    if stage in {"HOT", "PEAK"} and latest.sales_count >= 500:
        evidence += 5
    return round(clamp(evidence, 45, 95))


def _nearest(snapshots: list[ProductSnapshot], target) -> ProductSnapshot:
    return min(snapshots, key=lambda item: abs(item.snapshot_time - target))


def _empty_metrics() -> LifecycleMetrics:
    return LifecycleMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
