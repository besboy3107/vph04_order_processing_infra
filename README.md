# VPh04 — инфраструктура сайта обработки заказов

Учебная реализация первой части кейса: Nginx, PostgreSQL, pgAdmin, защищённый локальный Docker Registry и Watchtower. Backend намеренно оставлен закомментированным до следующего этапа.

> Проект выполнен и развёрнут с помощью **Claude Code** (CLI-агент от Anthropic в терминале), а не Cursor. Подключение к серверу, установка Docker, написание конфигов, деплой и выпуск TLS-сертификатов выполнялись через Claude Code по SSH.

## Боевое развёртывание (демо)

Стек развёрнут на VPS (Ubuntu) за системным Nginx с TLS от Let's Encrypt:

| Сервис | Адрес | Проверка |
|--------|-------|----------|
| Сайт (входная точка Nginx) | https://test.rulewise.ru | `200`, HTTPS |
| pgAdmin | https://test.rulewise.ru/pgadmin/ | логин по `.env` |
| Docker Registry | https://reg-test.rulewise.ru/v2/ | `401` без ключа, `200` с ключом |

Контейнеры Postgres и pgAdmin наружу не публикуются (`expose`), порты nginx/registry забинжены на `127.0.0.1` и проксируются системным Nginx только по HTTPS — внешний мир видит лишь защищённые домены.

## Состав

- `nginx` — единственная HTTP-точка входа приложения, порт `8080`.
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
