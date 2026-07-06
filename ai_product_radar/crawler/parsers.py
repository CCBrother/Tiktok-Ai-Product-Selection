from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_money(value: Any) -> float:
    match = re.search(r"(\d+(?:\.\d+)?)", str(value or "").replace(",", ""))
    return float(match.group(1)) if match else 0.0


def parse_count(value: Any) -> int:
    text = str(value or "").replace(",", "").strip()
    match = re.search(r"(\d+(?:\.\d+)?)([kKmM]?)", text)
    if not match:
        return 0
    amount = float(match.group(1))
    suffix = match.group(2).lower()
    if suffix == "k":
        amount *= 1_000
    elif suffix == "m":
        amount *= 1_000_000
    return int(amount)


def first_value(data: Any, keys: set[str]) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in keys and value not in (None, ""):
                return value
            found = first_value(value, keys)
            if found not in (None, ""):
                return found
    elif isinstance(data, list):
        for item in data:
            found = first_value(item, keys)
            if found not in (None, ""):
                return found
    return None


def load_json_strings(values: list[str]) -> list[Any]:
    loaded: list[Any] = []
    for value in values:
        try:
            loaded.append(json.loads(value))
        except json.JSONDecodeError:
            continue
    return loaded


@dataclass(frozen=True)
class ProductParser:
    def parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        json_candidates = load_json_strings(payload.get("jsonLd", []) or [])
        if payload.get("nextData"):
            json_candidates.extend(load_json_strings([payload["nextData"]]))
        text = compact_text(payload.get("text", ""))
        name = first_value(json_candidates, {"name", "title", "productName"}) or payload.get("title") or ""
        return {
            "product_id": first_value(json_candidates, {"product_id", "productId", "id"}),
            "title": compact_text(str(name)),
            "description": compact_text(str(first_value(json_candidates, {"description"}) or "")),
            "category": first_value(json_candidates, {"category"}),
            "brand": first_value(json_candidates, {"brandName", "brand"}),
            "price": parse_money(first_value(json_candidates, {"price", "salePrice"}) or text),
            "currency": first_value(json_candidates, {"currency", "priceCurrency"}) or "USD",
            "rating": float(first_value(json_candidates, {"ratingValue", "rating"}) or 0),
            "review_count": parse_count(first_value(json_candidates, {"reviewCount", "ratingCount"}) or text),
        }


@dataclass(frozen=True)
class ShopParser:
    def parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = compact_text(payload.get("text", ""))
        return {
            "shop_id": payload.get("shop_id") or payload.get("id"),
            "name": payload.get("title") or first_value(payload, {"name", "shopName"}),
            "follower_count": parse_count(first_value(payload, {"follower_count", "followers"}) or text),
            "rating": float(first_value(payload, {"rating"}) or 0),
            "product_count": parse_count(first_value(payload, {"product_count", "productCount"}) or text),
            "country": first_value(payload, {"country", "region"}),
        }


@dataclass(frozen=True)
class CreatorParser:
    def parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = compact_text(payload.get("text", ""))
        return {
            "creator_id": payload.get("creator_id") or first_value(payload, {"authorId", "creatorId", "id"}),
            "nickname": payload.get("title") or first_value(payload, {"nickname", "uniqueId", "handle"}),
            "follower_count": parse_count(first_value(payload, {"follower_count", "followers"}) or text),
            "total_videos": parse_count(first_value(payload, {"total_videos", "videoCount"}) or text),
            "avg_views": parse_count(first_value(payload, {"avg_views", "avgViews"}) or text),
            "engagement_rate": float(first_value(payload, {"engagement_rate", "engagementRate"}) or 0),
            "country": first_value(payload, {"country", "region"}),
        }


@dataclass(frozen=True)
class VideoParser:
    def parse(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = compact_text(payload.get("text", ""))
        views = parse_count(first_value(payload, {"views", "viewCount", "playCount"}) or text)
        likes = parse_count(first_value(payload, {"likes", "likeCount", "diggCount"}) or 0)
        comments = parse_count(first_value(payload, {"comments", "commentCount"}) or 0)
        shares = parse_count(first_value(payload, {"shares", "shareCount"}) or 0)
        engagement = 0.0 if views <= 0 else round((likes + comments + shares) / views * 100, 2)
        return {
            "video_id": payload.get("video_id") or first_value(payload, {"videoId", "awemeId", "id"}),
            "product_id": first_value(payload, {"productId", "product_id"}),
            "creator_id": first_value(payload, {"creatorId", "authorId", "creator_id"}),
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "publish_time": first_value(payload, {"publish_time", "createTime", "create_time"}),
            "engagement_score": engagement,
        }

