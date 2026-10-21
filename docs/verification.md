# Проверки развёртывания (ответ на замечания преподавателя)

## Замечание 1 — не зависеть только от браузера: `docker compose config` + проверка реестра curl'ом; пояснить замену Cursor

### 1.1. `docker compose config` — состав контура
По умолчанию (рабочий режим) поднимаются только четыре сервиса; `pgadmin` и
`registry` вынесены в профиль `tools` и наружу не торчат:

```bash
$ docker compose --env-file .env config --services
postgres
backend
nginx
watchtower

$ docker compose --env-file .env config --profiles
tools
```

Полную развёрнутую конфигурацию (с подставленными переменными, портами и сетями)
можно получить так — она подтверждает, что backend/postgres не публикуют порты
наружу (`expose`), а nginx слушает только `127.0.0.1`:

```bash
docker compose --env-file .env config
```

### 1.2. Проверка Docker Registry без браузера (curl)
Реестр закрыт Basic-аутентификацией и TLS; проверяется двумя запросами:

```bash
# Без логина — 401 Unauthorized
$ curl -s -o /dev/null -w "%{http_code}\n" https://reg-test.rulewise.ru/v2/
401

# С логином — 200 и пустой каталог
$ curl -s -u "$REGISTRY_USER:$REGISTRY_PASSWORD" https://reg-test.rulewise.ru/v2/
{}
```

> В части 3 реестр по умолчанию выключен (профиль `tools`). Для этой проверки его
> поднимают явно: `docker compose --env-file .env --profile tools up -d registry`.

### 1.3. Про инструмент (Cursor → Claude Code)
Урок рассчитан на **Cursor**. Проект выполнен через **Claude Code** — CLI-агента от
Anthropic, работающего в терминале. Это функционально эквивалентный агентный
инструмент: тот же цикл «промпт → правка файлов → запуск команд». Все действия
(правка backend/frontend/конфигов, сборка образов, `docker compose`, выпуск TLS,
деплой по SSH) выполнялись через Claude Code. Отдельного сеанса Cursor нет —
замена инструмента осознанная и задокументирована здесь и в README.

## Замечание 2 — README и стенд должны совпадать: Swagger закрыт, в рабочем `.env` стоит `BACKEND_DOCS_ENABLED=0`

Приведено к одному состоянию:
- в рабочем `.env` **явно** задано `BACKEND_DOCS_ENABLED=0` (значение по умолчанию в
  `config.py` тоже `0`);
- во всех README сказано, что Swagger закрыт;
- проверка совпадает с описанием:

```bash
$ curl -s -o /dev/null -w "%{http_code}\n" https://test.rulewise.ru/api/docs
404
```

Открывать `/api/docs` следует только временно и локально, выставив
`BACKEND_DOCS_ENABLED=1` на время отладки, а итоговые скриншоты снимать при
закрытом Swagger (404).
