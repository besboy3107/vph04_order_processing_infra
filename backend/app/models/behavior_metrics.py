"""Модель behavior_metrics + CRUD.

Анонимная поведенческая телеметрия клиентского сайта: сколько секунд человек
провёл на странице, какие кнопки нажимал, где был курсор, как часто возвращался
на вкладку. Данные пишутся append-only (каждую секунду новая строка) и ни с кем
не связаны — никаких проверок на существование заявки (часть 3 урока явно
требует убрать логику application_id и писать метрики анонимно).
"""

from __future__ import annotations

from typing import Any

from app.core.db import pool


class BehaviorMetric:
    """
    CREATE TABLE IF NOT EXISTS behavior_metrics (
        id               SERIAL PRIMARY KEY,
        time_on_page     INTEGER NOT NULL DEFAULT 0,
        buttons_clicked  TEXT NOT NULL DEFAULT '',
        cursor_positions TEXT NOT NULL DEFAULT '',
        return_frequency INTEGER NOT NULL DEFAULT 0,
        created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    table = "behavior_metrics"


class BehaviorMetricCRUD:
    """CRUD-операции для анонимных метрик поведения."""

    @staticmethod
    def list(skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        with pool.connection() as conn:
            cur = conn.execute(
                "SELECT id, time_on_page, buttons_clicked, cursor_positions, "
                "return_frequency, created_at FROM behavior_metrics "
                "ORDER BY id DESC OFFSET %s LIMIT %s",
                (max(0, skip), max(1, min(limit, 1000))),
            )
            return cur.fetchall()

    @staticmethod
    def create(
        time_on_page: int = 0,
        buttons_clicked: str = "",
        cursor_positions: str = "",
        return_frequency: int = 0,
    ) -> dict[str, Any]:
        with pool.connection() as conn:
            cur = conn.execute(
                "INSERT INTO behavior_metrics "
                "(time_on_page, buttons_clicked, cursor_positions, return_frequency) "
                "VALUES (%s, %s, %s, %s) "
                "RETURNING id, time_on_page, buttons_clicked, cursor_positions, "
                "return_frequency, created_at",
                (int(time_on_page), buttons_clicked or "", cursor_positions or "", int(return_frequency)),
            )
            return cur.fetchone()

    @staticmethod
    def time_stats() -> dict[str, Any]:
        """Среднее и максимальное время на странице за день / неделю / месяц."""
        with pool.connection() as conn:
            cur = conn.execute(
                """
                SELECT
                  COALESCE(ROUND(AVG(time_on_page) FILTER (WHERE created_at >= now() - interval '1 day')), 0)  AS avg_day,
                  COALESCE(MAX(time_on_page)       FILTER (WHERE created_at >= now() - interval '1 day'), 0)   AS max_day,
                  COALESCE(ROUND(AVG(time_on_page) FILTER (WHERE created_at >= now() - interval '7 days')), 0) AS avg_week,
                  COALESCE(MAX(time_on_page)       FILTER (WHERE created_at >= now() - interval '7 days'), 0)  AS max_week,
                  COALESCE(ROUND(AVG(time_on_page) FILTER (WHERE created_at >= now() - interval '30 days')), 0) AS avg_month,
                  COALESCE(MAX(time_on_page)       FILTER (WHERE created_at >= now() - interval '30 days'), 0)  AS max_month,
                  COUNT(*) AS samples
                FROM behavior_metrics
                """
            )
            row = cur.fetchone()
            # psycopg возвращает Decimal для ROUND/AVG — приводим к int для JSON.
            return {k: int(v) for k, v in row.items()}
