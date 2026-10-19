"""Роут admin_settings: услуги и диапазоны бюджета (используется админ-панелью и
клиентским сайтом для построения выпадающего списка)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.admin_settings import AdminSettingCRUD
from app.schemas import AdminSettingIn

router = APIRouter(prefix="/admin-settings", tags=["admin-settings"])


@router.get("")
def list_settings():
    return AdminSettingCRUD.list()


@router.get("/{item_id}")
def get_setting(item_id: int):
    item = AdminSettingCRUD.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Настройка не найдена")
    return item


@router.post("", status_code=201)
def create_setting(payload: AdminSettingIn):
    return AdminSettingCRUD.create(payload.services, payload.budget_range)


@router.put("/{item_id}")
def update_setting(item_id: int, payload: AdminSettingIn):
    item = AdminSettingCRUD.update(item_id, payload.services, payload.budget_range)
    if item is None:
        raise HTTPException(status_code=404, detail="Настройка не найдена")
    return item


@router.delete("/{item_id}", status_code=204)
def delete_setting(item_id: int):
    if not AdminSettingCRUD.delete(item_id):
        raise HTTPException(status_code=404, detail="Настройка не найдена")
