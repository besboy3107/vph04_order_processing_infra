"""Модель admin_settings + CRUD.

Каждая строка — одна услуга компании и допустимый диапазон бюджета для неё.
Фронтенд читает весь набор и динамически строит интерфейс (выпадающий список
услуг + границы ползунка бюджета).
"""

from __future__ import annotations

from typing import Any

from app.core.db import pool


class AdminSetting:
    """
    CREATE TABLE IF NOT EXISTS admin_settings (
        id          SERIAL PRIMARY KEY,
        services    TEXT NOT NULL,
        budget_range TEXT NOT NULL,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    table = "admin_settings"


class AdminSettingCRUD:
    """CRUD-операции для услуг/настроек администратора."""

    @staticmethod
    def list() -> list[dict[str, Any]]:
        with pool.connection() as conn:
            cur = conn.execute(
                "SELECT id, services, budget_range, created_at, updated_at "
                "FROM admin_settings ORDER BY id"
            )
            return cur.fetchall()

    @staticmethod
    def get(item_id: int) -> dict[str, Any] | None:
        with pool.connection() as conn:
            cur = conn.execute(
                "SELECT id, services, budget_range, created_at, updated_at "
                "FROM admin_settings WHERE id = %s",
                (item_id,),
            )
            return cur.fetchone()

    @staticmethod
    def create(services: str, budget_range: str) -> dict[str, Any]:
        with pool.connection() as conn:
            cur = conn.execute(
                "INSERT INTO admin_settings (services, budget_range) "
                "VALUES (%s, %s) RETURNING id, services, budget_range, created_at, updated_at",
                (services, budget_range),
            )
            return cur.fetchone()

    @staticmethod
    def update(item_id: int, services: str, budget_range: str) -> dict[str, Any] | None:
        with pool.connection() as conn:
            cur = conn.execute(
                "UPDATE admin_settings SET services = %s, budget_range = %s, updated_at = now() "
                "WHERE id = %s RETURNING id, services, budget_range, created_at, updated_at",
                (services, budget_range, item_id),
            )
            return cur.fetchone()

    @staticmethod
    def delete(item_id: int) -> bool:
        with pool.connection() as conn:
            cur = conn.execute("DELETE FROM admin_settings WHERE id = %s", (item_id,))
            return cur.rowcount > 0
