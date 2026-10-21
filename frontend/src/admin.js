import "./styles.css";
import { api, setToken, clearToken, hasToken } from "./api.js";

const $ = (id) => document.getElementById(id);

function spawnCircles(n = 10) {
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

function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function msg(id, kind, text) {
  const el = $(id);
  el.className = `message show ${kind}`;
  el.textContent = text;
}

const TEMP = {
  hot: { label: "🔥 Горячий", cls: "badge hot" },
  warm: { label: "🌤 Тёплый", cls: "badge warm" },
  cold: { label: "❄️ Холодный", cls: "badge cold" },
};

/* ------------------------- Услуги (CRUD в таблице) ------------------------- */
async function renderServices() {
  const tbody = $("rows");
  try {
    const items = await api.listServices();
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="4">Услуг пока нет — добавьте первую.</td></tr>';
      return;
    }
    tbody.innerHTML = items
      .map(
        (s) => `
        <tr data-id="${s.id}">
          <td>${s.id}</td>
          <td class="cell-services">${esc(s.services)}</td>
          <td class="cell-budget">${esc(s.budget_range)}</td>
          <td class="row-actions">
            <button class="mini row-edit" data-id="${s.id}">Изм.</button>
            <button class="mini row-del" data-id="${s.id}">Удал.</button>
          </td>
        </tr>`
      )
      .join("");
    bindServiceRows();
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4">Ошибка: ${esc(e.message || e)}</td></tr>`;
  }
}

function bindServiceRows() {
  $("rows")
    .querySelectorAll(".row-del")
    .forEach((btn) =>
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          await api.deleteService(btn.dataset.id);
          renderServices();
        } catch (e) {
          msg("message", "err", "Не удалось удалить: " + (e.message || e));
          btn.disabled = false;
        }
      })
    );
  $("rows")
    .querySelectorAll(".row-edit")
    .forEach((btn) => btn.addEventListener("click", () => startEdit(btn.dataset.id)));
}

function startEdit(id) {
  const tr = $("rows").querySelector(`tr[data-id="${id}"]`);
  if (!tr || tr.classList.contains("editing")) return;
  const services = tr.querySelector(".cell-services").textContent;
  const budget = tr.querySelector(".cell-budget").textContent;
  tr.classList.add("editing");
  tr.querySelector(".cell-services").innerHTML = `<input class="edit-services" value="${esc(services)}" />`;
  tr.querySelector(".cell-budget").innerHTML = `<input class="edit-budget" value="${esc(budget)}" />`;
  tr.querySelector(".row-actions").innerHTML = `
    <button class="mini row-save" data-id="${id}">Сохр.</button>
    <button class="mini row-cancel">Отмена</button>`;
  tr.querySelector(".row-cancel").addEventListener("click", renderServices);
  tr.querySelector(".row-save").addEventListener("click", async () => {
    const s = tr.querySelector(".edit-services").value.trim();
    const b = tr.querySelector(".edit-budget").value.trim();
    if (!s || !b) {
      msg("message", "err", "Оба поля обязательны.");
      return;
    }
    try {
      await api.updateService(id, s, b);
      msg("message", "ok", `Услуга #${id} обновлена.`);
      renderServices();
    } catch (e) {
      msg("message", "err", "Не удалось сохранить: " + (e.message || e));
    }
  });
}

/* --------------------------- Заявки + ранжирование -------------------------- */
let appsCache = [];

async function renderApplications() {
  const tbody = $("app-rows");
  try {
    appsCache = await api.listApplications();
    if (!appsCache.length) {
      tbody.innerHTML = '<tr><td colspan="6">Заявок пока нет.</td></tr>';
      return;
    }
    tbody.innerHTML = appsCache
      .map((a) => {
        const name = [a.last_name, a.first_name, a.middle_name].filter(Boolean).join(" ");
        const t = TEMP[a.lead.temperature] || TEMP.cold;
        return `<tr>
          <td><span class="${t.cls}">${t.label}</span> <span class="score">${a.lead.score}</span></td>
          <td>${esc(name)}</td>
          <td>${esc(a.product)}</td>
          <td>${esc(a.budget)}</td>
          <td>${esc(a.lead.department)}</td>
          <td><button class="mini row-view" data-id="${a.id}">Просмотр</button></td>
        </tr>`;
      })
      .join("");
    tbody.querySelectorAll(".row-view").forEach((btn) =>
      btn.addEventListener("click", () => openAppModal(Number(btn.dataset.id)))
    );
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6">Ошибка: ${esc(e.message || e)}</td></tr>`;
  }
}

