from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from backend.app.decision_engine.lifecycle import predict_lifecycle
from backend.app.models.product_snapshot import ProductSnapshot


def make_history(
    sales: list[int],
    creators: list[int],
    videos: list[int],
    shops: list[int],
    engagement: list[float],
) -> list[ProductSnapshot]:
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    return [
        ProductSnapshot(
            product_id="p-1",
            snapshot_time=start + timedelta(days=index),
            sales_count=sales[index],
            creator_count=creators[index],
            video_count=videos[index],
            shop_count=shops[index],
            engagement_score=Decimal(str(engagement[index])),
            raw_json={},
        )
        for index in range(len(sales))
    ]


def test_rising_product_detection():
    history = make_history(
        sales=[20 + i * i for i in range(30)],
        creators=[2 + i for i in range(30)],
        videos=[5 + i * 2 for i in range(30)],
        shops=[8 + i // 8 for i in range(30)],
        engagement=[55 + i * 0.8 for i in range(30)],
    )

    result = predict_lifecycle(history)

    assert result.stage == "RISING"
    assert result.confidence >= 70


def test_peak_product_detection():
    sales = [100 + i * 35 for i in range(15)] + [625 + i * 4 for i in range(15)]
    history = make_history(
        sales=sales,
        creators=[20 + i for i in range(30)],
        videos=[40 + i * 2 for i in range(30)],
        shops=[15 + i * 3 for i in range(30)],
        engagement=[82 - i * 0.3 for i in range(30)],
    )

    result = predict_lifecycle(history)

    assert result.stage == "PEAK"
    assert result.metrics.competition_increase_rate > 25


def test_declining_product_detection():
    history = make_history(
        sales=[600 - i * 12 for i in range(30)],
        creators=[30 - i // 2 for i in range(30)],
        videos=[80 - i for i in range(30)],
        shops=[45 + i for i in range(30)],
        engagement=[78 - i for i in range(30)],
    )

    result = predict_lifecycle(history)

    assert result.stage == "DECLINING"
    assert result.metrics.engagement_decay > 0
