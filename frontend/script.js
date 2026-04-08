/* Traffic Analyzer – Frontend JavaScript */
'use strict';

const API = window.location.origin;

// ---------------------------------------------------------------------------
// Security helper – escape HTML to prevent XSS
// ---------------------------------------------------------------------------

function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API}/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

function setLoading(btnId, spinnerId, loading) {
  const btn = document.getElementById(btnId);
  const spinner = document.getElementById(spinnerId);
  const text = btn?.querySelector('.btn-text');
  if (!btn) return;
  btn.disabled = loading;
  spinner?.classList.toggle('hidden', !loading);
  if (text) text.textContent = loading ? 'Thinking…' : btn.dataset.label || text.textContent;
}

function showCard(cardId) {
  const card = document.getElementById(cardId);
  if (card) card.classList.remove('hidden');
}

function hideCard(cardId) {
  const card = document.getElementById(cardId);
  if (card) card.classList.add('hidden');
}

function toast(msg, type = 'info') {
  const colours = { info: '#89b4fa', success: '#a6e3a1', error: '#f38ba8' };
  const t = document.createElement('div');
  t.textContent = msg;
  Object.assign(t.style, {
    position: 'fixed', bottom: '1.5rem', right: '1.5rem',
    background: colours[type] || colours.info,
    color: '#1e1e2e', padding: '.75rem 1.25rem',
    borderRadius: '8px', fontWeight: '600',
    boxShadow: '0 4px 20px rgba(0,0,0,.4)',
    zIndex: '9999', maxWidth: '320px',
    animation: 'fadeIn .3s ease',
  });
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// ---------------------------------------------------------------------------
// API Health check
// ---------------------------------------------------------------------------

async function checkApiStatus() {
  const dot = document.getElementById('apiStatus');
  const txt = document.getElementById('apiStatusText');
  try {
    await apiFetch('/health');
    if (dot) { dot.classList.add('online'); }
    if (txt) txt.textContent = 'API Online';
  } catch {
    if (dot) dot.classList.remove('online');
    if (txt) txt.textContent = 'API Offline';
  }
}

// ---------------------------------------------------------------------------
// Results rendering
// ---------------------------------------------------------------------------

function renderResults(data, title = 'Analysis Results') {
  showCard('resultsCard');
  document.getElementById('resultsTitle').textContent = title;

  // Congestion badge
  const congestion = data.congestion_level;
  const badge = document.getElementById('congestionBadge');
  if (congestion && congestion !== 'unknown') {
    badge.className = `congestion-badge congestion-${congestion}`;
    document.getElementById('congestionLabel').textContent =
      `🚦 ${congestion.charAt(0).toUpperCase() + congestion.slice(1)} Congestion`;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }

  // Delay
  const delay = data.estimated_delay;
  const delayEl = document.getElementById('delayInfo');
  if (delay != null && delay > 0) {
    document.getElementById('delayValue').textContent = delay;
    delayEl.classList.remove('hidden');
  } else {
    delayEl.classList.add('hidden');
  }

  // Analysis text
  document.getElementById('analysisBox').textContent = data.analysis || '';

  // Recommendations
  const recs = data.recommendations || [];
  const recBox = document.getElementById('recommendationsBox');
  const recList = document.getElementById('recommendationsList');
  if (recs.length) {
    recList.innerHTML = recs.map(r => `<li>${r}</li>`).join('');
    recBox.classList.remove('hidden');
  } else {
    recBox.classList.add('hidden');
  }

  // Scroll into view
  document.getElementById('resultsCard').scrollIntoView({ behavior: 'smooth' });
}

function closeResults() {
  hideCard('resultsCard');
}

// ---------------------------------------------------------------------------
// Analyze Traffic form
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  const analyzeForm = document.getElementById('analyzeForm');
  if (analyzeForm) {
    analyzeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('analyzeBtn');
      btn.dataset.label = 'Analyze';
      setLoading('analyzeBtn', null, true);
      btn.querySelector('.btn-text').textContent = 'Analyzing…';

      try {
        const payload = {
          location: document.getElementById('location').value.trim(),
          time_of_day: document.getElementById('timeOfDay').value || null,
          include_weather: document.getElementById('includeWeather').checked,
          query: document.getElementById('aiQuery').value.trim() || null,
        };
        const data = await apiFetch('/analyze', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        renderResults(data, `Analysis: ${payload.location}`);
        toast('Analysis complete!', 'success');
      } catch (err) {
        toast(`Error: ${err.message}`, 'error');
      } finally {
        setLoading('analyzeBtn', null, false);
        btn.querySelector('.btn-text').textContent = 'Analyze';
      }
    });
  }

  // Route Optimization form
  const routeForm = document.getElementById('routeForm');
  if (routeForm) {
    routeForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('routeBtn');
      btn.querySelector('.btn-text').textContent = 'Optimizing…';
      btn.disabled = true;

      try {
        const payload = {
          origin: document.getElementById('origin').value.trim(),
          destination: document.getElementById('destination').value.trim(),
          avoid_congestion: document.getElementById('avoidCongestion').checked,
          time_of_day: document.getElementById('routeTime').value || null,
        };
        const data = await apiFetch('/optimize-route', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        renderResults(data, `Route: ${payload.origin} → ${payload.destination}`);
        toast('Route optimized!', 'success');
      } catch (err) {
        toast(`Error: ${err.message}`, 'error');
      } finally {
        btn.querySelector('.btn-text').textContent = 'Optimize Route';
        btn.disabled = false;
      }
    });
  }

  // Initial calls
  checkApiStatus();
  loadAlerts();
  setInterval(checkApiStatus, 15000);
});

