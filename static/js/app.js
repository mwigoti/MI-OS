// MwohaOS Client Application Support
document.addEventListener("DOMContentLoaded", () => {
  // Global CSRF configuration for HTMX
  document.body.addEventListener("htmx:configRequest", (evt) => {
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    if (csrfToken) {
      evt.detail.headers["X-CSRFToken"] = csrfToken;
    }
  });
});
