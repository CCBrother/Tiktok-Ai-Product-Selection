from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    product_id: str
    title: str
    description: str | None = None
    category: str | None = None
    brand: str | None = None
    price: Decimal | None = None
    currency: str = "USD"
    rating: Decimal | None = None
    review_count: int = 0
    image_url: str | None = None


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    brand: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    rating: Decimal | None = None
    review_count: int | None = None
    image_url: str | None = None


class ProductRead(ProductCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductSnapshotCreate(BaseModel):
    product_id: str
    snapshot_time: datetime
    sales_count: int = 0
    gmv_estimate: Decimal = Decimal("0")
    price: Decimal | None = None
    video_count: int = 0
    creator_count: int = 0
    shop_count: int = 0
    engagement_score: Decimal = Decimal("0")
    raw_json: dict[str, Any] = Field(default_factory=dict)


class ProductSnapshotRead(ProductSnapshotCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AIScoreRead(BaseModel):
    id: int
    product_id: str
    score_time: datetime
    growth_score: Decimal
    trend_score: Decimal
    competition_score: Decimal
    profit_score: Decimal
    supply_score: Decimal
    copy_score: Decimal
    virality_score: Decimal
    lifecycle_score: Decimal
    final_score: Decimal
    recommendation_level: str
    ai_explanation: str

    model_config = ConfigDict(from_attributes=True)


class ProductListItem(BaseModel):
    id: int
    product_id: str
    title: str
    category: str | None
    brand: str | None
    price: Decimal | None
    currency: str
    rating: Decimal | None
    review_count: int
    image_url: str | None
    score: AIScoreRead | None = None


class ProductDetail(ProductListItem):
    description: str | None
    history: list[ProductSnapshotRead]
    scores: list[AIScoreRead]
    recommendation: str | None = None
