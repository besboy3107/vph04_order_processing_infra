"""Точка входа FastAPI. Собирает все роуты в один общий роут и управляет
жизненным циклом пула соединений с БД.

Приложение приватное: контейнер слушает только внутри docker-сети (expose 8000),
наружу запросы пускает nginx по префиксу /api. root_path=/api нужен Swagger'у,
чтобы корректно работать за обратным прокси.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.core import db
from app.core.config import DOCS_ENABLED, ROOT_PATH
from app.routes import admin_settings, applications, behavior_metrics


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.startup()
    try:
        yield
    finally:
        db.shutdown()


app = FastAPI(
    title="VPh05 — обработка заказов (backend)",
    version="1.0.0",
    lifespan=lifespan,
    root_path=ROOT_PATH,
    # Отключаем авто-редирект со слэшем: он давал 307/405 за nginx-проксированием.
    redirect_slashes=False,
    docs_url="/docs" if DOCS_ENABLED else None,
    redoc_url=None,
    openapi_url="/openapi.json" if DOCS_ENABLED else None,
)

# Один общий роут, к которому подключаются все остальные.
api = APIRouter()
api.include_router(admin_settings.router)
api.include_router(applications.router)
api.include_router(behavior_metrics.router)
app.include_router(api)


@app.get("/health", tags=["service"])
def health():
    return {"status": "ok"}
