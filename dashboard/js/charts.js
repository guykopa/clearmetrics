'use strict';

const API_BASE = 'http://localhost:8000';
const PALETTE = ['#38bdf8','#818cf8','#34d399','#fb923c','#f472b6','#a78bfa','#4ade80','#facc15'];

let token = null;
let currentRole = null;
let charts = {};
let metricsData = [];

function setStatus(msg) {
  document.getElementById('status-bar').textContent = msg;
}

async function login() {
  const userId = document.getElementById('user-id').value.trim();
  const role = document.getElementById('role').value;
  const errEl = document.getElementById('error-msg');
  errEl.style.display = 'none';

  try {
    const res = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, role }),
    });
    if (!res.ok) throw new Error('Authentication failed');
    const data = await res.json();
    token = data.access_token;
    currentRole = role;
    document.getElementById('user-info').textContent = `${userId} · ${role}`;
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    await loadData();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.style.display = 'block';
  }
}

function logout() {
  token = null;
  currentRole = null;
  metricsData = [];
  Object.values(charts).forEach(c => c.destroy());
  charts = {};
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('login-screen').style.display = 'flex';
  document.getElementById('user-info').textContent = '';
  setStatus('Ready');
}

async function loadData() {
  if (!token) return;
  setStatus('Loading…');

  const params = new URLSearchParams();
  const from = document.getElementById('filter-from').value;
  const to = document.getElementById('filter-to').value;
  const account = document.getElementById('filter-account').value.trim();
  if (from) params.set('from', from);
  if (to) params.set('to', to);
  if (account) params.set('account_id', account);

  try {
    const res = await fetch(`${API_BASE}/api/metrics?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    metricsData = await res.json();
    renderDashboard(metricsData);
    setStatus(`Loaded ${metricsData.length} metrics — ${new Date().toLocaleTimeString()}`);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}

function renderDashboard(data) {
  updateKPIs(data);
  renderBarChart(data);
  renderDoughnutChart(data);
  renderLineChart(data);
}

function updateKPIs(data) {
  const total = data.length;
  const totalValue = data.reduce((s, m) => s + m.value, 0);
  const uniqueNames = new Set(data.map(m => m.name)).size;
  document.getElementById('kpi-total').textContent = total;
  document.getElementById('kpi-value').textContent = totalValue.toLocaleString('en-US', { maximumFractionDigits: 2 });
  document.getElementById('kpi-names').textContent = uniqueNames;
}

function renderBarChart(data) {
  const grouped = {};
  data.forEach(m => { grouped[m.name] = (grouped[m.name] || 0) + m.value; });
  const labels = Object.keys(grouped);
  const values = Object.values(grouped);

  if (charts.bar) charts.bar.destroy();
  charts.bar = new Chart(document.getElementById('chart-bar'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{ label: 'Value', data: values, backgroundColor: PALETTE }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
      },
    },
  });
}

function renderDoughnutChart(data) {
  const grouped = {};
  data.forEach(m => { grouped[m.name] = (grouped[m.name] || 0) + m.value; });
  const labels = Object.keys(grouped);
  const values = Object.values(grouped);

  if (charts.doughnut) charts.doughnut.destroy();
  charts.doughnut = new Chart(document.getElementById('chart-doughnut'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{ data: values, backgroundColor: PALETTE }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } },
    },
  });
}

function renderLineChart(data) {
  const sorted = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const labels = sorted.map(m => new Date(m.timestamp).toLocaleDateString());
  const values = sorted.map(m => m.value);

  if (charts.line) charts.line.destroy();
  charts.line = new Chart(document.getElementById('chart-line'), {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Value over time',
        data: values,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56,189,248,0.1)',
        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#38bdf8',
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#94a3b8' } } },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
      },
    },
  });
}

function exportCSV() {
  if (!metricsData.length) { setStatus('No data to export'); return; }
  const headers = ['name', 'value', 'unit', 'timestamp'];
  const rows = metricsData.map(m => headers.map(h => m[h]).join(','));
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `clearmetrics-export-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  setStatus('Export done');
}
