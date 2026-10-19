"""Модель applications + CRUD.

Одна заявка "тёплого клиента": контактные данные, информация о бизнесе,
бюджет (на фронте выбирается ползунком, хранится строкой), квалификационные
поля (ниша, размер компании, объём задачи, роль и т.д.) и способ/время связи.
"""

from __future__ import annotations

from typing import Any

from app.core.db import pool

# Поля, которые принимаем из формы (без id/created_at/updated_at).
FIELDS = (
    "first_name",
    "last_name",
    "middle_name",
    "business_info",
    "budget",
    "contact_method",
    "contact_time",
    "comment",
    "niche",
    "company_size",
    "task_volume",
    "role",
    "deadline",
    "task_type",
    "product",
)

_RETURNING = "id, " + ", ".join(FIELDS) + ", created_at, updated_at"


class Application:
    """
    CREATE TABLE IF NOT EXISTS applications (
        id             SERIAL PRIMARY KEY,
        first_name     TEXT NOT NULL,
        last_name      TEXT NOT NULL,
        middle_name    TEXT DEFAULT '',
        business_info  TEXT DEFAULT '',
        budget         TEXT DEFAULT '',
        contact_method TEXT DEFAULT '',
        contact_time   TEXT DEFAULT '',
        comment        TEXT DEFAULT '',
        niche          TEXT DEFAULT '',
        company_size   TEXT DEFAULT '',
        task_volume    TEXT DEFAULT '',
        role           TEXT DEFAULT '',
        deadline       TEXT DEFAULT '',
        task_type      TEXT DEFAULT '',
        product        TEXT DEFAULT '',
        created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    table = "applications"


class ApplicationCRUD:
    """CRUD-операции для заявок."""

    @staticmethod
    def list() -> list[dict[str, Any]]:
        with pool.connection() as conn:
            cur = conn.execute(f"SELECT {_RETURNING} FROM applications ORDER BY id DESC")
            return cur.fetchall()

    @staticmethod
    def get(item_id: int) -> dict[str, Any] | None:
        with pool.connection() as conn:
            cur = conn.execute(f"SELECT {_RETURNING} FROM applications WHERE id = %s", (item_id,))
            return cur.fetchone()

    @staticmethod
    def create(data: dict[str, Any]) -> dict[str, Any]:
        cols = ", ".join(FIELDS)
        placeholders = ", ".join(["%s"] * len(FIELDS))
        values = [str(data.get(f, "") or "") for f in FIELDS]
        with pool.connection() as conn:
            cur = conn.execute(
                f"INSERT INTO applications ({cols}) VALUES ({placeholders}) RETURNING {_RETURNING}",
                values,
            )
            return cur.fetchone()

    @staticmethod
    def delete(item_id: int) -> bool:
        with pool.connection() as conn:
            cur = conn.execute("DELETE FROM applications WHERE id = %s", (item_id,))
            return cur.rowcount > 0
