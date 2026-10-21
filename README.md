# Сайт обработки заказов (Кейс 3, части 1-3)

Учебный проект: приём заявок от «тёплых клиентов» с сохранением в БД внутри защищённого Docker-контура.

- **Часть 1 — инфраструктура:** Nginx, PostgreSQL, pgAdmin, защищённый локальный Docker Registry, Watchtower.
- **Часть 2 — приложение:** приватный backend на FastAPI (модели с SQL-докстрингом + CRUD + роуты), фронтенд (клиентский сайт с формой заявки и ползунком бюджета + админ-панель), связка через Nginx `/api`, авторизация админки и закрытый Swagger. Подробно: **[README-VPh05.md](README-VPh05.md)**.
- **Часть 3 — JWT-админка, метрики, ранжирование:** авторизация через JWT + таблица `admins`, CRUD услуг в таблице, анонимные поведенческие метрики с heatmap, ранжирование заявок по «температуре» лида, закрытие контура до единственной точки входа (pgAdmin/registry — в профиль `tools`). Подробно: **[README-VPh06.md](README-VPh06.md)**. Проверки и ответы на замечания преподавателя: **[docs/verification.md](docs/verification.md)**. Скриншоты — в [`screenshots/`](screenshots/).

> Проект выполнен и развёрнут с помощью **Claude Code** (CLI-агент от Anthropic в терминале), а не Cursor. Подключение к серверу, установка Docker, написание конфигов, деплой и выпуск TLS-сертификатов выполнялись через Claude Code по SSH.

## Боевое развёртывание (демо)

Стек развёрнут на VPS (Ubuntu) за системным Nginx с TLS от Let's Encrypt:

| Сервис | Адрес | Проверка |
|--------|-------|----------|
| Клиентский сайт (форма заявки) | https://test.rulewise.ru/ | `200`, HTTPS |
| Админ-панель (вход по логину) | https://test.rulewise.ru/admin | услуги + заявки |
| Swagger API | https://test.rulewise.ru/api/docs | `404` (закрыт в части 2) |
| pgAdmin | https://test.rulewise.ru/pgadmin/ | логин по `.env` |
| Docker Registry | https://reg-test.rulewise.ru/v2/ | `401` без ключа, `200` с ключом |

Контейнеры Postgres и pgAdmin наружу не публикуются (`expose`), порты nginx/registry забинжены на `127.0.0.1` и проксируются системным Nginx только по HTTPS — внешний мир видит лишь защищённые домены.

## Состав

- `nginx` — единственная HTTP-точка входа, порт `8080`: отдаёт собранный фронтенд и проксирует `/api` в backend, `/pgadmin/` в pgAdmin.
- `backend` (часть 2) — FastAPI, приватный (`expose 8000`, наружу не публикуется), доступен только через Nginx `/api`.
- `postgres` — внутренняя PostgreSQL 16, наружу порт не публикуется.
- `pgadmin` — доступен через Nginx по `/pgadmin/`, работает в server-режиме с логином (`PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` из `.env`).
- `registry` — Docker Registry с Basic Auth, порт `5000`.
- `watchtower` — обновляет только контейнеры с label `com.centurylinklabs.watchtower.enable=true`; в учебной конфигурации label не включён, чтобы обновления не происходили неожиданно.

## Запуск

1. Скопировать `.env.example` в `.env` и заменить учебные пароли:

   ```bash
   cp .env.example .env
   ```

2. Создать пользователя Registry (берёт `REGISTRY_USER`/`REGISTRY_PASSWORD` из `.env`):

   ```bash
   chmod +x registry/create-user.sh
   ./registry/create-user.sh
   ```

   Либо явно: `./registry/create-user.sh admin 'strong-password'`.
   Файл `htpasswd` создаётся в `registry/auth/` — именно там его ждёт контейнер registry.

3. Проверить конфигурацию и запустить:

   ```bash
   docker compose --env-file .env config
   docker compose --env-file .env up -d
   docker compose ps
   ```

4. Проверить:

   - Nginx: `http://localhost:8080/`
   - healthcheck: `http://localhost:8080/healthz`
   - pgAdmin: `http://localhost:8080/pgadmin/`
   - Registry API: `http://localhost:5000/v2/` — ожидается `401` без авторизации.

## Подключение pgAdmin к PostgreSQL

В pgAdmin создайте Server:

- Host: `postgres`
- Port: `5432`
- Maintenance database: значение `POSTGRES_DB` из `.env`
- Username: значение `POSTGRES_USER` из `.env`
- Password: значение `POSTGRES_PASSWORD` из `.env`

## Docker Registry

Для учебного HTTP-режима:

```bash
docker login localhost:5000
docker tag example:local localhost:5000/example:local
docker push localhost:5000/example:local
```

На реальном VPS Registry нельзя оставлять на обычном HTTP: нужен домен, TLS-сертификат и firewall с ограничением портов. `docker login` через Basic Auth по HTTP в production небезопасен.

В этом развёртывании реестр опубликован правильно — по HTTPS через системный Nginx:

```bash
docker login reg-test.rulewise.ru     # Basic Auth + TLS
docker tag example:local reg-test.rulewise.ru/example:local
docker push reg-test.rulewise.ru/example:local
```

## Проверка без запуска

Если Docker Desktop не запущен, всё равно можно проверить синтаксис после запуска daemon:

```bash
docker compose --env-file .env config
```

Не коммитьте `.env` и `registry/auth/htpasswd`.
