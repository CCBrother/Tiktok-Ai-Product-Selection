from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")


async def anti_block_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay_s: float = 1.2,
) -> T:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return await operation()
        except Exception as exc:  # noqa: BLE001 - crawler retries intentionally catch broad page/network failures.
            last_error = exc
            if attempt == attempts - 1:
                break
            await asyncio.sleep(base_delay_s * (2**attempt))
    assert last_error is not None
    raise last_error