function fieldRow(label, value) {
  if (!value) return "";
  return `<div class="kv"><span>${esc(label)}</span><b>${esc(value)}</b></div>`;
}

function openAppModal(id) {
  const a = appsCache.find((x) => x.id === id);
  if (!a) return;
  const t = TEMP[a.lead.temperature] || TEMP.cold;
  const name = [a.last_name, a.first_name, a.middle_name].filter(Boolean).join(" ");
  $("app-modal-title").innerHTML = `Заявка #${a.id} · <span class="${t.cls}">${t.label}</span> ${a.lead.score}/100`;
  $("app-modal-body").innerHTML =
    `<div class="lead-summary">
       <div>Отдел: <b>${esc(a.lead.department)}</b></div>
       <div>Персональный менеджер: <b>${a.lead.needs_manager ? "да" : "не обязательно"}</b></div>
       ${a.lead.reasons.length ? `<div class="reasons">Почему: ${a.lead.reasons.map(esc).join(" · ")}</div>` : ""}
     </div>
     <div class="kv-grid">` +
    fieldRow("Клиент", name) +
    fieldRow("Роль", a.role) +
    fieldRow("Ниша", a.niche) +
    fieldRow("Размер компании", a.company_size) +
    fieldRow("Услуга", a.product) +
    fieldRow("Тип задачи", a.task_type) +
    fieldRow("Объём", a.task_volume) +
    fieldRow("Бюджет", a.budget) +
    fieldRow("Срок", a.deadline) +
    fieldRow("О бизнесе", a.business_info) +
    fieldRow("Комментарий", a.comment) +
    `</div>`;
  const contact = [a.contact_method, a.contact_time].filter(Boolean).join(", ");
  $("app-modal-foot").innerHTML = contact
    ? `<div class="contact">📞 Связаться: <b>${esc(contact)}</b></div>`
    : "";
  openModal("app-modal");
}

/* ------------------------------ Статистика -------------------------------- */
function fmtTime(sec) {
  sec = Number(sec) || 0;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return m ? `${m} мин ${s} с` : `${s} с`;
}

async function openStats() {
  openModal("stats-modal");
  const cards = $("stat-cards");
  cards.innerHTML = "Загрузка…";
  try {
    const st = await api.metricsStats();
    cards.innerHTML = [
      ["За день", st.avg_day, st.max_day],
      ["За неделю", st.avg_week, st.max_week],
      ["За месяц", st.avg_month, st.max_month],
    ]
      .map(
        ([label, avg, max]) => `
        <div class="stat-card">
          <div class="stat-label">${label}</div>
          <div class="stat-main">${fmtTime(avg)}</div>
          <div class="stat-sub">макс. ${fmtTime(max)}</div>
        </div>`
      )
      .join("");
    $("heatmap-hint").textContent = `Выборка: ${st.samples} замеров телеметрии.`;
  } catch (e) {
    cards.innerHTML = `<div class="message show err">Ошибка статистики: ${esc(e.message || e)}</div>`;
  }
  try {
    const rows = await api.metricsList(0, 500);
    drawHeatmap(rows);
  } catch (e) {
    $("heatmap-hint").textContent = "Не удалось загрузить точки курсора: " + (e.message || e);
  }
}

