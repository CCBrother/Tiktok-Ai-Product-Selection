from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CookieManager:
    def __init__(self, cookies_path: Path) -> None:
        self.cookies_path = cookies_path

    def load(self) -> list[dict[str, Any]]:
        if not self.cookies_path.exists():
            return []
        return json.loads(self.cookies_path.read_text(encoding="utf-8"))

    def save(self, cookies: list[dict[str, Any]]) -> None:
        self.cookies_path.parent.mkdir(parents=True, exist_ok=True)
        self.cookies_path.write_text(json.dumps(cookies, ensure_ascii=False, indent=2), encoding="utf-8")

