/**
 * Auth helpers — token management, current user state, nav updates.
 */
const auth = {
  getToken() {
    return localStorage.getItem('token');
  },

  getUser() {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  },

  isLoggedIn() {
    return !!this.getToken();
  },

  isAdmin() {
    const user = this.getUser();
    return user && user.user_type === 'admin';
  },

  save(data) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify({
      user_id: data.user_id,
      user_type: data.user_type,
      display_name: data.display_name,
    }));
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
  },

  /** Update the navbar auth section based on login state. */
  updateNav() {
    const authArea = document.getElementById('navbar-auth');
    if (!authArea) return;

    if (this.isLoggedIn()) {
      const user = this.getUser();
      let links = `
        <a href="dashboard.html" class="btn btn-sm btn-secondary">Dashboard</a>
        <span class="text-muted" style="font-size:0.85rem">Hi, ${this.escapeHtml(user.display_name)}</span>
        <a href="#" onclick="auth.logout(); return false;" class="btn btn-sm btn-secondary">Logout</a>
      `;
      if (this.isAdmin()) {
        links = `<a href="admin.html" class="btn btn-sm btn-secondary">Admin</a>` + links;
      }
      authArea.innerHTML = links;
    } else {
      authArea.innerHTML = `
        <a href="signup.html?mode=login" class="btn btn-sm btn-secondary">Log In</a>
        <a href="signup.html" class="btn btn-sm btn-primary">Sign Up</a>
      `;
    }
  },

  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  /** Require login — redirect if not authenticated. */
  requireLogin() {
    if (!this.isLoggedIn()) {
      window.location.href = 'signup.html?mode=login';
      return false;
    }
    return true;
  },

  requireAdmin() {
    if (!this.isAdmin()) {
      window.location.href = 'index.html';
      return false;
    }
    return true;
  },
};

// Update nav on every page load
document.addEventListener('DOMContentLoaded', () => auth.updateNav());
