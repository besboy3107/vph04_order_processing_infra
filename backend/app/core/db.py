"""Драйвер PostgreSQL: пул соединений psycopg3 и инициализация схемы.

Это и есть "работа драйвера для PostgreSQL" из ТЗ. CRUD-классы моделей берут
соединения отсюда, напрямую к базе никто кроме backend не ходит.
"""

from __future__ import annotations

import time

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.core.config import CONNINFO

# Пул открывается лениво при старте приложения (см. lifespan в main.py).
pool = ConnectionPool(CONNINFO, min_size=1, max_size=10, open=False, kwargs={"row_factory": dict_row})


def wait_for_db(timeout: float = 60.0) -> None:
    """Дожидаемся готовности postgres (контейнер поднимается не мгновенно)."""
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(CONNINFO, connect_timeout=3) as conn:
                conn.execute("SELECT 1")
            return
        except Exception as exc:  # noqa: BLE001 — на старте ловим любую ошибку соединения
            last_err = exc
            time.sleep(1.5)
    raise RuntimeError(f"PostgreSQL недоступен за {timeout}s: {last_err}")


def init_schema() -> None:
    """Создаём таблицы из SQL, лежащего в докстрингах классов-моделей."""
    # Импорт здесь, чтобы избежать циклических импортов на уровне модуля.
    from app.models.admin_settings import AdminSetting
    from app.models.applications import Application
    from app.models.behavior_metrics import BehaviorMetric

    # Порядок важен: applications раньше behavior_metrics (внешний ключ 1:1).
    for model in (AdminSetting, Application, BehaviorMetric):
        sql = (model.__doc__ or "").strip()
        if not sql:
            raise RuntimeError(f"У модели {model.__name__} нет SQL в докстринге")
        with pool.connection() as conn:
            conn.execute(sql)


def startup() -> None:
    wait_for_db()
    pool.open()
    init_schema()


def shutdown() -> None:
    pool.close()
