"""Интеллектуальная оценка «температуры» заявки.

Чистая функция без обращения к БД (легко тестируется). На вход — словарь заявки,
на выходе — балл 0..100, температура (hot/warm/cold), рекомендованный отдел,
нужен ли персональный менеджер и человекочитаемые причины оценки.

Баллы складываются из квалификационных полей: бюджет, размер компании, роль
заполняющего, срочность дедлайна, объём задачи. Намеренно не завязываемся на
статус заявки — «срочность» выводится нашей логикой, как и просил урок.
"""

from __future__ import annotations

import re
from typing import Any


def _parse_amount(token: str) -> int | None:
    """'100k', '1.5 млн', '900к', '300000 ₽' -> целое число рублей."""
    t = token.lower().replace(" ", "").replace("₽", "").replace("руб.", "").replace("руб", "")
    t = t.replace(",", ".")
    m = re.search(r"([\d.]+)\s*(кк|kk|млн|m|к|k)?", t)
    if not m:
        return None
    try:
        value = float(m.group(1))
    except ValueError:
        return None
    suf = m.group(2) or ""
    if suf in ("кк", "kk", "млн", "m"):
        value *= 1_000_000
    elif suf in ("к", "k"):
        value *= 1_000
    return round(value)


def budget_to_rub(budget: str) -> int:
    """Берём максимум из строки бюджета (может быть диапазон '100k-900k')."""
    if not budget:
        return 0
    parts = [p for p in re.split(r"[-–—]", budget) if p.strip()]
    amounts = [a for a in (_parse_amount(p) for p in parts) if a is not None]
    return max(amounts) if amounts else 0


# Чем срочнее фраза — тем выше вклад.
_URGENT_WORDS = ("срочно", "сегодня", "завтра", "вчера", "как можно", "asap", "ургент")
_SOON_WORDS = ("недел", "дней", "дня", "до конца месяц", "в этом месяц")


def _deadline_score(deadline: str) -> tuple[int, str | None]:
    d = (deadline or "").lower()
    if any(w in d for w in _URGENT_WORDS):
        return 25, "жёсткий дедлайн"
    if any(w in d for w in _SOON_WORDS):
        return 15, "срок в пределах месяца"
    if d.strip():
        return 5, None
    return 0, None


_COMPANY_SCORE = {
    "крупный бизнес": 25,
    "средний бизнес": 18,
    "малый бизнес": 10,
    "частное лицо": 4,
}


def score_application(app: dict[str, Any]) -> dict[str, Any]:
    score = 0
    reasons: list[str] = []

    # 1. Бюджет (0..30)
    rub = budget_to_rub(str(app.get("budget", "")))
    if rub >= 1_000_000:
        score += 30
        reasons.append("бюджет свыше 1 млн ₽")
    elif rub >= 500_000:
        score += 22
        reasons.append("бюджет 500k–1 млн ₽")
    elif rub >= 150_000:
        score += 14
        reasons.append("средний бюджет")
    elif rub > 0:
        score += 6
    # 2. Размер компании (0..25)
    comp = str(app.get("company_size", "")).strip().lower()
    comp_pts = _COMPANY_SCORE.get(comp, 0)
    if comp_pts:
        score += comp_pts
        if comp_pts >= 18:
            reasons.append(f"{app.get('company_size')}")
    # 3. Роль заполняющего (0..15)
    if str(app.get("role", "")).strip().lower() == "руководитель":
        score += 15
        reasons.append("заявку оставил руководитель (ЛПР)")
    elif str(app.get("role", "")).strip():
        score += 5
    # 4. Срочность (0..25)
    dl_pts, dl_reason = _deadline_score(str(app.get("deadline", "")))
    score += dl_pts
    if dl_reason:
        reasons.append(dl_reason)
    # 5. Объём задачи (0..10) — упоминание парка / нескольких единиц
    vol = str(app.get("task_volume", "")).lower()
    if re.search(r"\d{2,}", vol) or any(w in vol for w in ("парк", "сеть", "несколько", "много")):
        score += 10
        reasons.append("крупный объём задачи")
    elif vol.strip():
        score += 3

    score = max(0, min(100, score))

    if score >= 60:
        temperature = "hot"
        needs_manager = True
    elif score >= 35:
        temperature = "warm"
        needs_manager = comp_pts >= 18 or rub >= 500_000
    else:
        temperature = "cold"
        needs_manager = False

    department = _route_department(app, rub)

    return {
        "score": score,
        "temperature": temperature,
        "needs_manager": needs_manager,
        "department": department,
        "budget_rub": rub,
        "reasons": reasons,
    }


def _route_department(app: dict[str, Any], rub: int) -> str:
    """Грубая маршрутизация по отделу на основе типа задачи / продукта."""
    text = " ".join(
        str(app.get(k, "")) for k in ("task_type", "product", "niche", "comment")
    ).lower()
    if any(w in text for w in ("керамик", "покрас", "полиров", "детейл", "кузов")):
        return "Детейлинг"
    if any(w in text for w in ("аудио", "звук", "колонк", "саб")):
        return "Аудио"
    if rub >= 700_000:
        return "VIP / ключевые клиенты"
    return "Общий отдел продаж"
