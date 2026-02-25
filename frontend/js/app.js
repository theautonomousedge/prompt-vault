/**
 * Main app logic — page-specific initialisation keyed off body data-page.
 */
document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;
  if (page && pages[page]) pages[page]();

  // Mobile nav toggle
  const toggle = document.querySelector('.mobile-toggle');
  const navLinks = document.querySelector('.navbar-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => navLinks.classList.toggle('open'));
  }
});

/* ============================================================
   Utility helpers
   ============================================================ */

function $(sel, root = document) { return root.querySelector(sel); }
function $$(sel, root = document) { return [...root.querySelectorAll(sel)]; }

function showAlert(container, msg, type = 'error') {
  const el = document.createElement('div');
  el.className = `alert alert-${type}`;
  el.textContent = msg;
  container.prepend(el);
  setTimeout(() => el.remove(), 5000);
}

function formatCurrency(n) {
  return '$' + Number(n).toFixed(2);
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str || '';
  return div.innerHTML;
}

/* ============================================================
   Animated counters (landing page)
   ============================================================ */

function animateCounter(el, target, duration = 2000) {
  let start = 0;
  const step = (ts) => {
    if (!start) start = ts;
    const progress = Math.min((ts - start) / duration, 1);
    el.textContent = Math.floor(progress * target).toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* ============================================================
   Page handlers
   ============================================================ */
const pages = {};

/* ---------- Landing ---------- */
pages.landing = async () => {
  // Animate stats
  $$('.stat-number[data-target]').forEach(el => {
    animateCounter(el, parseInt(el.dataset.target, 10));
  });

  // Load featured profiles
  try {
    const data = await api.getProfiles({ per_page: 3 });
    const grid = $('#featured-profiles');
    if (grid && data.profiles.length) {
      grid.innerHTML = data.profiles.map(profileCardHtml).join('');
    }
  } catch (e) {
    // Silently fail on landing — profiles may not be available yet
  }
};

/* ---------- Browse ---------- */
pages.browse = async () => {
  const grid = $('#profiles-grid');
  const paginationEl = $('#pagination');
  let currentPage = 1;

  async function load() {
    grid.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';
    try {
      const params = { page: currentPage, per_page: 12 };
      const city = $('#filter-city')?.value;
      const state = $('#filter-state')?.value;
      const sort = $('#filter-sort')?.value;
      const search = $('#search-input')?.value;
      if (city) params.city = city;
      if (state) params.state = state;
      if (sort) params.sort = sort;
      if (search) params.search = search;

      const data = await api.getProfiles(params);
      if (!data.profiles.length) {
        grid.innerHTML = '<div class="empty-state"><h3>No profiles found</h3><p>Try adjusting your filters.</p></div>';
        paginationEl.innerHTML = '';
        return;
      }
      grid.innerHTML = data.profiles.map(profileCardHtml).join('');
      renderPagination(paginationEl, data.total, data.per_page, currentPage, (p) => { currentPage = p; load(); });
    } catch (e) {
      grid.innerHTML = `<div class="alert alert-error">${escapeHtml(e.message)}</div>`;
    }
  }

  // Filter / search listeners
  $$('.filters-bar .form-control, .filters-bar input').forEach(el => {
    el.addEventListener('change', () => { currentPage = 1; load(); });
  });
  $('#search-input')?.addEventListener('keyup', debounce(() => { currentPage = 1; load(); }, 400));

  load();
};

/* ---------- Profile ---------- */
pages.profile = async () => {
  const id = new URLSearchParams(location.search).get('id');
  if (!id) { window.location.href = 'browse.html'; return; }

  try {
    const p = await api.getProfile(id);
    $('#profile-name').textContent = p.display_name;
    $('#profile-location').textContent = `${p.city}, ${p.state}`;
    $('#profile-story').textContent = p.story;
    $('#profile-member-since').textContent = p.member_since;
    $('#profile-meals').textContent = p.meals_received;
    if (p.is_verified) {
      $('#verified-badge').classList.remove('hidden');
    }
    $('#send-meal-btn').href = `donate.html?receiver_id=${p.user_id}&name=${encodeURIComponent(p.display_name)}&city=${encodeURIComponent(p.city)}`;
  } catch (e) {
    showAlert($('.page-content'), e.message);
  }
};

/* ---------- Donate ---------- */
pages.donate = async () => {
  const params = new URLSearchParams(location.search);
  const receiverId = params.get('receiver_id');
  const receiverName = params.get('name') || 'Someone';
  const receiverCity = params.get('city') || '';

  if (!receiverId) { window.location.href = 'browse.html'; return; }

  $('#recipient-name').textContent = receiverName;
  $('#recipient-city').textContent = receiverCity;
  $('#summary-recipient').textContent = `${receiverName} in ${receiverCity}`;

  let selectedAmount = 25;
  let selectedDelivery = 'doordash';
  let tipPercent = 12;

  // Amount selection
  $$('.amount-option').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.amount-option').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedAmount = parseFloat(btn.dataset.amount);
      $('#custom-amount').value = '';
      updateSummary();
    });
  });

  $('#custom-amount')?.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    if (val > 0) {
      $$('.amount-option').forEach(b => b.classList.remove('selected'));
      selectedAmount = val;
      updateSummary();
    }
  });

  // Delivery selection
  $$('.delivery-option').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.delivery-option').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      selectedDelivery = btn.dataset.method;
    });
  });

  // Tip selection
  $$('.tip-option').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.tip-option').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      tipPercent = parseFloat(btn.dataset.tip);
      updateSummary();
    });
  });

  function updateSummary() {
    const tip = (selectedAmount * tipPercent / 100);
    const total = selectedAmount + tip;
    $('#summary-amount').textContent = formatCurrency(selectedAmount);
    $('#summary-tip').textContent = formatCurrency(tip);
    $('#summary-total').textContent = formatCurrency(total);
  }

  // Default state
  $(`.amount-option[data-amount="25"]`)?.classList.add('selected');
  $(`.delivery-option[data-method="doordash"]`)?.classList.add('selected');
  $(`.tip-option[data-tip="12"]`)?.classList.add('selected');
  updateSummary();

  // Submit
  $('#donate-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!auth.requireLogin()) return;

    const submitBtn = $('#donate-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    try {
      const tip = (selectedAmount * tipPercent / 100);
      const result = await api.createTransaction({
        receiver_id: receiverId,
        amount: selectedAmount,
        tip_amount: parseFloat(tip.toFixed(2)),
        delivery_method: selectedDelivery,
        message: $('#donate-message')?.value || null,
      });

      if (result.session_url) {
        window.location.href = result.session_url;
      } else {
        // Demo mode — show confirmation
        $('#donate-form-section').classList.add('hidden');
        $('#order-summary-section').classList.add('hidden');
        $('#confirmation-section').classList.remove('hidden');
        $('#confirm-name').textContent = receiverName;
        $('#confirm-city').textContent = receiverCity;
      }
    } catch (err) {
      showAlert($('#donate-form'), err.message);
      submitBtn.disabled = false;
      submitBtn.textContent = 'Send Meal Now';
    }
  });
};

