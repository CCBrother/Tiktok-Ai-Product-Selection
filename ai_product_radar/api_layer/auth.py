from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ai_product_radar.core.config import get_settings


class OptionalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if settings.auth_token and request.url.path != "/health":
            header = request.headers.get("authorization", "")
            if header != f"Bearer {settings.auth_token}":
                from fastapi.responses import JSONResponse

                return JSONResponse(status_code=401, content={"ok": False, "error": "Unauthorized"})
        return await call_next(request)
