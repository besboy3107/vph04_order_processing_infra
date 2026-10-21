"""Конфигурация backend: подключение к PostgreSQL, JWT и флаги.

Параметры берём из тех же переменных окружения, что и контейнер postgres в
docker-compose.yml (POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD), host —
имя сервиса `postgres` внутри docker-сети. Наружу БД не публикуется.
"""

import os
import secrets


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


DB_HOST = _env("POSTGRES_HOST", "postgres")
DB_PORT = _env("POSTGRES_PORT", "5432")
DB_NAME = _env("POSTGRES_DB", "orders")
DB_USER = _env("POSTGRES_USER", "orders_app")
DB_PASSWORD = _env("POSTGRES_PASSWORD", "")

# Открывать ли /docs и схему OpenAPI. В рабочем контуре закрыто (замечание
# преподавателя: README и реальный стенд должны совпадать). Включается явно
# BACKEND_DOCS_ENABLED=1 только на время отладки.
DOCS_ENABLED = _env("BACKEND_DOCS_ENABLED", "0") not in ("0", "false", "False", "")

# Префикс, под которым nginx проксирует бэкенд наружу. Нужен Swagger'у, чтобы
# правильно построить путь к openapi.json за обратным прокси.
ROOT_PATH = _env("BACKEND_ROOT_PATH", "/api")

# --- JWT-авторизация админ-панели (часть 3) ---
# Секрет для подписи токенов (HS256). В проде задаётся в .env:
#   openssl rand -hex 32
# Если не задан — генерируем эфемерный на старте: токены проживут до перезапуска
# контейнера, но пароли из БД при этом не компрометируются.
JWT_SECRET = _env("JWT_SECRET_KEY") or secrets.token_hex(32)
# Время жизни токена в часах.
JWT_TTL_HOURS = int(_env("JWT_TTL_HOURS", "12") or "12")

CONNINFO = (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)
