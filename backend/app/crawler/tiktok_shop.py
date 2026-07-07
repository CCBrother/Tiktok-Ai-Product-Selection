from __future__ import annotations

from urllib.parse import quote_plus


TIKTOK_SHOP_BASE = "https://www.tiktok.com/shop"


def product_search_url(keyword: str) -> str:
    return f"{TIKTOK_SHOP_BASE}/s/{quote_plus(keyword)}"


def category_url(category: str) -> str:
    return f"{TIKTOK_SHOP_BASE}/c/{quote_plus(category)}"
