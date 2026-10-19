"""Pydantic-схемы запросов. Валидируют вход до обращения к CRUD."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AdminSettingIn(BaseModel):
    services: str = Field(min_length=1, description="Название услуги")
    budget_range: str = Field(min_length=1, description='Диапазон бюджета, напр. "100k-900k"')


class ApplicationIn(BaseModel):
    # Контактные данные
    first_name: str = Field(min_length=1, description="Имя")
    last_name: str = Field(min_length=1, description="Фамилия")
    middle_name: str = ""
    # Бизнес и задача
    business_info: str = ""
    budget: str = ""  # на фронте — ползунок, в базе — строка
    niche: str = ""
    company_size: str = ""
    task_volume: str = ""
    role: str = ""  # сотрудник / руководитель
    deadline: str = ""
    task_type: str = ""
    product: str = ""
    # Связь
    contact_method: str = ""
    contact_time: str = ""
    comment: str = ""


class BehaviorMetricIn(BaseModel):
    application_id: int = Field(gt=0)
    time_on_page: int = 0
    clicks: int = 0
    hovers: int = 0
    returns: int = 0
    details: dict[str, Any] = Field(default_factory=dict)
