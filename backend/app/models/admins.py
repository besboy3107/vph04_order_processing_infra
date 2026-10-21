"""Модель admins + CRUD.

Администраторы панели: логин и хеш пароля (pbkdf2_sha256). Первый администратор
регистрируется при первом запуске (пока таблица пуста); после этого регистрация
на фронте скрывается, вход — только по логину/паролю с выдачей JWT.
"""

from __future__ import annotations

from typing import Any

from app.core.db import pool


class Admin:
    """
    CREATE TABLE IF NOT EXISTS admins (
        id            SERIAL PRIMARY KEY,
        username      TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    table = "admins"


class AdminCRUD:
    """CRUD-операции для администраторов."""

    @staticmethod
    def count() -> int:
        with pool.connection() as conn:
            cur = conn.execute("SELECT COUNT(*) AS n FROM admins")
            return int(cur.fetchone()["n"])

    @staticmethod
    def get_by_username(username: str) -> dict[str, Any] | None:
        with pool.connection() as conn:
            cur = conn.execute(
                "SELECT id, username, password_hash, created_at FROM admins WHERE username = %s",
                (username,),
            )
            return cur.fetchone()

    @staticmethod
    def create(username: str, password_hash: str) -> dict[str, Any]:
        with pool.connection() as conn:
            cur = conn.execute(
                "INSERT INTO admins (username, password_hash) VALUES (%s, %s) "
                "RETURNING id, username, created_at",
                (username, password_hash),
            )
            return cur.fetchone()
