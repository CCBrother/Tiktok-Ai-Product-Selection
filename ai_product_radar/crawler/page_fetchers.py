from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .browser import PlaywrightBrowser
from .config import CrawlerConfig
from .events import RawEvent, append_event, make_event
from .network import NetworkInterceptor
from .parsers import CreatorParser, ProductParser, ShopParser, VideoParser
from .retry import anti_block_retry
from .throttle import RequestThrottle


PAGE_EVALUATE_SCRIPT = """
() => ({
  title: document.querySelector("h1")?.innerText || document.title || "",
  url: location.href,
  text: document.body?.innerText?.slice(0, 16000) || "",
  jsonLd: Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
    .map((node) => node.textContent)
    .filter(Boolean),
  nextData: document.querySelector("#__NEXT_DATA__")?.textContent || ""
})
"""


@dataclass
class TikTokPageFetcher:
    browser: PlaywrightBrowser
    config: CrawlerConfig

    async def fetch_page(self, url: str, page_type: str) -> RawEvent:
        async def operation() -> RawEvent:
            page = await self.browser.new_page()
            network = NetworkInterceptor()
            network.attach(page)
            await RequestThrottle(self.config.throttle_min_ms, self.config.throttle_max_ms).wait()
            await page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeout_ms)
            await page.wait_for_timeout(self.config.settle_ms)
            payload = await page.evaluate(PAGE_EVALUATE_SCRIPT)
            payload["network_json"] = network.json_payloads()
            payload["parsed"] = parse_page_payload(page_type, payload)
            await page.close()
            return make_event(
                event_type=f"{page_type}_page",
                source="tiktok_shop_us",
                url=url,
                payload=payload,
                meta={"headless": self.config.headless},
            )

        return await anti_block_retry(operation, attempts=self.config.retry_attempts)

    async def fetch_many(self, urls: list[str], page_type: str, output: Path) -> int:
        count = 0
        for url in urls:
            append_event(output, await self.fetch_page(url, page_type))
            count += 1
        return count


def parse_page_payload(page_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if page_type == "product":
        return ProductParser().parse(payload)
    if page_type == "shop":
        return ShopParser().parse(payload)
    if page_type == "creator":
        return CreatorParser().parse(payload)
    if page_type == "video":
        return VideoParser().parse(payload)
    return {}

