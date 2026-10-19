"""Роут applications: приём заявок с клиентского сайта."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.applications import ApplicationCRUD
from app.schemas import ApplicationIn

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("")
def list_applications():
    return ApplicationCRUD.list()


@router.get("/{item_id}")
def get_application(item_id: int):
    item = ApplicationCRUD.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return item


@router.post("", status_code=201)
def create_application(payload: ApplicationIn):
    return ApplicationCRUD.create(payload.model_dump())


@router.delete("/{item_id}", status_code=204)
def delete_application(item_id: int):
    if not ApplicationCRUD.delete(item_id):
        raise HTTPException(status_code=404, detail="Заявка не найдена")