function drawHeatmap(rows) {
  const canvas = $("heatmap");
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#fbfaf7";
  ctx.fillRect(0, 0, W, H);

  // Собираем все нормированные позиции курсора из cursor_positions (JSON-строка).
  const points = [];
  for (const r of rows) {
    if (!r.cursor_positions) continue;
    try {
      for (const p of JSON.parse(r.cursor_positions)) {
        if (typeof p.x === "number" && typeof p.y === "number") points.push(p);
      }
    } catch (_) {
      /* битая строка — пропускаем */
    }
  }
  if (!points.length) {
    ctx.fillStyle = "#6b7280";
    ctx.font = "16px Nunito, sans-serif";
    ctx.fillText("Пока нет данных о движении курсора.", 20, 30);
    return;
  }

  // Бакетируем в сетку, чтобы кружки показывали плотность.
  const GX = 40;
  const GY = 22;
  const grid = new Map();
  let maxCount = 0;
  for (const p of points) {
    const gx = Math.min(GX - 1, Math.max(0, Math.floor(p.x * GX)));
    const gy = Math.min(GY - 1, Math.max(0, Math.floor(p.y * GY)));
    const key = `${gx},${gy}`;
    const n = (grid.get(key) || 0) + 1;
    grid.set(key, n);
    if (n > maxCount) maxCount = n;
  }
  const cellW = W / GX;
  const cellH = H / GY;
  for (const [key, n] of grid) {
    const [gx, gy] = key.split(",").map(Number);
    const intensity = n / maxCount; // 0..1
    const radius = Math.max(4, intensity * Math.min(cellW, cellH) * 2.2);
    const cx = gx * cellW + cellW / 2;
    const cy = gy * cellH + cellH / 2;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
    // от синего (холодно) к красному (горячо)
    const hue = 240 - intensity * 240;
    g.addColorStop(0, `hsla(${hue}, 85%, 55%, ${0.25 + intensity * 0.55})`);
    g.addColorStop(1, `hsla(${hue}, 85%, 55%, 0)`);
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

/* ------------------------------ Модалки ----------------------------------- */
function openModal(id) {
  $(id).style.display = "flex";
}
function closeModal(id) {
  $(id).style.display = "none";
}

/* ------------------------------ Экраны ------------------------------------ */
function showPanel() {
  $("login").style.display = "none";
  $("panel").style.display = "block";
  renderServices();
  renderApplications();
}

async function showLogin() {
  $("panel").style.display = "none";
  $("login").style.display = "block";
  // Кнопка регистрации — только если ещё нет ни одного админа.
  try {
    const { has_admin } = await api.authCheck();
    $("register-btn").style.display = has_admin ? "none" : "inline-block";
    $("auth-sub").textContent = has_admin
      ? "Доступ только для администратора."
      : "Администраторов пока нет — зарегистрируйте первого.";
  } catch (_) {
    $("register-btn").style.display = "none";
  }
}

async function onLogin(e) {
  e.preventDefault();
  const btn = $("login-btn");
  btn.disabled = true;
  const user = $("login-user").value.trim();
  const pass = $("login-pass").value;
  try {
    const { token } = await api.login(user, pass);
    setToken(token);
    $("login-form").reset();
    $("login-message").className = "message";
    showPanel();
  } catch (err) {
    clearToken();
    msg("login-message", "err", err.status === 401 ? "Неверный логин или пароль." : "Ошибка входа: " + (err.message || err));
  } finally {
    btn.disabled = false;
  }
}

async function onRegister() {
  const btn = $("register-btn");
  const user = $("login-user").value.trim();
  const pass = $("login-pass").value;
  if (user.length < 3 || pass.length < 6) {
    msg("login-message", "err", "Логин от 3 символов, пароль от 6.");
    return;
  }
  btn.disabled = true;
  try {
    const { token } = await api.register(user, pass);
    setToken(token);
    $("login-form").reset();
    $("login-message").className = "message";
    showPanel();
  } catch (err) {
    msg("login-message", "err", "Не удалось зарегистрировать: " + (err.detail || err.message || err));
  } finally {
    btn.disabled = false;
  }
}

async function onAdd(e) {
  e.preventDefault();
  const btn = $("add-btn");
  const services = $("services").value.trim();
  const budget = $("budget_range").value.trim();
  if (!services || !budget) {
    msg("message", "err", "Заполните оба поля.");
    return;
  }
  btn.disabled = true;
  try {
    await api.createService(services, budget);
    msg("message", "ok", `Услуга «${services}» добавлена.`);
    $("svc-form").reset();
    renderServices();
  } catch (err) {
    msg("message", "err", err.status === 401 ? "Сессия истекла, войдите заново." : "Не удалось добавить: " + (err.message || err));
  } finally {
    btn.disabled = false;
  }
}

function logout(e) {
  e.preventDefault();
  clearToken();
  showLogin();
}

async function init() {
  spawnCircles();
  $("login-form").addEventListener("submit", onLogin);
  $("register-btn").addEventListener("click", onRegister);
  $("svc-form").addEventListener("submit", onAdd);
  $("logout").addEventListener("click", logout);
  $("stats-btn").addEventListener("click", openStats);
  document.querySelectorAll("[data-close]").forEach((b) =>
    b.addEventListener("click", () => closeModal(b.dataset.close))
  );
  document.querySelectorAll(".modal-overlay").forEach((ov) =>
    ov.addEventListener("click", (e) => {
      if (e.target === ov) ov.style.display = "none";
    })
  );

  if (hasToken()) {
    try {
      await api.me();
      showPanel();
      return;
    } catch (_) {
      clearToken();
    }
  }
  showLogin();
}

init();
