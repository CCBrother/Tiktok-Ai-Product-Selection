from __future__ import annotations

import hashlib
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "you",
    "your",
    "new",
    "hot",
    "best",
    "sale",
    "tiktok",
    "shop",
}

CATEGORY_KEYWORDS = {
    "Beauty": {"makeup", "brush", "curl", "roller", "skin", "beauty", "cosmetic"},
    "Pet Supplies": {"pet", "dog", "cat", "hair", "paw", "nail"},
    "Kitchen": {"kitchen", "air fryer", "fridge", "coffee", "seal", "food"},
    "Home Utility": {"laundry", "lint", "curtain", "stove", "home", "clean"},
    "Mobile Accessories": {"phone", "cable", "charger", "cooling", "mobile"},
    "Fashion Accessories": {"jewelry", "purse", "bag", "clasp", "fashion"},
}

KNOWN_BRANDS = {
    "apple",
    "samsung",
    "dyson",
    "shark",
    "sony",
    "anker",
    "loreal",
    "maybelline",
    "cerave",
}

POSITIVE_WORDS = {
    "love",
    "great",
    "amazing",
    "perfect",
    "easy",
    "works",
    "useful",
    "fast",
    "good",
    "excellent",
}

NEGATIVE_WORDS = {
    "bad",
    "broken",
    "cheap",
    "slow",
    "return",
    "refund",
    "awful",
    "hard",
    "poor",
    "defective",
}


