from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class JsonResponseExtractor:
    responses: list[dict[str, Any]] = field(default_factory=list)

    async def capture_response(self, response: Any) -> None:
        content_type = response.headers.get("content-type", "")
        url = response.url
        if "json" not in content_type and "api" not in url and "shop" not in url:
            return
        try:
            payload = await response.json()
        except Exception:
            return
        self.responses.append({"url": url, "status": response.status, "json": payload})


class NetworkInterceptor:
    def __init__(self) -> None:
        self.extractor = JsonResponseExtractor()

    def attach(self, page: Any) -> None:
        page.on("response", lambda response: self.extractor.capture_response(response))

    def json_payloads(self) -> list[dict[str, Any]]:
        return self.extractor.responses

