from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from backend.app.models.ai_score import AIScore
from backend.app.models.creator import Creator
from backend.app.models.product import Product
from backend.app.models.product_snapshot import ProductSnapshot
from backend.app.models.shop import Shop
from backend.app.models.video import Video
from backend.app.services.scoring_service import score_product


CATEGORIES = [
    "Kitchen + Wellness",
    "Beauty Tools",
    "Mobile Accessories",
    "Pet Supplies",
    "Home Utility",
    "Fitness Accessories",
    "Car Accessories",
    "Office + Tech",
]
PRODUCT_NOUNS = ["Blender", "Organizer", "Massager", "Cleaner", "Lamp", "Grip", "Brush", "Bottle", "Rack", "Tool"]
PRODUCT_ADJECTIVES = ["Portable", "Magnetic", "Mini", "Foldable", "Smart", "Reusable", "Cordless", "Silicone", "LED", "Travel"]


def reset_mock_data(db: Session) -> None:
    for model in (AIScore, Video, ProductSnapshot, Creator, Shop, Product):
        db.execute(delete(model))
    db.commit()


def generate_mock_data(db: Session, product_count: int = 1000, days: int = 30, seed: int = 42) -> dict[str, int]:
    random.seed(seed)
    reset_mock_data(db)
    creators = _create_creators(db, 350)
    shops = _create_shops(db, 220)
    products: list[Product] = []
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    for index in range(product_count):
        price = round(random.uniform(8.99, 69.99), 2)
        product = Product(
            product_id=f"mock-product-{index + 1:04d}",
            title=_product_title(index),
            description="Synthetic TikTok Shop US product signal generated for backend testing.",
            category=random.choice(CATEGORIES),
            brand=random.choice(["Generic", "Unbranded", "TrendLab", "ViralHome", "FitDaily"]),
            price=Decimal(str(price)),
            currency="USD",
            rating=Decimal(str(round(random.uniform(3.5, 4.9), 2))),
            review_count=random.randint(0, 4200),
            image_url=f"https://picsum.photos/seed/ai-product-{index + 1}/480/480",
        )
        db.add(product)
        products.append(product)
    db.flush()

    for product in products:
        _create_snapshots(db, product, now, days)
        _create_videos(db, product, creators)

    db.commit()
    for product in products:
        score_product(db, product)
    return {"products": len(products), "snapshots": len(products) * days, "creators": len(creators), "shops": len(shops)}


def _product_title(index: int) -> str:
    return f"{random.choice(PRODUCT_ADJECTIVES)} {random.choice(PRODUCT_ADJECTIVES)} {random.choice(PRODUCT_NOUNS)} #{index + 1}"


def _create_creators(db: Session, count: int) -> list[Creator]:
    creators = [
        Creator(
            creator_id=f"creator-{index + 1:04d}",
            nickname=f"Creator {index + 1}",
            followers=random.randint(1_000, 1_200_000),
            video_count=random.randint(10, 900),
            engagement_rate=Decimal(str(round(random.uniform(1.5, 15), 2))),
        )
        for index in range(count)
    ]
    db.add_all(creators)
    return creators


def _create_shops(db: Session, count: int) -> list[Shop]:
    shops = [
        Shop(
            shop_id=f"shop-{index + 1:04d}",
            shop_name=f"US Trend Shop {index + 1}",
            followers=random.randint(50, 200_000),
            rating=Decimal(str(round(random.uniform(3.7, 4.9), 2))),
            country="US",
        )
        for index in range(count)
    ]
    db.add_all(shops)
    return shops


def _create_snapshots(db: Session, product: Product, now: datetime, days: int) -> None:
    base_sales = random.randint(0, 350)
    daily_growth = random.uniform(-0.02, 0.16)
    video_base = random.randint(1, 40)
    creator_base = random.randint(1, 25)
    shop_base = random.randint(2, 80)
    cost_ratio = random.uniform(0.22, 0.48)
    supplier_availability = random.randint(25, 95)
    moq = random.choice([50, 80, 100, 150, 200, 300, 500])
    lead_time = random.randint(5, 28)

    for day in range(days):
        age_factor = day / max(days - 1, 1)
        noise = random.uniform(0.9, 1.18)
        sales = max(0, int((base_sales + day * random.randint(2, 28)) * ((1 + daily_growth) ** day) * noise))
        videos = max(1, int(video_base + day * random.uniform(0.2, 3.2)))
        creators = max(1, int(creator_base + day * random.uniform(0.1, 1.7)))
        shops = max(1, int(shop_base + day * random.uniform(-0.1, 1.1)))
        engagement = round(random.uniform(4, 18) * (1 + age_factor * random.uniform(-0.2, 0.5)), 2)
        price = float(product.price or 0)
        db.add(
            ProductSnapshot(
                product_id=product.product_id,
                snapshot_time=now - timedelta(days=days - day - 1),
                sales_count=sales,
                gmv_estimate=Decimal(str(round(sales * price, 2))),
                price=product.price,
                video_count=videos,
                creator_count=creators,
                shop_count=shops,
                engagement_score=Decimal(str(engagement)),
                raw_json={
                    "estimated_cost": round(price * cost_ratio, 2),
                    "supplier_availability": supplier_availability,
                    "moq": moq,
                    "lead_time_days": lead_time,
                    "brand_risk": random.randint(5, 55),
                    "patent_risk": random.randint(5, 55),
                    "production_difficulty": random.randint(10, 65),
                    "lifecycle_score": random.randint(45, 92),
                    "source": "synthetic_mock_generator",
                },
            )
        )


def _create_videos(db: Session, product: Product, creators: list[Creator]) -> None:
    for index in range(random.randint(3, 18)):
        views = random.randint(800, 850_000)
        likes = int(views * random.uniform(0.015, 0.12))
        comments = int(views * random.uniform(0.001, 0.018))
        shares = int(views * random.uniform(0.001, 0.025))
        creator = random.choice(creators)
        db.add(
            Video(
                video_id=f"{product.product_id}-video-{index + 1}",
                product_id=product.product_id,
                creator_id=creator.creator_id,
                views=views,
                likes=likes,
                comments=comments,
                shares=shares,
                publish_time=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30)),
            )
        )
