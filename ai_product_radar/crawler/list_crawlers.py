from __future__ import annotations

from pathlib import Path
from urllib.parse import quote_plus

from .browser import PlaywrightBrowser
from .config import CrawlerConfig
from .events import append_event, make_event
from .network import NetworkInterceptor
from .pagination import PaginationHandler
from .retry import anti_block_retry
from .throttle import RequestThrottle


SEARCH_URL = "https://www.tiktok.com/shop/s/{query}"
TRENDING_URL = "https://www.tiktok.com/shop"


class ProductListCrawler:
    def __init__(self, browser: PlaywrightBrowser, config: CrawlerConfig) -> None:
        self.browser = browser
        self.config = config

    async def crawl_search_terms(self, terms: list[str], output: Path, limit: int = 30) -> int:
        event_count = 0
        for term in terms:
            url = SEARCH_URL.format(query=quote_plus(term))
            cards = await self._collect_cards(url, limit)
            append_event(
                output,
                make_event(
                    event_type="search_page",
                    source="tiktok_shop_us",
                    url=url,
                    payload={"term": term, "result_count": len(cards), "cards": cards},
                    meta={"headless": self.config.headless},
                ),
            )
            event_count += 1
        return event_count

    async def _collect_cards(self, url: str, limit: int) -> list[dict[str, str]]:
        async def operation() -> list[dict[str, str]]:
            page = await self.browser.new_page()
            network = NetworkInterceptor()
            network.attach(page)
            await RequestThrottle(self.config.throttle_min_ms, self.config.throttle_max_ms).wait()
            await page.goto(url, wait_until="domcontentloaded", timeout=self.config.timeout_ms)
            await page.wait_for_timeout(self.config.settle_ms)
            await PaginationHandler().scroll_to_load_more(page, max_scrolls=3)
            cards = await page.locator("[data-e2e*='product'], a[href*='/shop/']").evaluate_all(
                """
                (nodes) => nodes.slice(0, 80).map((node) => ({
                  text: node.innerText || node.textContent || "",
                  href: node.href || node.querySelector("a")?.href || "",
                  html: node.outerHTML?.slice(0, 2500) || ""
                }))
                """
            )
            await page.close()
            return cards[:limit]

        return await anti_block_retry(operation, attempts=self.config.retry_attempts)


class TrendingProductCrawler:
    def __init__(self, browser: PlaywrightBrowser, config: CrawlerConfig) -> None:
        self.browser = browser
        self.config = config

    async def crawl(self, output: Path, limit: int = 40) -> int:
        cards = await ProductListCrawler(self.browser, self.config)._collect_cards(TRENDING_URL, limit)
        append_event(
            output,
            make_event(
                event_type="trending_products",
                source="tiktok_shop_us",
                url=TRENDING_URL,
                payload={"result_count": len(cards), "cards": cards},
                meta={"headless": self.config.headless},
            ),
        )
        return 1

