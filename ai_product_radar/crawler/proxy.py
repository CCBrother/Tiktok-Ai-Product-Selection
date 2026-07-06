from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyManager:
    server: str | None = None
    username: str | None = None
    password: str | None = None

    def playwright_proxy(self) -> dict[str, str] | None:
        if not self.server:
            return None
        proxy = {"server": self.server}
        if self.username:
            proxy["username"] = self.username
        if self.password:
            proxy["password"] = self.password
        return proxy

