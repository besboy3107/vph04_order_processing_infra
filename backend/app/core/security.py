"""Авторизация админ-панели через HTTP Basic.

Публичные эндпоинты (выпадающий список услуг, приём заявки и метрик) остаются
открытыми. Всё, что относится к управлению и к персональным данным клиентов
(создание/изменение услуг, чтение заявок и метрик), закрыто этой зависимостью.
"""

from __future__ import annotations

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import ADMIN_PASSWORD, ADMIN_USER

_basic = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(_basic)) -> str:
    if not ADMIN_PASSWORD:
        # Пароль не задан — панель не настроена, доступ закрыт полностью.
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Админ-доступ не настроен")
    user_ok = secrets.compare_digest(credentials.username, ADMIN_USER)
    pass_ok = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
