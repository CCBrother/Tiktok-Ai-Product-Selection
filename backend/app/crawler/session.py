from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_STORAGE_STATE = Path("storage/session/storage_state.json")


def load_session(path: Path = DEFAULT_STORAGE_STATE) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return {"storage_state": str(path)}


async def save_session(context: Any, path: Path = DEFAULT_STORAGE_STATE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    await context.storage_state(path=str(path))
    return path


async def check_login(page: Any) -> bool:
    url = (getattr(page, "url", "") or "").lower()
    if "login" in url:
        return False
    try:
        text = await page.locator("body").inner_text(timeout=2_000)
    except Exception:
        return True
    lowered = text.lower()
    return "log in" not in lowered and "sign in" not in lowered
