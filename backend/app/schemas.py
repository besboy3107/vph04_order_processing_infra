"""Pydantic-схемы запросов. Валидируют вход до обращения к CRUD."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AuthIn(BaseModel):
    username: str = Field(min_length=3, max_length=64, description="Логин администратора")
    password: str = Field(min_length=6, max_length=128, description="Пароль")


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
    """Анонимная телеметрия. application_id принимаем для совместимости с фронтом,
    но backend его игнорирует и никуда не сохраняет (требование части 3)."""

    application_id: int = 0
    time_on_page: int = 0
    buttons_clicked: str = ""
    cursor_positions: str = ""
    return_frequency: int = 0
