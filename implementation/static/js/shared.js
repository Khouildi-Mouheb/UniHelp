// ============================================================
// UniHelp – Shared Utilities
// ============================================================

// ── Toast notification system ────────────────────────────────
const Toast = (() => {
  let container = null;

  function getContainer() {
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * Show a toast notification.
   * @param {string} message
   * @param {'success'|'error'|'info'} type
   * @param {number} duration ms before auto-dismiss
   */
  function show(message, type = 'info', duration = 3500) {
    const c = getContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: '✓', error: '✕', info: 'ℹ' };
    toast.innerHTML = `<span>${icons[type] || icons.info}</span><span>${message}</span>`;

    c.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'toastOut 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  return { show, success: m => show(m, 'success'), error: m => show(m, 'error'), info: m => show(m, 'info') };
})();

// ── API base helper ──────────────────────────────────────────
const API = {
  base: window.location.origin,

  /**
   * Wrapper around fetch with JSON handling and error normalization.
   * @param {string} path      endpoint path (e.g. '/api/chat/ask')
   * @param {object} options   fetch options
   * @returns {Promise<any>}   parsed JSON response
   */
  async request(path, options = {}) {
    const url = `${this.base}${path}`;
    const defaults = {
      headers: { 'Content-Type': 'application/json' },
    };
    const merged = { ...defaults, ...options };
    if (merged.headers && options.headers) {
      merged.headers = { ...defaults.headers, ...options.headers };
    }

    const res = await fetch(url, merged);

    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const err = await res.json();
        detail = err.detail || err.message || detail;
      } catch (_) { /* body not JSON */ }
      throw new Error(detail);
    }

    const ct = res.headers.get('content-type') || '';
    return ct.includes('application/json') ? res.json() : res.text();
  },

  get:  (path)        => API.request(path, { method: 'GET' }),
  post: (path, body)  => API.request(path, { method: 'POST', body: JSON.stringify(body) }),
};

// ── Format helpers ───────────────────────────────────────────
function formatTime(date = new Date()) {
  return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1_048_576) return `${(bytes / 1024).toFixed(1)} Ko`;
  return `${(bytes / 1_048_576).toFixed(1)} Mo`;
}

// ── Active nav link ──────────────────────────────────────────
(function markActiveLink() {
  const current = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === current || (current === '/' && href === '/') || (href !== '/' && current.startsWith(href))) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
})();

// ── Expose globally ──────────────────────────────────────────
window.UniHelp = { Toast, API, formatTime, formatBytes };