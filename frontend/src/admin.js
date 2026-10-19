import "./styles.css";
import { api } from "./api.js";

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

function showMessage(kind, text) {
  const el = $("message");
  el.className = `message show ${kind}`;
  el.textContent = text;
}

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

async function render() {
  const tbody = $("rows");
  try {
    const items = await api.listServices();
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="4">Услуг пока нет — добавьте первую.</td></tr>';
      return;
    }
    tbody.innerHTML = items
      .map(
        (s) =>
          `<tr>
            <td>${s.id}</td>
            <td>${esc(s.services)}</td>
            <td>${esc(s.budget_range)}</td>
            <td><button class="row-del" data-id="${s.id}">Удалить</button></td>
          </tr>`
      )
      .join("");
    tbody.querySelectorAll(".row-del").forEach((btn) =>
      btn.addEventListener("click", async () => {
        btn.disabled = true;
        try {
          await api.deleteService(btn.dataset.id);
          render();
        } catch (e) {
          showMessage("err", "Не удалось удалить: " + (e.message || e));
          btn.disabled = false;
        }
      })
    );
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4">Ошибка загрузки: ${esc(e.message || e)}</td></tr>`;
  }
}

async function onAdd(e) {
  e.preventDefault();
  const btn = $("add-btn");
  const services = $("services").value.trim();
  const budget = $("budget_range").value.trim();
  if (!services || !budget) {
    showMessage("err", "Заполните оба поля.");
    return;
  }
  btn.disabled = true;
  try {
    await api.createService(services, budget);
    showMessage("ok", `Услуга «${services}» добавлена.`);
    $("svc-form").reset();
    render();
  } catch (err) {
    showMessage("err", "Не удалось добавить: " + (err.message || err));
  } finally {
    btn.disabled = false;
  }
}

spawnCircles();
$("svc-form").addEventListener("submit", onAdd);
render();
