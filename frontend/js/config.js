/**
 * SkyGuard AI - Frontend Configuration
 * 
 * Dynamic API Base URL management supporting both local development
 * and production Render backend deployments.
 */
(function() {
  // Determine if running in local development
  const isLocalhost = Boolean(
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '[::1]' ||
    window.location.protocol === 'file:'
  );

  // Resolution order for API Base URL:
  // 1. Explicit runtime environment variable injected via window.ENV_API_BASE_URL
  // 2. Custom override in localStorage for staging / preview deployments
  // 3. Localhost fallback (http://127.0.0.1:5000) during local testing
  // 4. Relative URL ('') if deployed on same origin or production default
  let apiBaseUrl = '';

  if (window.ENV_API_BASE_URL && typeof window.ENV_API_BASE_URL === 'string') {
    apiBaseUrl = window.ENV_API_BASE_URL.replace(/\/+$/, '');
  } else if (localStorage.getItem('SKYGUARD_API_URL')) {
    apiBaseUrl = localStorage.getItem('SKYGUARD_API_URL').replace(/\/+$/, '');
  } else if (isLocalhost) {
    apiBaseUrl = 'http://127.0.0.1:5000';
  } else {
    // Production Render backend placeholder / relative fallback
    // Configure window.ENV_API_BASE_URL in your HTML or deployment settings
    apiBaseUrl = window.ENV_API_BASE_URL || '';
  }

  window.APP_CONFIG = {
    API_BASE_URL: apiBaseUrl,
    IS_LOCAL: isLocalhost,
    APP_NAME: 'SkyGuard AI',
    VERSION: '2.0.0',
    setApiUrl: function(url) {
      if (url) {
        localStorage.setItem('SKYGUARD_API_URL', url.replace(/\/+$/, ''));
        window.APP_CONFIG.API_BASE_URL = url.replace(/\/+$/, '');
      } else {
        localStorage.removeItem('SKYGUARD_API_URL');
      }
    }
  };

  // Expose global API_BASE_URL for quick access
  window.API_BASE_URL = window.APP_CONFIG.API_BASE_URL;
})();
