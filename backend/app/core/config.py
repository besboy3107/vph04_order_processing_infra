"""Конфигурация подключения к PostgreSQL.

Параметры берём из тех же переменных окружения, что и контейнер postgres в
docker-compose.yml (POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD), host —
имя сервиса `postgres` внутри docker-сети. Наружу БД не публикуется.
"""

import os


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


DB_HOST = _env("POSTGRES_HOST", "postgres")
DB_PORT = _env("POSTGRES_PORT", "5432")
DB_NAME = _env("POSTGRES_DB", "orders")
DB_USER = _env("POSTGRES_USER", "orders_app")
DB_PASSWORD = _env("POSTGRES_PASSWORD", "")

# Открывать ли /docs и схему OpenAPI. На время тестирования — включено (как в уроке).
DOCS_ENABLED = _env("BACKEND_DOCS_ENABLED", "1") not in ("0", "false", "False", "")

# Префикс, под которым nginx проксирует бэкенд наружу. Нужен Swagger'у, чтобы
# правильно построить путь к openapi.json за обратным прокси.
ROOT_PATH = _env("BACKEND_ROOT_PATH", "/api")

CONNINFO = (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)
