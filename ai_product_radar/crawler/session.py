from __future__ import annotations

from .config import CrawlerConfig


class TikTokLoginSessionManager:
    def __init__(self, config: CrawlerConfig) -> None:
        self.config = config

    def has_persisted_session(self) -> bool:
        return self.config.storage_state_path.exists() or self.config.cookies_path.exists()

    async def ensure_login_session(self, page: object, login_url: str = "https://www.tiktok.com/login") -> None:
        if self.has_persisted_session():
            return
        await page.goto(login_url, wait_until="domcontentloaded", timeout=self.config.timeout_ms)
        print("Login in the opened browser, then press Enter here to persist the session.")
        input()

