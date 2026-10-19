# VPh05 — Кейс 3, часть 2: бэкенд + фронтенд поверх инфраструктуры

Дополнение к части 1 (Nginx + Postgres + pgAdmin + Registry + Watchtower). Добавлены
приватный backend на FastAPI и собираемый фронтенд, связанные через nginx `/api`.

## Что добавлено

```
backend/                     FastAPI (приватный, наружу только через nginx /api)
  app/core/      db.py        пул соединений psycopg3 + инициализация схемы из докстрингов
  app/models/                 3 модели, в каждой SQL в докстринге + класс CRUD
    admin_settings.py          услуги и диапазоны бюджета (для выпадающего списка)
    applications.py            заявка клиента (контакты, бизнес, бюджет-строка, квалификация)
    behavior_metrics.py        поведение на странице, 1:1 к заявке (PK = applications.id)
  app/routes/                 отдельный роут на каждую модель
  app/main.py                 все роуты собраны в один общий роут (APIRouter)
frontend/                    webpack + npm, white elite theme, Google Fonts (Nunito/Comfortaa)
  src/index.html/.js          клиентский сайт: услуги из /api/admin-settings, ползунок бюджета, форма
  src/admin.html/.js          админ-панель услуг на /admin
  dist/                       npm run build (CSS вынесен mini-css-extract-plugin)
```

## Живой стенд

| Что | URL |
|-----|-----|
| Клиентский сайт | https://test.rulewise.ru/ |
| Админ-панель | https://test.rulewise.ru/admin |
| Swagger (на время теста) | https://test.rulewise.ru/api/docs |
| pgAdmin | https://test.rulewise.ru/pgadmin/ |

## Выполнение ДЗ

1. **Бэкенд + БД**: контейнеры `vph04-backend` и `vph04-postgres` подняты, видят друг друга;
   `init_schema()` создаёт 3 таблицы при старте.
2. **3 услуги** заведены через API (`POST /api/admin-settings`): «Полировка кузова» (50k-150k),
   «Химчистка салона» (15k-60k), «Керамическое покрытие 9H» (100k-900k); `GET` отдаёт список.
3. **Фронтенд**: белая тема, округлые шрифты, анимация золотых кружков; `npm run build` → `dist`;
   CSS отдаётся отдельным файлом (mini-css-extract-plugin) — ошибки 404 на стили нет.
4. **Интеграция**: nginx проксирует `/api/` → `backend:8000`; на бэкенде `redirect_slashes=False`
   и точные пути без хвостового слэша — это снимает 307 Redirect / 405 Not Allowed.
   На сайте услуга выбирается из выпадающего списка, форма отправляется, приходит
   «Заявка отправлена! Мы свяжемся с вами в ближайшее время».
5. **Хранение**: заявки сохраняются в `applications`, метрики поведения — в `behavior_metrics`
   (связь 1:1). Проверено: 2 заявки (через API и с сайта) + метрика к заявке с сайта.

Скриншоты работающего проекта — в папке [`screenshots/`](screenshots/).

## Ключевой фикс 405/307

FastAPI по умолчанию редиректит `/applications` ↔ `/applications/` статусом 307, что за
обратным прокси ломает POST (405 Not Allowed). Решение: `FastAPI(redirect_slashes=False)`,
маршруты заданы на точных путях, а nginx `proxy_pass http://backend:8000/;` срезает префикс `/api`.
