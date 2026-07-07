from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.crawler.base import JsonResponseCapture, retry_async, save_raw_json
from backend.app.crawler.browser import BrowserManager, BrowserSettings
from backend.app.crawler.parser import extract_meta_image, extract_page_text
from backend.app.crawler.tiktok_shop import category_url, product_search_url


PAGE_SNAPSHOT_SCRIPT = """
() => ({
  url: location.href,
  title: document.title,
  html: document.documentElement.outerHTML,
  text: document.body?.innerText || "",
  jsonLd: Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map((node) => node.textContent).filter(Boolean),
  nextData: document.querySelector("#__NEXT_DATA__")?.textContent || ""
})
"""


class TikTokProductCrawler:
    def __init__(self, settings: BrowserSettings | None = None, raw_root: Path = Path("storage/raw")) -> None:
        self.settings = settings or BrowserSettings()
        self.raw_root = raw_root

    async def crawl_product(self, url: str) -> dict[str, Any]:
        async with BrowserManager(self.settings) as browser:
            return await self._crawl_product_with_browser(browser, url)

    async def crawl_product_list(self, keyword: str) -> list[dict[str, Any]]:
        return await self._crawl_listing(product_search_url(keyword), task=f"search:{keyword}")

    async def crawl_category(self, category: str) -> list[dict[str, Any]]:
        return await self._crawl_listing(category_url(category), task=f"category:{category}")

    async def _crawl_listing(self, url: str, task: str) -> list[dict[str, Any]]:
        async with BrowserManager(self.settings) as browser:
            page = await browser.create_page()
            capture = JsonResponseCapture()
            capture.attach(page)
            await page.goto(url, wait_until="domcontentloaded", timeout=self.settings.timeout_ms)
            await page.wait_for_timeout(2500)
            snapshot = await page.evaluate(PAGE_SNAPSHOT_SCRIPT)
            links = _extract_product_links(snapshot.get("html", ""))
            raw = {
                "task": task,
                "url": url,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "page": snapshot,
                "network_json": capture.as_dicts(),
                "product_urls": links,
            }
            save_raw_json(raw, "product_list", task, root=self.raw_root)
            return [await self._crawl_product_with_browser(browser, link) for link in links[: self._max_products()]]

    async def _crawl_product_with_browser(self, browser: BrowserManager, url: str) -> dict[str, Any]:
        async def operation() -> dict[str, Any]:
            page = await browser.create_page()
            capture = JsonResponseCapture()
            capture.attach(page)
            await page.goto(url, wait_until="domcontentloaded", timeout=self.settings.timeout_ms)
            await page.wait_for_timeout(2500)
            snapshot = await page.evaluate(PAGE_SNAPSHOT_SCRIPT)
            html = snapshot.get("html", "")
            raw = {
                "url": url,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "page": snapshot,
                "network_json": capture.as_dicts(),
                "product": _extract_product_hint(snapshot, html),
            }
            save_raw_json(raw, "product", raw["product"].get("product_id") or url, root=self.raw_root)
            await page.close()
            return raw

        return await retry_async(operation, attempts=3)

    def _max_products(self) -> int:
        return 30


async def crawl_product(url: str) -> dict[str, Any]:
    return await TikTokProductCrawler().crawl_product(url)


async def crawl_product_list(keyword: str) -> list[dict[str, Any]]:
    return await TikTokProductCrawler().crawl_product_list(keyword)


async def crawl_category(category: str) -> list[dict[str, Any]]:
    return await TikTokProductCrawler().crawl_category(category)


def _extract_product_links(html: str) -> list[str]:
    links = re.findall(r"https://www\.tiktok\.com/shop/[^\"]+", html or "")
    product_links = []
    for link in links:
        if "/shop/" in link and link not in product_links:
            product_links.append(link.split("?")[0])
    return product_links


def _extract_product_hint(snapshot: dict[str, Any], html: str) -> dict[str, Any]:
    text = snapshot.get("text") or extract_page_text(html)
    title = _clean_title(snapshot.get("title") or "")
    product_id = _first_match(snapshot.get("url", ""), [r"/product/(\d+)", r"product_id=(\w+)"]) or _slug_id(title)
    price = _parse_money(text)
    sales = _parse_count(_first_match(text, [r"([\d,.]+[KkMm]?)\s+sold", r"Sold\s+([\d,.]+[KkMm]?)"]))
    rating = _parse_float(_first_match(text, [r"([0-5]\.\d)\s*(?:/5|stars?)"]))
    review_count = _parse_count(_first_match(text, [r"([\d,.]+[KkMm]?)\s+reviews?"]))
    return {
        "product_id": product_id,
        "title": title,
        "description": text[:800],
        "price": price,
        "currency": "USD",
        "image": extract_meta_image(html),
        "rating": rating,
        "review_count": review_count,
        "sales_count": sales,
        "estimated_gmv": round(sales * price, 2),
        "video_count": _parse_count(_first_match(text, [r"([\d,.]+[KkMm]?)\s+videos?"])),
        "creator_count": _parse_count(_first_match(text, [r"([\d,.]+[KkMm]?)\s+creators?"])),
        "shop": {
            "id": _first_match(text, [r"Shop ID[:\s]+([\w-]+)"]),
            "shop_name": _first_match(text, [r"Sold by\s+(.{2,80})"]) or "",
            "followers": _parse_count(_first_match(text, [r"([\d,.]+[KkMm]?)\s+followers?"])),
        },
    }


def _clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").replace("| TikTok", "")).strip()[:255]


def _slug_id(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "unknown-product"


def _first_match(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text or "", re.I)
        if match:
            return match.group(1).strip()
    return None


def _parse_money(text: str | None) -> float:
    match = re.search(r"\$?\s*(\d+(?:\.\d+)?)", text or "")
    return float(match.group(1)) if match else 0.0


def _parse_float(text: str | None) -> float:
    try:
        return float(text or 0)
    except ValueError:
        return 0.0


def _parse_count(text: str | None) -> int:
    if not text:
        return 0
    cleaned = text.replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)([KkMm]?)", cleaned)
    if not match:
        return 0
    value = float(match.group(1))
    suffix = match.group(2).lower()
    if suffix == "k":
        value *= 1_000
    if suffix == "m":
        value *= 1_000_000
    return int(value)
