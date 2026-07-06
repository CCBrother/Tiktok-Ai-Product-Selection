from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CrawlerConfig:
    headless: bool = True
    locale: str = "en-US"
    timezone_id: str = "America/Los_Angeles"
    timeout_ms: int = 60_000
    settle_ms: int = 2_500
    throttle_min_ms: int = 900
    throttle_max_ms: int = 2_400
    retry_attempts: int = 3
    storage_state_path: Path = Path("sessions/tiktok_shop_us.json")
    cookies_path: Path = Path("sessions/tiktok_shop_us_cookies.json")
    proxy_server: str | None = None
    proxy_username: str | None = None
    proxy_password: str | None = None

