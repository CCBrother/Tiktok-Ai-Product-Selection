from __future__ import annotations

from typing import Any


class PaginationHandler:
    async def next_url(self, page: Any) -> str | None:
        href = await page.locator("a[rel='next'], a:has-text('Next')").first.get_attribute("href")
        if not href:
            return None
        if href.startswith("http"):
            return href
        return await page.evaluate("(href) => new URL(href, location.href).toString()", href)

    async def scroll_to_load_more(self, page: Any, max_scrolls: int = 6) -> None:
        for _ in range(max_scrolls):
            await page.mouse.wheel(0, 1600)
            await page.wait_for_timeout(900)