def text_normalization(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[\u2018\u2019\u201c\u201d]", "'", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_product_data(raw: dict[str, Any]) -> dict[str, Any]:
    title = str(raw.get("title") or raw.get("product_name") or raw.get("name") or "").strip()
    description = str(raw.get("description") or raw.get("desc") or "").strip()
    normalized_title = text_normalization(title)
    return {
        "product_id": str(raw.get("product_id") or raw.get("id") or stable_id(normalized_title)),
        "shop_id": empty_to_none(raw.get("shop_id")),
        "title": title,
        "normalized_title": normalized_title,
        "description": description,
        "category": raw.get("category") or category_mapping(title + " " + description),
        "brand": raw.get("brand") or brand_extraction(title + " " + description),
        "price": to_float(raw.get("price") or raw.get("price_usd")),
        "currency": str(raw.get("currency") or "USD"),
        "rating": to_float(raw.get("rating") or raw.get("rating_avg")),
        "review_count": to_int(raw.get("review_count") or raw.get("rating_count")),
        "raw": raw,
    }


def filter_invalid_data(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid: list[dict[str, Any]] = []
    for product in products:
        title = str(product.get("title") or product.get("product_name") or "").strip()
        price = to_float(product.get("price") or product.get("price_usd"))
        if not title:
            continue
        if price < 0:
            continue
        if product.get("currency") and len(str(product["currency"])) > 8:
            continue
        valid.append(product)
    return valid


def deduplicate_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_key: dict[str, dict[str, Any]] = {}
    for product in products:
        normalized = normalize_product_data(product)
        key = normalized.get("product_id") or duplicate_key(normalized)
        existing = best_by_key.get(key)
        if existing is None or record_quality(normalized) > record_quality(existing):
            best_by_key[key] = normalized
    return list(best_by_key.values())


def merge_product_variants(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for product in products:
        normalized = normalize_product_data(product)
        groups[variant_key(normalized["normalized_title"], normalized.get("brand") or "")].append(normalized)

    merged: list[dict[str, Any]] = []
    for _, variants in groups.items():
        primary = max(variants, key=record_quality).copy()
        prices = [to_float(item.get("price")) for item in variants if to_float(item.get("price")) > 0]
        primary["variants"] = variants
        primary["variant_count"] = len(variants)
        if prices:
            primary["min_price"] = min(prices)
            primary["max_price"] = max(prices)
        merged.append(primary)
    return merged


def compute_sales_delta(current_sales: int | float, previous_sales: int | float) -> float:
    return to_float(current_sales) - to_float(previous_sales)


def compute_gmv(sales: int | float | None = None, price: int | float | None = None, order_count: int | float | None = None) -> float:
    quantity = to_float(sales if sales is not None else order_count)
    return round(quantity * to_float(price), 2)


def build_time_series(snapshots: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for snapshot in snapshots:
        product_id = str(snapshot.get("product_id") or "")
        if product_id:
            grouped[product_id].append(snapshot)

    series: dict[str, list[dict[str, Any]]] = {}
    for product_id, rows in grouped.items():
        rows = sorted(rows, key=lambda row: parse_time(row.get("snapshot_time") or row.get("observed_date")))
        previous_sales = 0.0
        points: list[dict[str, Any]] = []
        for row in rows:
            sales = to_float(row.get("sales") or row.get("sold_count"))
            price = to_float(row.get("price") or row.get("price_usd"))
            point = dict(row)
            point["sales_delta"] = compute_sales_delta(sales, previous_sales)
            point["gmv"] = to_float(row.get("gmv")) or compute_gmv(sales=sales, price=price)
            points.append(point)
            previous_sales = sales
        series[product_id] = points
    return series


def detect_anomalies(points: list[dict[str, Any]], z_threshold: float = 3.0) -> list[dict[str, Any]]:
    values = [to_float(point.get("sales_delta") or point.get("sales") or 0) for point in points]
    mean = sum(values) / len(values) if values else 0.0
    std = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)) if values else 0.0
    annotated: list[dict[str, Any]] = []
    for point, value in zip(points, values):
        reasons: list[str] = []
        price = to_float(point.get("price") or point.get("price_usd"))
        if value < 0:
            reasons.append("negative_sales_delta")
        if price < 0:
            reasons.append("negative_price")
        if std > 0 and abs((value - mean) / std) >= z_threshold:
            reasons.append("sales_spike")
        enriched = dict(point)
        enriched["is_anomaly"] = bool(reasons)
        enriched["anomaly_reasons"] = reasons
        annotated.append(enriched)
    return annotated


def image_hash_dedup(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        image_hash = str(item.get("image_hash") or item.get("perceptual_hash") or "").strip()
        if not image_hash:
            unique.append(item)
            continue
        if image_hash in seen:
            continue
        seen.add(image_hash)
        unique.append(item)
    return unique


def category_mapping(text: str) -> str:
    normalized = text_normalization(text)
    scores = {
        category: sum(1 for keyword in keywords if keyword in normalized)
        for category, keywords in CATEGORY_KEYWORDS.items()
    }
    best_category, score = max(scores.items(), key=lambda item: item[1])
    return best_category if score > 0 else "Unknown"


def brand_extraction(text: str) -> str:
    tokens = set(text_normalization(text).split())
    for brand in KNOWN_BRANDS:
        if brand in tokens:
            return brand.title()
    match = re.search(r"\bby\s+([A-Z][A-Za-z0-9& ]{1,32})", text)
    return match.group(1).strip() if match else ""


def supplier_inference(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        product_id = str(record.get("product_id") or record.get("product_key") or "")
        if product_id:
            grouped[product_id].append(record)

    inferred: dict[str, dict[str, Any]] = {}
    for product_id, rows in grouped.items():
        moqs = [to_float(row.get("min_order_quantity") or row.get("avg_moq")) for row in rows if to_float(row.get("min_order_quantity") or row.get("avg_moq")) > 0]
        lead_times = [to_float(row.get("lead_time_days")) for row in rows if to_float(row.get("lead_time_days")) > 0]
        prices = [to_float(row.get("supplier_price") or row.get("avg_price")) for row in rows if to_float(row.get("supplier_price") or row.get("avg_price")) > 0]
        inferred[product_id] = {
            "supplier_count": len(rows),
            "avg_moq": round(sum(moqs) / len(moqs)) if moqs else 0,
            "avg_price": round(sum(prices) / len(prices), 2) if prices else 0,
            "lead_time_days": round(sum(lead_times) / len(lead_times)) if lead_times else 0,
        }
    return inferred


def review_sentiment(reviews: list[str]) -> float:
    if not reviews:
        return 0.0
    score = 0
    total = 0
    for review in reviews:
        tokens = text_normalization(review).split()
        score += sum(1 for token in tokens if token in POSITIVE_WORDS)
        score -= sum(1 for token in tokens if token in NEGATIVE_WORDS)
        total += max(1, len(tokens))
    normalized = 50 + (score / max(1, total)) * 250
    return round(max(0, min(100, normalized)), 2)


def keyword_extraction(text: str, limit: int = 12) -> list[str]:
    tokens = [
        token
        for token in text_normalization(text).split()
        if len(token) >= 3 and token not in STOPWORDS and not token.isdigit()
    ]
    return [token for token, _ in Counter(tokens).most_common(limit)]


def embedding_generation(text: str, dimensions: int = 64) -> list[float]:
    vector = [0.0] * dimensions
    for token in keyword_extraction(text, limit=100):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


def similarity_matching(products: list[dict[str, Any]], threshold: float = 0.82) -> list[tuple[str, str, float]]:
    normalized = [normalize_product_data(product) for product in products]
    embeddings = {
        product["product_id"]: embedding_generation(product["title"] + " " + product.get("description", ""))
        for product in normalized
    }
    matches: list[tuple[str, str, float]] = []
    product_ids = list(embeddings)
    for i, left_id in enumerate(product_ids):
        for right_id in product_ids[i + 1 :]:
            similarity = cosine_similarity(embeddings[left_id], embeddings[right_id])
            if similarity >= threshold:
                matches.append((left_id, right_id, round(similarity, 4)))
    return matches


def product_clustering(products: list[dict[str, Any]], threshold: float = 0.74) -> list[list[str]]:
    normalized = [normalize_product_data(product) for product in products]
    clusters: list[list[str]] = []
    cluster_vectors: list[list[float]] = []
    for product in normalized:
        vector = embedding_generation(product["title"] + " " + product.get("description", ""))
        placed = False
        for index, cluster_vector in enumerate(cluster_vectors):
            if cosine_similarity(vector, cluster_vector) >= threshold:
                clusters[index].append(product["product_id"])
                cluster_vectors[index] = average_vectors([cluster_vectors[index], vector])
                placed = True
                break
        if not placed:
            clusters.append([product["product_id"]])
            cluster_vectors.append(vector)
    return clusters


def lifecycle_detection(series: list[dict[str, Any]]) -> dict[str, Any]:
    if len(series) <= 1:
        return {"stage": "新兴", "confidence": 0.55}
    first = to_float(series[0].get("sales") or series[0].get("sold_count"))
    last = to_float(series[-1].get("sales") or series[-1].get("sold_count"))
    growth = 0 if first <= 0 else (last - first) / first * 100
    recent_delta = to_float(series[-1].get("sales_delta"))
    if growth >= 120 and recent_delta > 0:
        return {"stage": "上升", "confidence": 0.86}
    if growth >= 30 and recent_delta >= 0:
        return {"stage": "高峰", "confidence": 0.72}
    if recent_delta < 0 or growth < -10:
        return {"stage": "下降", "confidence": 0.78}
    return {"stage": "新兴", "confidence": 0.64}


def trend_detection(series: list[dict[str, Any]]) -> dict[str, Any]:
    if len(series) < 2:
        return {"trend": "insufficient_data", "growth_pct": 0.0}
    first = to_float(series[0].get("sales") or series[0].get("sold_count"))
    last = to_float(series[-1].get("sales") or series[-1].get("sold_count"))
    growth_pct = 0.0 if first <= 0 else (last - first) / first * 100
    if growth_pct >= 80:
        trend = "fast_growth"
    elif growth_pct >= 20:
        trend = "rising"
    elif growth_pct <= -15:
        trend = "declining"
    else:
        trend = "flat"
    return {"trend": trend, "growth_pct": round(growth_pct, 2)}


def duplicate_key(product: dict[str, Any]) -> str:
    return stable_id(f"{product.get('brand') or ''}:{product.get('normalized_title') or product.get('title') or ''}")


def variant_key(normalized_title: str, brand: str) -> str:
    value = re.sub(r"\b(red|blue|black|white|green|pink|small|medium|large|xl|xs|pack|set)\b", " ", normalized_title)
    value = re.sub(r"\b\d+\s*(pcs|pieces|oz|ml|cm|inch|in)\b", " ", value)
    return text_normalization(f"{brand} {value}")


def record_quality(product: dict[str, Any]) -> float:
    return sum(
        1
        for field in ["title", "description", "category", "brand", "price", "rating", "review_count", "shop_id"]
        if product.get(field)
    )


def stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def average_vectors(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []
    averaged = [sum(vector[index] for vector in vectors) / len(vectors) for index in range(len(vectors[0]))]
    norm = math.sqrt(sum(value * value for value in averaged)) or 1.0
    return [value / norm for value in averaged]


def parse_time(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.min
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)


def to_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0


def to_int(value: Any) -> int:
    return round(to_float(value))


def empty_to_none(value: Any) -> Any:
    return None if value in (None, "") else value
