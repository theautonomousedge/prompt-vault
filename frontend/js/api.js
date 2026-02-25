/**
 * API helper — all backend calls go through here.
 */
const API_BASE = 'http://localhost:8000';

const api = {
  /** Generic fetch wrapper with auth header injection. */
  async request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('token');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, opts);
    if (res.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = 'signup.html?mode=login';
      throw new Error('Unauthorized');
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || 'Request failed');
    }
    return res.json();
  },

  get(path) { return this.request('GET', path); },
  post(path, body) { return this.request('POST', path, body); },
  put(path, body) { return this.request('PUT', path, body); },

  // --- Auth ---
  register(data) { return this.post('/auth/register', data); },
  login(data) { return this.post('/auth/login', data); },

  // --- Profiles ---
  getProfiles(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return this.get(`/profiles${qs ? '?' + qs : ''}`);
  },
  getProfile(id) { return this.get(`/profiles/${id}`); },
  createProfile(data) { return this.post('/profiles', data); },
  updateProfile(id, data) { return this.put(`/profiles/${id}`, data); },

  // --- Transactions ---
  createTransaction(data) { return this.post('/transactions', data); },
  getMyTransactions() { return this.get('/transactions/my'); },

  // --- Dashboard ---
  getDashboardStats() { return this.get('/dashboard/stats'); },

  // --- Admin ---
  getPendingProfiles() { return this.get('/admin/profiles/pending'); },
  approveProfile(id) { return this.post(`/admin/profiles/${id}/approve`, {}); },
  flagProfile(id, reason) { return this.post(`/admin/profiles/${id}/flag`, { reason }); },
  getAdminTransactions() { return this.get('/admin/transactions'); },
  getAdminStats() { return this.get('/admin/stats'); },

  // --- Config ---
  getStripeKey() { return this.get('/config/stripe'); },
};
