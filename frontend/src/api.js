// Единая точка обращения к бэкенду. Все пути идут через nginx-прокси /api.
const BASE = "/api";
const TOKEN_KEY = "vph06_admin_token"; // JWT администратора

export function setToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token);
}
export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}
export function hasToken() {
  return Boolean(sessionStorage.getItem(TOKEN_KEY));
}

async function request(path, options = {}, auth = false) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (auth) {
    const token = sessionStorage.getItem(TOKEN_KEY);
    if (token) headers.Authorization = `Bearer ${token}`;
  }
  const res = await fetch(BASE + path, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)) : detail;
    } catch (_) {
      /* тело не JSON */
    }
    const err = new Error(`HTTP ${res.status}: ${detail}`);
    err.status = res.status;
    err.detail = detail;
    throw err;
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // --- Публичные (клиентский сайт) ---
  listServices: () => request("/admin-settings"),
  createApplication: (payload) =>
    request("/applications", { method: "POST", body: JSON.stringify(payload) }),
  sendMetrics: (payload) =>
    request("/behavior-metrics", { method: "POST", body: JSON.stringify(payload) }),

  // --- Авторизация ---
  authCheck: () => request("/auth/check"),
  register: (username, password) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ username, password }) }),
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  me: () => request("/auth/me", {}, true),

  // --- Только для администратора (требуют Bearer-токен) ---
  createService: (services, budget_range) =>
    request("/admin-settings", { method: "POST", body: JSON.stringify({ services, budget_range }) }, true),
  updateService: (id, services, budget_range) =>
    request(`/admin-settings/${id}`, { method: "PUT", body: JSON.stringify({ services, budget_range }) }, true),
  deleteService: (id) => request(`/admin-settings/${id}`, { method: "DELETE" }, true),
  listApplications: () => request("/applications", {}, true),
  getApplication: (id) => request(`/applications/${id}`, {}, true),
  metricsList: (skip = 0, limit = 500) => request(`/behavior-metrics?skip=${skip}&limit=${limit}`, {}, true),
  metricsStats: () => request("/behavior-metrics/stats", {}, true),
};