// ---------------------------------------------------------------------------
// Congestion checker
// ---------------------------------------------------------------------------

async function checkCongestion() {
  const loc = document.getElementById('congestionLocation')?.value.trim();
  if (!loc) { toast('Please enter a location.', 'error'); return; }
  const btn = document.getElementById('congestionBtn');
  const resultEl = document.getElementById('congestionResult');
  btn.disabled = true;
  btn.textContent = '…';
  resultEl?.classList.add('hidden');

  try {
    const data = await apiFetch(`/congestion/${encodeURIComponent(loc)}`);
    if (resultEl) {
      resultEl.innerHTML = `<strong>${escHtml(loc)}</strong>: ${
        escHtml(data.congestion_level?.toUpperCase() ?? 'N/A')
      }<br/><span style="color:var(--muted);font-size:.85rem">${
        escHtml(data.analysis?.slice(0, 220) ?? '')
      }…</span>`;
      resultEl.classList.remove('hidden');
    }
  } catch (err) {
    toast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Check';
  }
}

// ---------------------------------------------------------------------------
// Alerts
// ---------------------------------------------------------------------------

async function loadAlerts() {
  const el = document.getElementById('alertsList');
  if (!el) return;
  el.innerHTML = '<p class="muted skeleton" style="height:1.2rem;width:60%">&nbsp;</p>';

  try {
    const data = await apiFetch('/alerts');
    const alerts = data.alerts || [];
    if (!alerts.length) {
      el.innerHTML = '<p class="muted">✅ No active alerts.</p>';
      return;
    }
    el.innerHTML = alerts.map(a => `
      <div class="alert-item">
        <span class="alert-severity severity-${a.severity ?? 'medium'}">${a.severity ?? 'medium'}</span>
        <div>
          <strong>${a.location}</strong><br/>
          <span class="muted">${a.description ?? a.alert_type}</span>
        </div>
      </div>`).join('');
  } catch {
    el.innerHTML = '<p class="muted">Could not load alerts.</p>';
  }
}

// Expose to HTML onclick
window.closeResults = closeResults;
window.loadAlerts = loadAlerts;
window.checkCongestion = checkCongestion;