/* ---------- Signup / Login ---------- */
pages.signup = () => {
  const mode = new URLSearchParams(location.search).get('mode');
  if (mode === 'login') {
    $('#signup-section')?.classList.add('hidden');
    $('#login-section')?.classList.remove('hidden');
    document.title = 'Log In — Prompt Vault';
  }

  // Toggle between forms
  $('#show-login')?.addEventListener('click', (e) => {
    e.preventDefault();
    $('#signup-section').classList.add('hidden');
    $('#login-section').classList.remove('hidden');
  });
  $('#show-signup')?.addEventListener('click', (e) => {
    e.preventDefault();
    $('#login-section').classList.add('hidden');
    $('#signup-section').classList.remove('hidden');
  });

  // Register
  $('#register-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;

    try {
      const data = {
        email: form.email.value,
        password: form.password.value,
        display_name: form.display_name.value,
        phone: form.phone?.value || null,
        user_type: form.user_type.value,
      };
      const result = await api.register(data);
      auth.save(result);

      if (data.user_type === 'receiver') {
        $('#signup-section').classList.add('hidden');
        $('#profile-setup-section').classList.remove('hidden');
      } else {
        window.location.href = 'browse.html';
      }
    } catch (err) {
      showAlert(form, err.message);
      btn.disabled = false;
    }
  });

  // Profile setup (receiver)
  $('#profile-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;

    try {
      await api.createProfile({
        city: form.city.value,
        state: form.state.value,
        story: form.story.value,
        street: form.street.value,
        zip_code: form.zip_code.value,
      });
      window.location.href = 'browse.html';
    } catch (err) {
      showAlert(form, err.message);
      btn.disabled = false;
    }
  });

  // Login
  $('#login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;

    try {
      const result = await api.login({
        email: form.email.value,
        password: form.password.value,
      });
      auth.save(result);
      window.location.href = 'browse.html';
    } catch (err) {
      showAlert(form, err.message);
      btn.disabled = false;
    }
  });
};

/* ---------- Dashboard ---------- */
pages.dashboard = async () => {
  if (!auth.requireLogin()) return;

  try {
    const stats = await api.getDashboardStats();
    $('#stat-meals').textContent = stats.total_meals;
    $('#stat-given').textContent = formatCurrency(stats.total_given);
    $('#stat-families').textContent = stats.families_helped;

    const feed = $('#activity-feed');
    if (stats.recent_transactions.length) {
      feed.innerHTML = stats.recent_transactions.map(t => `
        <div class="activity-item">
          <div class="activity-icon">&#127858;</div>
          <div class="activity-details">
            <div class="activity-text">
              Sent ${formatCurrency(t.amount)} meal to <strong>${escapeHtml(t.receiver_name)}</strong> in ${escapeHtml(t.receiver_city)}
            </div>
            <div class="activity-date">${formatDate(t.created_at)} &middot; ${t.delivery_method} &middot; <span class="status-badge ${t.status}">${t.status}</span></div>
          </div>
        </div>
      `).join('');
    } else {
      feed.innerHTML = '<div class="empty-state"><h3>No meals sent yet</h3><p><a href="browse.html">Browse profiles</a> to send your first meal!</p></div>';
    }
  } catch (e) {
    showAlert($('.page-content'), e.message);
  }
};

