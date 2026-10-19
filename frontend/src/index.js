import "./styles.css";
import { api } from "./api.js";
import { createTracker } from "./metrics.js";

const $ = (id) => document.getElementById(id);

/* --- Плавающие золотые кружочки на фоне --- */
function spawnCircles(n = 14) {
  const box = $("bg");
  for (let i = 0; i < n; i += 1) {
    const s = document.createElement("span");
    const size = 40 + Math.random() * 150;
    s.style.width = `${size}px`;
    s.style.height = `${size}px`;
    s.style.left = `${Math.random() * 100}%`;
    s.style.animationDuration = `${16 + Math.random() * 20}s`;
    s.style.animationDelay = `${-Math.random() * 25}s`;
    box.appendChild(s);
  }
}

/* --- Разбор диапазона бюджета вида "100k-900k", "900к-1.5кк", "1.5млн" --- */
function parseAmount(token) {
  const t = token.toLowerCase().replace(/\s|₽|руб\.?/g, "").replace(",", ".");
  const m = t.match(/([\d.]+)\s*(кк|kk|млн|m|к|k)?/);
  if (!m) return null;
  let value = parseFloat(m[1]);
  const suf = m[2] || "";
  if (["кк", "kk", "млн", "m"].includes(suf)) value *= 1_000_000;
  else if (["к", "k"].includes(suf)) value *= 1_000;
  return Math.round(value);
}

function parseRange(str) {
  if (!str) return null;
  const parts = str.split(/[-–—]/).map((p) => parseAmount(p)).filter((x) => x != null);
  if (parts.length === 2) return { min: parts[0], max: parts[1] };
  if (parts.length === 1) return { min: Math.round(parts[0] * 0.3), max: parts[0] };
  return null;
}

const fmtRub = (n) => new Intl.NumberFormat("ru-RU").format(n) + " ₽";

function syncBudgetLabel() {
  $("budget-value").textContent = fmtRub(Number($("budget").value));
}

let services = [];

function applyServiceRange() {
  const idx = $("service").value;
  const svc = services.find((s) => String(s.id) === String(idx));
  const slider = $("budget");
  const range = svc ? parseRange(svc.budget_range) : null;
  if (range) {
    slider.min = range.min;
    slider.max = range.max;
    slider.step = Math.max(1000, Math.round((range.max - range.min) / 100));
    slider.value = Math.round((range.min + range.max) / 2);
    $("budget-hint").textContent = `Диапазон услуги: ${svc.budget_range}`;
  } else {
    $("budget-hint").textContent = "Доступный диапазон зависит от выбранной услуги.";
  }
  syncBudgetLabel();
}

async function loadServices() {
  const sel = $("service");
  try {
    services = await api.listServices();
    if (!services.length) {
      sel.innerHTML = '<option value="">Услуги пока не добавлены</option>';
      $("service-hint").textContent = "Администратор ещё не завёл услуги.";
      return;
    }
    sel.innerHTML =
      '<option value="">Выберите услугу…</option>' +
      services.map((s) => `<option value="${s.id}">${s.services}</option>`).join("");
    $("service-hint").textContent = "";
  } catch (e) {
    sel.innerHTML = '<option value="">Ошибка загрузки услуг</option>';
    $("service-hint").textContent = String(e.message || e);
  }
}

function showMessage(kind, text) {
  const el = $("message");
  el.className = `message show ${kind}`;
  el.textContent = text;
}

function collect() {
  const svc = services.find((s) => String(s.id) === String($("service").value));
  return {
    first_name: $("first_name").value.trim(),
    last_name: $("last_name").value.trim(),
    middle_name: $("middle_name").value.trim(),
    business_info: $("business_info").value.trim(),
    budget: fmtRub(Number($("budget").value)),
    niche: $("niche").value.trim(),
    company_size: $("company_size").value,
    task_volume: $("task_volume").value.trim(),
    role: $("role").value,
    deadline: $("deadline").value.trim(),
    task_type: $("task_type").value.trim(),
    product: svc ? svc.services : $("product").value.trim(),
    contact_method: $("contact_method").value,
    contact_time: $("contact_time").value.trim(),
    comment: $("comment").value.trim(),
  };
}

async function onSubmit(e) {
  e.preventDefault();
  const btn = $("submit-btn");
  if (!$("service").value) {
    showMessage("err", "Пожалуйста, выберите услугу.");
    return;
  }
  btn.disabled = true;
  btn.textContent = "Отправляем…";
  try {
    const created = await api.createApplication(collect());
    // Метрики поведения привязываем к созданной заявке (1:1).
    try {
      await api.sendMetrics({ application_id: created.id, ...tracker.snapshot() });
    } catch (_) {
      /* метрики не критичны для пользователя */
    }
    showMessage("ok", "Заявка отправлена! Мы свяжемся с вами в ближайшее время.");
    $("lead-form").reset();
    applyServiceRange();
  } catch (err) {
    showMessage("err", "Не удалось отправить заявку: " + (err.message || err));
  } finally {
    btn.disabled = false;
    btn.textContent = "Отправить заявку";
  }
}

const tracker = createTracker();

spawnCircles();
syncBudgetLabel();
$("budget").addEventListener("input", syncBudgetLabel);
$("service").addEventListener("change", applyServiceRange);
$("lead-form").addEventListener("submit", onSubmit);
loadServices();
