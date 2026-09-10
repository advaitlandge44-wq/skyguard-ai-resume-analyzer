/**
 * SkyGuard AI - Unified Frontend API Client
 *
 * Handles HTTP requests to the Render Flask backend with credentials support,
 * error handling, and JSON serialization.
 */
(function() {
  function getBaseUrl() {
    return (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) || window.API_BASE_URL || '';
  }

  function buildUrl(endpoint) {
    const base = getBaseUrl();
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
    return base ? `${base}${cleanEndpoint}` : cleanEndpoint;
  }

  /**
   * Robustly extracts a human-readable error string from any error object,
   * nested structure, validation map, or response payload.
   * Prevents "[object Object]" from ever reaching the UI.
   */
  function extractErrorMessage(source, defaultMsg = 'An unexpected error occurred.') {
    if (!source) return defaultMsg;
    if (typeof source === 'string') {
      const trimmed = source.trim();
      if (!trimmed || trimmed === '[object Object]') return defaultMsg;
      return trimmed;
    }
    if (source instanceof Error) {
      if (source.message && source.message !== '[object Object]' && source.message.trim()) {
        return source.message.trim();
      }
      if (source.data) {
        return extractErrorMessage(source.data, defaultMsg);
      }
    }
    if (typeof source === 'object') {
      if (source.error) {
        return extractErrorMessage(source.error, defaultMsg);
      }
      if (source.message) {
        return extractErrorMessage(source.message, defaultMsg);
      }
      if (source.detail) {
        return extractErrorMessage(source.detail, defaultMsg);
      }
      if (Array.isArray(source.errors) && source.errors.length > 0) {
        const joined = source.errors.map(e => extractErrorMessage(e, '')).filter(Boolean).join('; ');
        if (joined) return joined;
      }
      if (source.errors && typeof source.errors === 'object') {
        const msgs = Object.values(source.errors).flat().map(e => extractErrorMessage(e, '')).filter(Boolean);
        if (msgs.length > 0) return msgs.join('; ');
      }
      if (source.code && source.message) {
        return `${source.message} (${source.code})`;
      }
      if (source.raw && typeof source.raw === 'string' && source.raw.trim()) {
        return extractErrorMessage(source.raw, defaultMsg);
      }
    }
    return defaultMsg;
  }

  async function request(endpoint, options = {}) {
    const url = buildUrl(endpoint);
    const defaultHeaders = {
      'Accept': 'application/json'
    };

    if (!(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      credentials: 'include', // Pass session cookies cross-domain
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        const text = await response.text();
        data = { success: response.ok, raw: text };
      }

      if (!response.ok) {
        const errorMsg = extractErrorMessage(data, `Request failed with status ${response.status}`);
        const err = new Error(errorMsg);
        err.status = response.status;
        err.data = data;
        throw err;
      }

      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  }

  const api = {
    get: (endpoint, params = {}) => {
      let query = '';
      const keys = Object.keys(params);
      if (keys.length > 0) {
        const usp = new URLSearchParams();
        keys.forEach(k => {
          if (params[k] !== undefined && params[k] !== null && params[k] !== '') {
            usp.append(k, params[k]);
          }
        });
        const qs = usp.toString();
        if (qs) query = `?${qs}`;
      }
      return request(`${endpoint}${query}`, { method: 'GET' });
    },

    post: (endpoint, data = {}) => {
      return request(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
      });
    },

    upload: (endpoint, formData) => {
      return request(endpoint, {
        method: 'POST',
        body: formData
      });
    },

    delete: (endpoint) => {
      return request(endpoint, {
        method: 'DELETE'
      });
    },

    // --------------------------------------------------------------------------
    // Specialized Domain Methods
    // --------------------------------------------------------------------------

    auth: {
      me: () => api.get('/api/auth/me'),
      login: (email, password, remember = false) => api.post('/api/auth/login', { email, password, remember }),
      register: (name, email, password, confirm_password) => api.post('/api/auth/register', { name, email, password, confirm_password }),
      logout: () => api.post('/api/auth/logout'),
      forgotPassword: (email) => api.post('/api/auth/forgot-password', { email }),
      resetPassword: (token, password, confirm_password) => api.post(`/api/auth/reset-password/${token}`, { password, confirm_password })
    },

    resume: {
      getRoles: () => api.get('/api/resume/roles'),
      upload: (formData) => api.upload('/api/resume/upload', formData)
    },

    analysis: {
      get: (id) => api.get(`/api/analysis/${id}`),
      delete: (id) => api.post(`/api/analysis/${id}/delete`)
    },

    dashboard: {
      get: () => api.get('/api/dashboard')
    },

    history: {
      get: (q = '', sort = 'date') => api.get('/api/history', { q, sort })
    },

    demo: {
      getData: () => api.get('/api/demo/data')
    },

    chat: {
      send: (analysisId, message) => api.post(`/api/chat/${analysisId}`, { message })
    },

    improver: {
      improve: (bulletText, targetRole = 'Software Engineer') => api.post('/api/improve-bullet', { bullet_text: bulletText, target_role: targetRole })
    },

    extractErrorMessage: extractErrorMessage
  };

  window.SkyGuardAPI = api;
  window.extractErrorMessage = extractErrorMessage;
})();
