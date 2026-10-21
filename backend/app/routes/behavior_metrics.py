"""Роут behavior_metrics: анонимная телеметрия клиентского сайта.

POST открыт (сайт шлёт данные каждую секунду), чтение и агрегация — под админом.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.security import require_admin
from app.models.behavior_metrics import BehaviorMetricCRUD
from app.schemas import BehaviorMetricIn

router = APIRouter(prefix="/behavior-metrics", tags=["behavior-metrics"])

admin_only = [Depends(require_admin)]


@router.get("", dependencies=admin_only)
def list_metrics(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return BehaviorMetricCRUD.list(skip, limit)


@router.get("/stats", dependencies=admin_only)
def metrics_stats():
    """Агрегаты времени на странице за день/неделю/месяц для модалки статистики."""
    return BehaviorMetricCRUD.time_stats()


# Приём метрик с сайта — публичный и без проверок: пишем анонимно, append-only.
@router.post("", status_code=201)
def create_metric(payload: BehaviorMetricIn):
    return BehaviorMetricCRUD.create(
        time_on_page=payload.time_on_page,
        buttons_clicked=payload.buttons_clicked,
        cursor_positions=payload.cursor_positions,
        return_frequency=payload.return_frequency,
    )
