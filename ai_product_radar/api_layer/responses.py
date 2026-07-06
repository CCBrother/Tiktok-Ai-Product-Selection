from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    ok: bool = True
    data: T | None = None
    error: str | None = None


class ListResponse(BaseModel, Generic[T]):
    ok: bool = True
    items: list[T]
    count: int
    error: str | None = None
