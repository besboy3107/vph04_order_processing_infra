// Единая точка обращения к бэкенду. Все пути идут через nginx-прокси /api.
const BASE = "/api";
const AUTH_KEY = "vph05_admin_auth"; // base64("user:pass") для HTTP Basic

export function setAuth(user, password) {
  const token = btoa(unescape(encodeURIComponent(`${user}:${password}`)));
  sessionStorage.setItem(AUTH_KEY, token);
}
export function clearAuth() {
  sessionStorage.removeItem(AUTH_KEY);
}
export function hasAuth() {
  return Boolean(sessionStorage.getItem(AUTH_KEY));
}

async function request(path, options = {}, auth = false) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (auth) {
    const token = sessionStorage.getItem(AUTH_KEY);
    if (token) headers.Authorization = `Basic ${token}`;
  }
  const res = await fetch(BASE + path, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail ? JSON.stringify(data.detail) : detail;
    } catch (_) {
      /* тело не JSON */
    }
    const err = new Error(`HTTP ${res.status}: ${detail}`);
    err.status = res.status;
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

  // --- Только для администратора (требуют Basic-авторизации) ---
  checkAdmin: () => request("/admin/check", {}, true),
  createService: (services, budget_range) =>
    request("/admin-settings", { method: "POST", body: JSON.stringify({ services, budget_range }) }, true),
  deleteService: (id) => request(`/admin-settings/${id}`, { method: "DELETE" }, true),
  listApplications: () => request("/applications", {}, true),
};
