"""Роут auth: регистрация первого администратора, вход (JWT), профиль.

Логика регистрации: пока в таблице admins нет ни одного администратора, разрешена
регистрация (bootstrap первого). Как только админ появился — /register отдаёт 403,
а фронтенд скрывает кнопку регистрации (узнаёт об этом по /auth/check).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import create_token, hash_password, require_admin, verify_password
from app.models.admins import AdminCRUD
from app.schemas import AuthIn

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/check")
def check():
    """Есть ли уже хотя бы один админ. Фронт по этому полю показывает/прячет регистрацию."""
    return {"has_admin": AdminCRUD.count() > 0}


@router.post("/register", status_code=201)
def register(payload: AuthIn):
    if AdminCRUD.count() > 0:
        raise HTTPException(status_code=403, detail="Администратор уже зарегистрирован")
    admin = AdminCRUD.create(payload.username, hash_password(payload.password))
    return {"token": create_token(admin["username"]), "username": admin["username"]}


@router.post("/login")
def login(payload: AuthIn):
    admin = AdminCRUD.get_by_username(payload.username)
    if admin is None or not verify_password(payload.password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"token": create_token(admin["username"]), "username": admin["username"]}


@router.get("/me")
def me(user: str = Depends(require_admin)):
    return {"username": user}
