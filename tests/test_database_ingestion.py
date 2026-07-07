from __future__ import annotations

from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_product_radar.crawler.events import make_event
from ai_product_radar.db.ingestion import ingest_raw_events
from ai_product_radar.db.models import Base, Product, ProductHistory, ProductSnapshot
from ai_product_radar.db.repository import DatabaseProductRepository


def make_session_factory():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def test_ingest_raw_events_persists_snapshots_history_and_scores():
    session_factory = make_session_factory()
    event = make_event(
        event_type="product_snapshot",
        source="unit_public_tiktok_shop",
        url="https://www.tiktok.com/shop/search?q=pet",
        payload={
            "product_name": "Public Test Pet Brush",
            "shop_name": "Pet Finds",
            "category": "Pet Supplies",
            "price_usd": 18.99,
            "sold_count": 1200,
            "rating_avg": 4.7,
            "rating_count": 360,
            "video_mentions": 84,
            "seller_count": 9,
            "sales_growth_pct_7d": 140,
            "supplier_count": 12,
            "min_order_quantity": 80,
            "lead_time_days": 6,
            "content_creation_ease": 5,
            "interaction_velocity": 42,
        },
    )

    with session_factory() as session:
        stats = ingest_raw_events([event], session, observed_date=date(2026, 7, 6))

        assert stats["raw_events"] == 1
        assert stats["products"] == 1
        assert session.query(Product).count() == 1
        assert session.query(ProductSnapshot).count() == 1
        assert session.query(ProductHistory).count() == 1

    repository = DatabaseProductRepository(session_factory)
    products = repository.top_products(limit=5)

    assert len(products) == 1
    assert products[0]["product_name"] == "Public Test Pet Brush"
    assert products[0]["score"]["ai_score"] >= 0
    assert products[0]["decision"]["recommendation_level"] in {"S", "A", "B", "C"}


def test_database_repository_returns_lifecycle_and_summary():
    session_factory = make_session_factory()
    event = make_event(
        event_type="product_snapshot",
        source="unit_public_tiktok_shop",
        url="https://www.tiktok.com/shop/search?q=kitchen",
        payload={
            "product_name": "Public Test Kitchen Clip",
            "category": "Kitchen",
            "price_usd": 12.99,
            "sold_count": 500,
            "rating_avg": 4.4,
            "rating_count": 120,
            "video_mentions": 50,
            "seller_count": 6,
            "sales_growth_pct_7d": 90,
        },
    )
    with session_factory() as session:
        ingest_raw_events([event], session, observed_date=date(2026, 7, 6))

    repository = DatabaseProductRepository(session_factory)

    assert repository.dashboard_summary()["total_products"] == 1
    assert repository.lifecycle(limit=10)[0]["product_name"] == "Public Test Kitchen Clip"
