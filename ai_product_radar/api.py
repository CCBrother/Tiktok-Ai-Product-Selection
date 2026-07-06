from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from ai_product_radar.api_layer.auth import OptionalAuthMiddleware
from ai_product_radar.api_layer.errors import AppError, register_error_handlers
from ai_product_radar.api_layer.responses import BaseResponse, ListResponse
from ai_product_radar.core.config import get_settings
from ai_product_radar.core.logging import configure_logging
from ai_product_radar.db.repository import CsvProductRepository


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

repository = CsvProductRepository(settings.product_radar_data)


@app.get("/health")
def health() -> BaseResponse[dict[str, str]]:
    return BaseResponse(data={"status": "ok", "environment": settings.environment})


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


@app.get("/ai-scores")
def ai_scores(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, object]:
    scores = repository.ai_scores(limit=limit)
    return {"items": scores, "count": len(scores)}


@app.get("/trending")
def trending(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, object]:
    products = repository.trending(limit=limit)
    return {"items": products, "count": len(products)}


@app.get("/blue-ocean")
def blue_ocean(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, object]:
    products = repository.blue_ocean(limit=limit)
    return {"items": products, "count": len(products)}


@app.get("/opportunity")
def opportunity(limit: int = Query(default=20, ge=1, le=100)) -> dict[str, object]:
    products = repository.opportunities(limit=limit)
    return {"items": products, "count": len(products)}


@app.post("/recompute-score")
def recompute_score(product_id: str | None = None) -> dict[str, object]:
    if product_id:
        product = repository.get_product(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"status": "ok", "updated": 1, "item": product}
    scores = repository.ai_scores(limit=500)
    return {"status": "ok", "updated": len(scores)}


@app.get("/dashboard-summary")
def dashboard_summary() -> dict[str, object]:
    return repository.dashboard_summary()


@app.get("/lifecycle")
def lifecycle(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, object]:
    rows = repository.lifecycle(limit=limit)
    return {"items": rows, "count": len(rows)}
