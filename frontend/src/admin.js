import "./styles.css";
import { api, setAuth, clearAuth, hasAuth } from "./api.js";

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

/* --- Услуги --- */
async function renderServices() {
  const tbody = $("rows");
  try {
    const items = await api.listServices();
    tbody.innerHTML = items.length
      ? items
          .map(
            (s) =>
              `<tr><td>${s.id}</td><td>${esc(s.services)}</td><td>${esc(s.budget_range)}</td>
               <td><button class="row-del" data-id="${s.id}">Удалить</button></td></tr>`
          )
          .join("")
      : '<tr><td colspan="4">Услуг пока нет — добавьте первую.</td></tr>';
    tbody.querySelectorAll(".row-del").forEach((btn) =>
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
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4">Ошибка: ${esc(e.message || e)}</td></tr>`;
  }
}

/* --- Заявки (защищённое чтение) --- */
async function renderApplications() {
  const tbody = $("app-rows");
  try {
    const items = await api.listApplications();
    tbody.innerHTML = items.length
      ? items
          .map((a) => {
            const name = [a.last_name, a.first_name, a.middle_name].filter(Boolean).join(" ");
            const contact = [a.contact_method, a.contact_time].filter(Boolean).join(", ");
            return `<tr><td>${a.id}</td><td>${esc(name)}</td><td>${esc(a.product)}</td>
                    <td>${esc(a.budget)}</td><td>${esc(contact)}</td></tr>`;
          })
          .join("")
      : '<tr><td colspan="5">Заявок пока нет.</td></tr>';
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5">Ошибка: ${esc(e.message || e)}</td></tr>`;
  }
}

function showPanel() {
  $("login").style.display = "none";
  $("panel").style.display = "block";
  renderServices();
  renderApplications();
}

function showLogin() {
  $("panel").style.display = "none";
  $("login").style.display = "block";
}

/* --- Вход --- */
async function onLogin(e) {
  e.preventDefault();
  const btn = $("login-btn");
  btn.disabled = true;
  setAuth($("login-user").value.trim(), $("login-pass").value);
  try {
    await api.checkAdmin();
    $("login-form").reset();
    $("login-message").className = "message";
    showPanel();
  } catch (err) {
    clearAuth();
    msg("login-message", "err", err.status === 401 ? "Неверный логин или пароль." : "Ошибка входа: " + (err.message || err));
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
  clearAuth();
  showLogin();
}

async function init() {
  spawnCircles();
  $("login-form").addEventListener("submit", onLogin);
  $("svc-form").addEventListener("submit", onAdd);
  $("logout").addEventListener("click", logout);
  // Если уже есть сохранённые данные входа — проверяем их молча.
  if (hasAuth()) {
    try {
      await api.checkAdmin();
      showPanel();
      return;
    } catch (_) {
      clearAuth();
    }
  }
  showLogin();
}

init();
