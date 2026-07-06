from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import CrawlerConfig
from .cookies import CookieManager
from .proxy import ProxyManager


class PlaywrightBrowser:
    def __init__(self, config: CrawlerConfig) -> None:
        self.config = config
        self._playwright: Any = None
        self.browser: Any = None
        self.context: Any = None

    async def __aenter__(self) -> "PlaywrightBrowser":
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise SystemExit("Install crawler dependencies first: pip install -e '.[crawler]' && playwright install chromium") from exc

        self._playwright = await async_playwright().start()
        proxy = ProxyManager(
            self.config.proxy_server,
            self.config.proxy_username,
            self.config.proxy_password,
        ).playwright_proxy()
        self.browser = await self._playwright.chromium.launch(headless=self.config.headless, proxy=proxy)

        context_kwargs: dict[str, Any] = {
            "locale": self.config.locale,
            "timezone_id": self.config.timezone_id,
        }
        if self.config.storage_state_path.exists():
            context_kwargs["storage_state"] = str(self.config.storage_state_path)
        self.context = await self.browser.new_context(**context_kwargs)

        cookies = CookieManager(self.config.cookies_path).load()
        if cookies:
            await self.context.add_cookies(cookies)
        return self

    async def new_page(self) -> Any:
        return await self.context.new_page()

    async def persist_session(self) -> None:
        self.config.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        await self.context.storage_state(path=str(self.config.storage_state_path))
        CookieManager(self.config.cookies_path).save(await self.context.cookies())

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.context:
            await self.persist_session()
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

