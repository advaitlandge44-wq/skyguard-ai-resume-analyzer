/**
 * SkyGuard AI - Core Client Utilities & Interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  // Public mobile navigation toggle
  const publicToggle = document.getElementById('public-mobile-toggle');
  const publicNavLinks = document.getElementById('public-nav-links');

  if (publicToggle && publicNavLinks) {
    publicToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      publicNavLinks.classList.toggle('open');
    });
  }

  // Authenticated sidebar toggle for tablet/mobile
  const sidebarToggle = document.getElementById('sidebar-toggle-btn');
  const appSidebar = document.getElementById('app-sidebar');

  if (sidebarToggle && appSidebar) {
    sidebarToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      appSidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (!appSidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        appSidebar.classList.remove('open');
      }
    });
  }

  // Alert dismiss buttons
  const alertCloseBtns = document.querySelectorAll('.alert-close');
  alertCloseBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const alert = e.target.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        setTimeout(() => alert.remove(), 200);
      }
    });
  });
});

/**
 * Gets the CSRF token from the meta tag
 */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

/**
 * Displays a toast notification in the UI
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.position = 'fixed';
    container.style.bottom = '24px';
    container.style.right = '24px';
    container.style.zIndex = '99999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '8px';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `alert alert-${type}`;
  toast.style.boxShadow = '0 10px 30px rgba(0,0,0,0.6)';
  toast.style.margin = '0';
  toast.innerHTML = `
    <span>${message}</span>
    <button type="button" class="alert-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}
