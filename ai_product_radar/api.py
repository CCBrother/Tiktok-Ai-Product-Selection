from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from ai_product_radar.api_layer.auth import OptionalAuthMiddleware
from ai_product_radar.api_layer.errors import AppError, register_error_handlers
from ai_product_radar.api_layer.responses import BaseResponse, ListResponse
from ai_product_radar.core.config import get_settings
from ai_product_radar.core.logging import configure_logging
from ai_product_radar.db.repository import CsvProductRepository, DatabaseProductRepository, ProductRepository
from ai_product_radar.db.session import SessionLocal
from ai_product_radar.integrated_system import system_overview


configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(OptionalAuthMiddleware)
register_error_handlers(app)

def build_repository() -> ProductRepository:
    if settings.api_data_source.lower() in {"database", "postgres", "postgresql", "db"}:
        return DatabaseProductRepository(SessionLocal)
    return CsvProductRepository(settings.product_radar_data)


repository = build_repository()


@app.get("/health")
def health() -> BaseResponse[dict[str, str]]:
    return BaseResponse(data={"status": "ok", "environment": settings.environment})


@app.get("/system")
def system() -> BaseResponse[dict]:
    return BaseResponse(data=system_overview())


@app.get("/products")
def list_products(
    limit: int = Query(default=100, ge=1, le=500),
    category: str | None = None,
) -> ListResponse[dict]:
    products = repository.list_products(limit=limit, category=category)
    return ListResponse(items=products, count=len(products))


@app.get("/top-products")
def top_products(limit: int = Query(default=20, ge=1, le=100)) -> ListResponse[dict]:
    products = repository.top_products(limit=limit)
    return ListResponse(items=products, count=len(products))


@app.get("/product/{product_id}")
def get_product(product_id: str) -> BaseResponse[dict]:
    product = repository.get_product(product_id)
    if product is None:
        raise AppError("Product not found", status_code=404)
    return BaseResponse(data=product)


@app.get("/ai-scores")
def ai_scores(limit: int = Query(default=100, ge=1, le=500)) -> ListResponse[dict]:
    rows = repository.ai_scores(limit=limit)
    return ListResponse(items=rows, count=len(rows))


@app.get("/trending")
def trending(limit: int = Query(default=20, ge=1, le=100)) -> ListResponse[dict]:
    rows = repository.trending(limit=limit)
    return ListResponse(items=rows, count=len(rows))


@app.get("/blue-ocean")
def blue_ocean(limit: int = Query(default=20, ge=1, le=100)) -> ListResponse[dict]:
    rows = repository.blue_ocean(limit=limit)
    return ListResponse(items=rows, count=len(rows))


@app.get("/opportunity")
def opportunity(limit: int = Query(default=20, ge=1, le=100)) -> ListResponse[dict]:
    rows = repository.opportunities(limit=limit)
    return ListResponse(items=rows, count=len(rows))


@app.get("/dashboard-summary")
def dashboard_summary() -> BaseResponse[dict]:
    return BaseResponse(data=repository.dashboard_summary())


@app.get("/lifecycle")
def lifecycle(limit: int = Query(default=100, ge=1, le=500)) -> ListResponse[dict]:
    rows = repository.lifecycle(limit=limit)
    return ListResponse(items=rows, count=len(rows))


@app.post("/recompute-score")
def recompute_score() -> BaseResponse[dict[str, str]]:
    return BaseResponse(data={"status": "ok"})
