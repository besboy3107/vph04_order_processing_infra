// Считывание поведения пользователя: время на странице, клики, наведения, возвраты.
// Данные отправляются вместе с заявкой (1:1 к ней) после успешной отправки формы.
export function createTracker() {
  const start = Date.now();
  let clicks = 0;
  let hovers = 0;
  let returns = 0;
  const buttons = {};

  document.addEventListener("click", (e) => {
    clicks += 1;
    const t = e.target.closest("button, a, input[type=submit]");
    if (t) {
      const key = (t.id || t.name || t.textContent || "el").trim().slice(0, 40);
      buttons[key] = (buttons[key] || 0) + 1;
    }
  });

  document.addEventListener("mouseover", (e) => {
    if (e.target.closest("input, select, textarea, button")) hovers += 1;
  });

  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") returns += 1;
  });

  return {
    snapshot() {
      return {
        time_on_page: Math.round((Date.now() - start) / 1000),
        clicks,
        hovers,
        returns,
        details: { buttons, user_agent: navigator.userAgent.slice(0, 120) },
      };
    },
  };
}
