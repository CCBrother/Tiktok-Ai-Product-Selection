from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.app.crawler.session import DEFAULT_STORAGE_STATE, load_session


@dataclass(frozen=True)
class BrowserSettings:
    headless: bool = True
    user_data_dir: Path = Path("storage/session/tiktok_profile")
    storage_state_path: Path = DEFAULT_STORAGE_STATE
    timeout_ms: int = 30_000


class BrowserManager:
    def __init__(self, settings: BrowserSettings | None = None) -> None:
        self.settings = settings or BrowserSettings()
        self._playwright: Any = None
        self.browser: Any = None
        self.context: Any = None

    async def __aenter__(self) -> "BrowserManager":
        await self.create_browser()
        await self.create_context()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def create_browser(self) -> Any:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise SystemExit("Install crawler deps: pip install -e . && playwright install chromium") from exc
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=self.settings.headless)
        return self.browser

    async def create_context(self) -> Any:
        assert self.browser is not None
        session = load_session(self.settings.storage_state_path)
        kwargs = {
            "locale": "en-US",
            "timezone_id": "America/Los_Angeles",
            "viewport": {"width": 1365, "height": 900},
        }
        if session:
            kwargs.update(session)
        self.context = await self.browser.new_context(**kwargs)
        self.context.set_default_timeout(self.settings.timeout_ms)
        return self.context

    async def create_page(self) -> Any:
        assert self.context is not None
        return await self.context.new_page()


async def create_browser(settings: BrowserSettings | None = None) -> BrowserManager:
    manager = BrowserManager(settings)
    await manager.create_browser()
    return manager


async def create_context(manager: BrowserManager) -> Any:
    return await manager.create_context()


async def create_page(manager: BrowserManager) -> Any:
    return await manager.create_page()
