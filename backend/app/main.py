from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.creative import router as creative_router
from backend.app.api.decision import router as decision_router
from backend.app.api.products import router as product_router
from backend.app.api.radar import router as radar_router
from backend.app.api.supply import router as supply_router
from backend.app.core.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(product_router)
app.include_router(decision_router)
app.include_router(creative_router)
app.include_router(supply_router)
app.include_router(radar_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}
