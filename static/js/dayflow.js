/* ─── DAYFLOW HRMS — Main JS ─────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', function () {

  // ── Sidebar toggle (mobile) ────────────────────────────────────────────────
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar   = document.getElementById('sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          e.target !== toggleBtn) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ── Active nav link highlighting ───────────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.sidebar-nav a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });

  // ── Auto-dismiss alerts ────────────────────────────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.alert-auto-dismiss').forEach(el => {
      try {
        bootstrap.Alert.getOrCreateInstance(el).close();
      } catch (_) {
        el.style.opacity = '0';
        setTimeout(() => el.remove(), 400);
      }
    });
  }, 5000);

  // ── Tooltip init ───────────────────────────────────────────────────────────
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el, { trigger: 'hover' });
  });

  // ── Confirm delete/destructive links ──────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      if (!confirm(this.dataset.confirm || 'Are you sure?')) e.preventDefault();
    });
  });

  // ── Button loading state on form submit ───────────────────────────────────
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function () {
      const btn = this.querySelector('button[type="submit"]');
      if (btn && !btn.dataset.noLoading) {
        setTimeout(() => btn.classList.add('loading'), 50);
      }
    });
  });

  // ── Fade-in for cards and content blocks ──────────────────────────────────
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.06 });

  document.querySelectorAll('.card, .kpi-card').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.animationDelay = `${i * 0.04}s`;
    observer.observe(el);
  });

  // ── Table row hover effect (add cursor pointer to clickable rows) ─────────
  document.querySelectorAll('table tbody tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => window.location = row.dataset.href);
  });

  // ── Progress bars — animate on scroll ────────────────────────────────────
  const barObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const bar = entry.target;
        const target = bar.dataset.width || bar.style.width;
        bar.style.width = '0';
        requestAnimationFrame(() => {
          bar.style.transition = 'width .7s cubic-bezier(.4,0,.2,1)';
          bar.style.width = target;
        });
        barObserver.unobserve(bar);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.progress-bar').forEach(bar => {
    if (bar.style.width) {
      bar.dataset.width = bar.style.width;
      barObserver.observe(bar);
    }
  });

  // ── Smooth dropdown open ──────────────────────────────────────────────────
  document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
      const menu = toggle.nextElementSibling;
      if (menu && menu.classList.contains('dropdown-menu')) {
        menu.style.animation = 'dropIn .15s ease';
      }
    });
  });

  // ── Topbar: Add shadow on scroll ──────────────────────────────────────────
  const topbar = document.querySelector('.topbar');
  if (topbar) {
    window.addEventListener('scroll', () => {
      topbar.style.boxShadow = window.scrollY > 10
        ? '0 2px 12px rgba(0,0,0,.08)'
        : 'none';
    }, { passive: true });
  }

  // ── Select-all checkbox (tables) ──────────────────────────────────────────
  const selectAll = document.getElementById('selectAll');
  if (selectAll) {
    selectAll.addEventListener('change', function () {
      document.querySelectorAll('.row-check').forEach(cb => cb.checked = this.checked);
    });
  }

});

// ── Utility: getCookie (for AJAX CSRF) ────────────────────────────────────────
function getCookie(name) {
  let value = null;
  document.cookie.split(';').forEach(c => {
    const [k, v] = c.trim().split('=');
    if (k === name) value = decodeURIComponent(v);
  });
  return value;
}

// ── Utility: showToast ────────────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer') || (() => {
    const c = document.createElement('div');
    c.id = 'toastContainer';
    c.style.cssText = 'position:fixed;top:76px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px';
    document.body.appendChild(c);
    return c;
  })();

  const colors = {
    success: { bg: '#ecfdf5', border: '#6ee7b7', text: '#065f46', icon: 'fa-circle-check' },
    error:   { bg: '#fef2f2', border: '#fca5a5', text: '#b91c1c', icon: 'fa-circle-xmark' },
    warning: { bg: '#fffbeb', border: '#fcd34d', text: '#92400e', icon: 'fa-triangle-exclamation' },
    info:    { bg: '#eff6ff', border: '#93c5fd', text: '#1d4ed8', icon: 'fa-circle-info' },
  };
  const c = colors[type] || colors.success;

  const toast = document.createElement('div');
  toast.style.cssText = `
    background:${c.bg};border:1px solid ${c.border};color:${c.text};
    border-radius:10px;padding:12px 16px;font-size:.875rem;font-weight:500;
    display:flex;align-items:center;gap:10px;min-width:260px;max-width:360px;
    box-shadow:0 4px 16px rgba(0,0,0,.1);
    animation:fadeSlideIn .25s ease;
  `;
  toast.innerHTML = `<i class="fa-solid ${c.icon}"></i><span>${message}</span>
    <button onclick="this.parentElement.remove()" style="margin-left:auto;border:none;background:none;color:inherit;cursor:pointer;opacity:.6;padding:2px 4px;font-size:1rem">&times;</button>`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'fadeOut .3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
