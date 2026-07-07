from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.base import Base
from backend.app.models import AIScore, Creator, CrawlerLog, Product, ProductSnapshot, Shop, Video
from backend.app.services.data_pipeline import ingest_product


def test_pipeline_saves_product_snapshot_and_score(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'pipeline.db'}")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    raw = {
        "collected_at": "2026-07-07T00:00:00+00:00",
        "product": {
            "product_id": "p-1",
            "title": "Portable Mini Blender",
            "price": 24.99,
            "rating": 4.7,
            "review_count": 120,
            "sales_count": 950,
            "estimated_gmv": 23740.5,
            "video_count": 42,
            "creator_count": 18,
            "shop_count": 12,
            "shop": {"id": "s-1", "shop_name": "Viral Kitchen", "followers": 12000},
        },
    }

    with SessionLocal() as db:
        result = ingest_product(db, raw)

        assert result["product"].product_id == "p-1"
        assert db.query(Product).count() == 1
        assert db.query(ProductSnapshot).count() == 1
        assert db.query(AIScore).count() == 1
        assert db.query(Shop).count() == 1
        assert db.query(CrawlerLog).count() == 1
