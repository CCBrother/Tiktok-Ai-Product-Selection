from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar
from uuid import uuid4

from backend.app.crawler.exceptions import CrawlerError


T = TypeVar("T")


@dataclass
class CapturedResponse:
    url: str
    status: int
    body: Any


@dataclass
class JsonResponseCapture:
    responses: list[CapturedResponse] = field(default_factory=list)

    def attach(self, page: Any) -> None:
        page.on("response", lambda response: asyncio.create_task(self.capture(response)))

    async def capture(self, response: Any) -> None:
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type and "json" not in content_type:
            return
        try:
            body = await response.json()
        except Exception:
            return
        self.responses.append(CapturedResponse(url=response.url, status=response.status, body=body))

    def as_dicts(self) -> list[dict[str, Any]]:
        return [{"url": item.url, "status": item.status, "json": item.body} for item in self.responses]


async def retry_async(operation: Callable[[], Awaitable[T]], attempts: int = 3, delay_s: float = 1.5) -> T:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception as exc:
            last_error = exc
            if attempt < attempts - 1:
                await asyncio.sleep(delay_s * (2**attempt))
    raise CrawlerError(str(last_error)) from last_error


def raw_storage_path(kind: str, identifier: str, root: Path = Path("storage/raw")) -> Path:
    now = datetime.now(timezone.utc)
    safe_identifier = "".join(char if char.isalnum() or char in "-_" else "_" for char in identifier)[:96]
    name = f"{kind}_{safe_identifier}_{now.strftime('%H%M%S')}_{uuid4().hex[:8]}.json"
    return root / f"{now:%Y}" / f"{now:%m}" / f"{now:%d}" / name


def save_raw_json(payload: dict[str, Any], kind: str, identifier: str, root: Path = Path("storage/raw")) -> Path:
    path = raw_storage_path(kind, identifier, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return path