/* ---------- Admin ---------- */
pages.admin = async () => {
  if (!auth.requireAdmin()) return;

  const tabs = $$('.admin-tab');
  const panels = $$('.admin-panel');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      panels.forEach(p => p.classList.add('hidden'));
      tab.classList.add('active');
      $(`#panel-${tab.dataset.panel}`).classList.remove('hidden');
    });
  });

  loadAdminPending();
  loadAdminTransactions();
  loadAdminStats();
};

async function loadAdminPending() {
  const tbody = $('#pending-tbody');
  try {
    const profiles = await api.getPendingProfiles();
    if (!profiles.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No pending profiles</td></tr>';
      return;
    }
    tbody.innerHTML = profiles.map(p => `
      <tr>
        <td>${escapeHtml(p.display_name)}</td>
        <td>${escapeHtml(p.city)}, ${escapeHtml(p.state)}</td>
        <td>${escapeHtml(p.story.substring(0, 80))}...</td>
        <td>${p.member_since}</td>
        <td>
          <button class="btn btn-sm btn-success" onclick="adminApprove('${p.id}')">Approve</button>
          <button class="btn btn-sm btn-danger" onclick="adminFlag('${p.id}')">Flag</button>
        </td>
      </tr>
    `).join('');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5" class="alert-error">${escapeHtml(e.message)}</td></tr>`;
  }
}

async function loadAdminTransactions() {
  const tbody = $('#transactions-tbody');
  try {
    const txns = await api.getAdminTransactions();
    if (!txns.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No transactions</td></tr>';
      return;
    }
    tbody.innerHTML = txns.map(t => `
      <tr>
        <td>${escapeHtml(t.giver_name)}</td>
        <td>${escapeHtml(t.receiver_name)}</td>
        <td>${formatCurrency(t.amount)}</td>
        <td>${t.delivery_method}</td>
        <td><span class="status-badge ${t.status}">${t.status}</span></td>
        <td>${formatDate(t.created_at)}</td>
      </tr>
    `).join('');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="6" class="alert-error">${escapeHtml(e.message)}</td></tr>`;
  }
}

async function loadAdminStats() {
  try {
    const s = await api.getAdminStats();
    $('#admin-users').textContent = s.total_users;
    $('#admin-profiles').textContent = s.total_profiles;
    $('#admin-txns').textContent = s.total_transactions;
    $('#admin-amount').textContent = formatCurrency(s.total_amount);
    $('#admin-pending').textContent = s.pending_profiles;
    $('#admin-flagged').textContent = s.flagged_profiles;
  } catch (e) { /* ignore */ }
}

async function adminApprove(id) {
  try {
    await api.approveProfile(id);
    loadAdminPending();
  } catch (e) {
    alert(e.message);
  }
}

async function adminFlag(id) {
  const reason = prompt('Reason for flagging:');
  if (reason === null) return;
  try {
    await api.flagProfile(id, reason);
    loadAdminPending();
  } catch (e) {
    alert(e.message);
  }
}

/* ============================================================
   Shared HTML generators
   ============================================================ */

function profileCardHtml(p) {
  return `
    <div class="card profile-card">
      <div class="profile-name">${escapeHtml(p.display_name)}
        ${p.is_verified ? '<span class="verified-badge">&#10003; Verified</span>' : ''}
      </div>
      <div class="profile-location">&#128205; ${escapeHtml(p.city)}, ${escapeHtml(p.state)}</div>
      <div class="profile-story">${escapeHtml(p.story)}</div>
      <div class="profile-footer">
        <span class="meals-count">${p.meals_received} meals received</span>
        <a href="profile.html?id=${p.id}" class="btn btn-sm btn-primary">Send a Meal</a>
      </div>
    </div>
  `;
}

/* ============================================================
   Pagination renderer
   ============================================================ */

function renderPagination(container, total, perPage, current, onPageClick) {
  const totalPages = Math.ceil(total / perPage);
  if (totalPages <= 1) { container.innerHTML = ''; return; }

  let html = '';
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="${i === current ? 'active' : ''}" data-page="${i}">${i}</button>`;
  }
  container.innerHTML = html;
  container.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', () => onPageClick(parseInt(btn.dataset.page, 10)));
  });
}

/* ============================================================
   Debounce helper
   ============================================================ */

function debounce(fn, ms) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
