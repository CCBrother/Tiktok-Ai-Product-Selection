from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any


def parse_product(raw: dict[str, Any]) -> dict[str, Any]:
    product = _product_payload(raw)
    title = product.get("title") or raw.get("title") or "Untitled Product"
    product_id = product.get("product_id") or _stable_id(title)
    return {
        "product_id": str(product_id),
        "title": title,
        "description": product.get("description") or "",
        "category": product.get("category") or "Unknown",
        "brand": product.get("brand") or "Unknown",
        "price": Decimal(str(product.get("price") or 0)),
        "currency": product.get("currency") or "USD",
        "rating": Decimal(str(product.get("rating") or 0)),
        "review_count": int(product.get("review_count") or 0),
        "image_url": product.get("image") or product.get("image_url"),
    }


def parse_shop(raw: dict[str, Any]) -> dict[str, Any] | None:
    shop = _product_payload(raw).get("shop") or raw.get("shop")
    if not shop:
        return None
    shop_name = shop.get("shop_name") or shop.get("name") or "Unknown Shop"
    shop_id = shop.get("id") or shop.get("shop_id") or _stable_id(shop_name)
    return {
        "shop_id": str(shop_id),
        "shop_name": shop_name,
        "followers": int(shop.get("followers") or 0),
        "rating": Decimal(str(shop.get("rating") or 0)),
        "country": shop.get("country") or "US",
    }


def parse_video(raw: dict[str, Any]) -> dict[str, Any] | None:
    video = raw.get("video") or _first_dict(raw.get("network_json", []), {"video_id", "videoId", "aweme_id"})
    if not video:
        return None
    video_id = video.get("video_id") or video.get("videoId") or video.get("aweme_id")
    product_id = video.get("product_id") or _product_payload(raw).get("product_id")
    if not video_id or not product_id:
        return None
    return {
        "video_id": str(video_id),
        "product_id": str(product_id),
        "creator_id": video.get("creator_id") or video.get("creatorId"),
        "views": int(video.get("views") or video.get("view_count") or 0),
        "likes": int(video.get("likes") or video.get("like_count") or 0),
        "comments": int(video.get("comments") or video.get("comment_count") or 0),
        "shares": int(video.get("shares") or video.get("share_count") or 0),
        "publish_time": _parse_time(video.get("publish_time")),
    }


def parse_snapshot(raw: dict[str, Any]) -> dict[str, Any]:
    product = _product_payload(raw)
    product_id = product.get("product_id") or _stable_id(product.get("title") or "unknown")
    price = Decimal(str(product.get("price") or 0))
    sales = int(product.get("sales_count") or product.get("sales") or 0)
    return {
        "product_id": str(product_id),
        "snapshot_time": _parse_time(raw.get("collected_at")) or datetime.now(timezone.utc),
        "sales_count": sales,
        "gmv_estimate": Decimal(str(product.get("estimated_gmv") or (sales * float(price)))),
        "price": price,
        "video_count": int(product.get("video_count") or 0),
        "creator_count": int(product.get("creator_count") or 0),
        "shop_count": int(product.get("shop_count") or 1),
        "engagement_score": Decimal(str(product.get("engagement_score") or 0)),
        "raw_json": raw,
    }


def _product_payload(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("product"):
        return raw["product"]
    if raw.get("payload", {}).get("product"):
        return raw["payload"]["product"]
    return raw


def _stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _first_dict(value: Any, keys: set[str]) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if any(key in value for key in keys):
            return value
        for child in value.values():
            found = _first_dict(child, keys)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = _first_dict(child, keys)
            if found:
                return found
    return None
