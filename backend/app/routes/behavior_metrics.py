"""Роут behavior_metrics: метрики поведения, привязанные к заявке 1:1."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_admin
from app.models.applications import ApplicationCRUD
from app.models.behavior_metrics import BehaviorMetricCRUD
from app.schemas import BehaviorMetricIn

router = APIRouter(prefix="/behavior-metrics", tags=["behavior-metrics"])

admin_only = [Depends(require_admin)]


@router.get("", dependencies=admin_only)
def list_metrics():
    return BehaviorMetricCRUD.list()


@router.get("/{application_id}", dependencies=admin_only)
def get_metric(application_id: int):
    item = BehaviorMetricCRUD.get(application_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Метрики не найдены")
    return item


@router.post("", status_code=201)
def create_metric(payload: BehaviorMetricIn):
    if ApplicationCRUD.get(payload.application_id) is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return BehaviorMetricCRUD.upsert(
        payload.application_id,
        payload.time_on_page,
        payload.clicks,
        payload.hovers,
        payload.returns,
        payload.details,
    )
