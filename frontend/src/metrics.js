// Сбор анонимной телеметрии клиентского сайта и отправка раз в секунду.
// Копим: время на странице (сек), нажатые кнопки, позиции курсора, число
// возвратов на вкладку. Каждую секунду шлём POST /api/behavior-metrics.
import { api } from "./api.js";

export function startMetrics({ intervalMs = 1000 } = {}) {
  const start = Date.now();
  const buttons = {}; // подпись элемента -> счётчик кликов
  const cursor = []; // накопленные позиции курсора [{x,y,t}]
  let returns = 0;
  let lastX = 0;
  let lastY = 0;

  document.addEventListener("click", (e) => {
    const t = e.target.closest("button, a, input[type=submit], select");
    const key = t ? (t.id || t.name || (t.textContent || "").trim() || t.tagName).slice(0, 40) : "page";
    buttons[key] = (buttons[key] || 0) + 1;
  });

  document.addEventListener("mousemove", (e) => {
    lastX = e.clientX;
    lastY = e.clientY;
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") returns += 1;
  });

  // Раз в секунду снимаем позицию курсора (нормированную 0..1, чтобы heatmap
  // не зависел от разрешения экрана) и отправляем накопленное.
  const timer = setInterval(() => {
    const w = window.innerWidth || 1;
    const h = window.innerHeight || 1;
    cursor.push({ x: +(lastX / w).toFixed(4), y: +(lastY / h).toFixed(4), t: Math.round((Date.now() - start) / 1000) });

    const payload = {
      application_id: 0,
      time_on_page: Math.round((Date.now() - start) / 1000),
      buttons_clicked: JSON.stringify(buttons),
      cursor_positions: JSON.stringify(cursor),
      return_frequency: returns,
    };
    api.sendMetrics(payload).catch(() => {
      /* телеметрия не критична для пользователя — молча игнорируем сбой */
    });
  }, intervalMs);

  window.addEventListener("beforeunload", () => clearInterval(timer));
  return { stop: () => clearInterval(timer) };
}
