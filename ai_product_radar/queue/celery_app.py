from __future__ import annotations

from ai_product_radar.core.config import get_settings


try:
    from celery import Celery
except ImportError:
    Celery = None  # type: ignore[assignment]


settings = get_settings()


class InlineTask:
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def delay(self, *args, **kwargs):
        result = self.fn(*args, **kwargs)
        return type("InlineResult", (), {"id": "inline", "result": result})()


class InlineCelery:
    def task(self, *args, **kwargs):
        def decorator(fn):
            return InlineTask(fn)

        return decorator


if Celery is None:
    celery_app = InlineCelery()
else:
    celery_app = Celery(
        "ai_product_radar",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
