// Единая точка обращения к бэкенду. Все пути идут через nginx-прокси /api.
const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail ? JSON.stringify(data.detail) : detail;
    } catch (_) {
      /* тело не JSON — оставляем statusText */
    }
    throw new Error(`HTTP ${res.status}: ${detail}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listServices: () => request("/admin-settings"),
  createService: (services, budget_range) =>
    request("/admin-settings", { method: "POST", body: JSON.stringify({ services, budget_range }) }),
  deleteService: (id) => request(`/admin-settings/${id}`, { method: "DELETE" }),
  createApplication: (payload) =>
    request("/applications", { method: "POST", body: JSON.stringify(payload) }),
  sendMetrics: (payload) =>
    request("/behavior-metrics", { method: "POST", body: JSON.stringify(payload) }),
};
