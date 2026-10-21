"""Роут applications: приём заявок с сайта + ранжирование по «температуре» лида."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.scoring import score_application
from app.core.security import require_admin
from app.models.applications import ApplicationCRUD
from app.schemas import ApplicationIn

router = APIRouter(prefix="/applications", tags=["applications"])

# Чтение заявок содержит персональные данные клиентов — только для администратора.
admin_only = [Depends(require_admin)]


def _with_score(app: dict) -> dict:
    return {**app, "lead": score_application(app)}


@router.get("", dependencies=admin_only)
def list_applications():
    """Заявки с посчитанной оценкой, отсортированные по убыванию приоритета."""
    items = [_with_score(a) for a in ApplicationCRUD.list()]
    items.sort(key=lambda a: a["lead"]["score"], reverse=True)
    return items


@router.get("/{item_id}", dependencies=admin_only)
def get_application(item_id: int):
    item = ApplicationCRUD.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return _with_score(item)


# Приём заявки с клиентского сайта остаётся публичным.
@router.post("", status_code=201)
def create_application(payload: ApplicationIn):
    return ApplicationCRUD.create(payload.model_dump())


@router.delete("/{item_id}", status_code=204, dependencies=admin_only)
def delete_application(item_id: int):
    if not ApplicationCRUD.delete(item_id):
        raise HTTPException(status_code=404, detail="Заявка не найдена")
