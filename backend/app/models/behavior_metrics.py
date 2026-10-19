"""Модель behavior_metrics + CRUD.

Поведение пользователя на странице: сколько времени провёл, сколько кликов,
где зависал курсором, как часто возвращался. Связь с заявкой — один-к-одному:
первичный ключ совпадает с applications.id (внешний ключ).
"""

from __future__ import annotations

import json
from typing import Any

from app.core.db import pool


class BehaviorMetric:
    """
    CREATE TABLE IF NOT EXISTS behavior_metrics (
        application_id INTEGER PRIMARY KEY REFERENCES applications(id) ON DELETE CASCADE,
        time_on_page   INTEGER NOT NULL DEFAULT 0,
        clicks         INTEGER NOT NULL DEFAULT 0,
        hovers         INTEGER NOT NULL DEFAULT 0,
        returns        INTEGER NOT NULL DEFAULT 0,
        details        JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    table = "behavior_metrics"


class BehaviorMetricCRUD:
    """CRUD-операции для метрик поведения."""

    @staticmethod
    def list() -> list[dict[str, Any]]:
        with pool.connection() as conn:
            cur = conn.execute(
                "SELECT application_id, time_on_page, clicks, hovers, returns, details, created_at "
                "FROM behavior_metrics ORDER BY application_id DESC"
            )
            return cur.fetchall()

    @staticmethod
    def get(application_id: int) -> dict[str, Any] | None:
        with pool.connection() as conn:
            cur = conn.execute(
                "SELECT application_id, time_on_page, clicks, hovers, returns, details, created_at "
                "FROM behavior_metrics WHERE application_id = %s",
                (application_id,),
            )
            return cur.fetchone()

    @staticmethod
    def upsert(
        application_id: int,
        time_on_page: int = 0,
        clicks: int = 0,
        hovers: int = 0,
        returns: int = 0,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = json.dumps(details or {})
        with pool.connection() as conn:
            cur = conn.execute(
                "INSERT INTO behavior_metrics "
                "(application_id, time_on_page, clicks, hovers, returns, details) "
                "VALUES (%s, %s, %s, %s, %s, %s::jsonb) "
                "ON CONFLICT (application_id) DO UPDATE SET "
                "time_on_page = EXCLUDED.time_on_page, clicks = EXCLUDED.clicks, "
                "hovers = EXCLUDED.hovers, returns = EXCLUDED.returns, details = EXCLUDED.details "
                "RETURNING application_id, time_on_page, clicks, hovers, returns, details, created_at",
                (application_id, time_on_page, clicks, hovers, returns, payload),
            )
            return cur.fetchone()
