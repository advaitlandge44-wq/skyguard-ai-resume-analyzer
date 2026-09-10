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

  const PRODUCTION_BACKEND_URL = 'https://skyguard-ai-resume-analyzer.onrender.com';

  // Resolution order for API Base URL:
  // 1. Explicit runtime environment variable injected via window.ENV_API_BASE_URL
  // 2. Custom override in localStorage for staging / preview deployments
  // 3. Localhost fallback (http://127.0.0.1:5000) during local testing
  // 4. Production Render backend default (https://skyguard-ai-resume-analyzer.onrender.com)
  let apiBaseUrl = '';

  const envUrl = window.ENV_API_BASE_URL;
  const storageUrl = typeof localStorage !== 'undefined' ? localStorage.getItem('SKYGUARD_API_URL') : null;

  if (envUrl && typeof envUrl === 'string' && envUrl.trim() && envUrl !== '[object Object]') {
    apiBaseUrl = envUrl.trim().replace(/\/+$/, '');
  } else if (storageUrl && typeof storageUrl === 'string' && (storageUrl.startsWith('http://') || storageUrl.startsWith('https://')) && storageUrl !== '[object Object]') {
    apiBaseUrl = storageUrl.trim().replace(/\/+$/, '');
  } else if (isLocalhost) {
    apiBaseUrl = 'http://127.0.0.1:5000';
  } else {
    apiBaseUrl = PRODUCTION_BACKEND_URL;
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
