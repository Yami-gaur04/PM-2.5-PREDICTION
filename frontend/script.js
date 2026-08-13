/**
 * AirWatch India — coordinate-based dashboard
 */
import {
  fetchHealth, postPredict, fetchCityPredictions, fetchLocations,
  fetchCoverageSummary, fetchTrend, fetchModelMetrics,
  fetchStateRankings, fetchCpcbFeed,
} from './utils/api.js';
import { renderTrendChart, computeTrendInsights, renderFeatureChart, renderScatterChart } from './charts/charts.js';
import { initIndiaMap, bindMapControls } from './map/map.js';

const $ = (sel) => document.querySelector(sel);
let predictTimer = null;
let cpcbInterval = null;

const PREDICT_FIELDS = [
  'aod_value', 'temp_avg', 'temp_max', 'temp_min',
  'no2', 'so2', 'co', 'o3', 'pm10', 'precipitation',
];

function initParticles() {
  const canvas = $('#particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let w, h, particles;
  const resize = () => {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
    particles = Array.from({ length: 50 }, () => ({
      x: Math.random() * w, y: Math.random() * h,
      r: Math.random() * 2 + 0.5, vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
    }));
  };
  const draw = () => {
    ctx.clearRect(0, 0, w, h);
    particles.forEach((p) => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0,212,255,0.4)';
      ctx.fill();
    });
    requestAnimationFrame(draw);
  };
  resize();
  window.addEventListener('resize', resize);
  draw();
}

function initReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
  }, { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach((el) => obs.observe(el));
}

async function checkHealth() {
  const statusEl = $('#api-status');
  const textEl = statusEl?.querySelector('.status-text');
  try {
    const h = await fetchHealth();
    statusEl?.classList.add('online');
    if (textEl) textEl.textContent = h.model_loaded ? 'XGBoost Online' : 'Demo Mode';
    return true;
  } catch {
    statusEl?.classList.add('offline');
    if (textEl) textEl.textContent = 'API Offline';
    return false;
  }
}

async function loadHeroStats() {
  const container = $('#hero-stats');
  if (!container) return;
  try {
    const [coverage, metrics] = await Promise.all([fetchCoverageSummary(), fetchModelMetrics()]);
    container.innerHTML = `
      <div class="stat-card"><span class="stat-value">${coverage.named_locations}</span><span class="stat-label">Stations</span></div>
      <div class="stat-card"><span class="stat-value">${coverage.states_covered}</span><span class="stat-label">States</span></div>
      <div class="stat-card"><span class="stat-value">${metrics.r2 ? (metrics.r2 * 100).toFixed(1) + '%' : '—'}</span><span class="stat-label">Model R²</span></div>
      <div class="stat-card"><span class="stat-value">Pan-India</span><span class="stat-label">Coverage</span></div></div></div></div></div>`;
  } catch { /* keep placeholders */ }
}

function getPredictPayload() {
  const tmax = parseFloat($('#temp_max')?.value ?? 34);
  const tmin = parseFloat($('#temp_min')?.value ?? 22);
  const humidity = Math.max(20, Math.min(95, 100 - (tmax - tmin) * 2.5));
  return {
    latitude: parseFloat($('#latitude')?.value ?? 28.61),
    longitude: parseFloat($('#longitude')?.value ?? 77.21),
    aod: parseFloat($('#aod_value')?.value ?? 0.48),
    temperature: parseFloat($('#temp_avg')?.value ?? 28),
    humidity,
    wind_speed: 2.5,
    pressure: 1010,
    rainfall: parseFloat($('#precipitation')?.value ?? 0),
    season: parseInt($('#season')?.value ?? 2, 10),
  };
}

function displayPrediction(data) {
  if (!data || data.error) return;
  const pmEl = $('#result-pm25');
  const aqiEl = $('#result-aqi');
  if (pmEl) {
    pmEl.innerHTML = `${data.pm25} <small>${data.unit || 'µg/m³'}</small>`;
    pmEl.style.color = data.aqi_color;
  }
  if (aqiEl) {
    aqiEl.textContent = data.aqi_category;
    aqiEl.style.color = data.aqi_color;
  }
  if ($('#result-source')) $('#result-source').textContent = data.source;
  if ($('#result-timestamp') && data.timestamp) {
    $('#result-timestamp').textContent = new Date(data.timestamp).toLocaleString('en-IN');
  }
}

async function runPredict() {
  $('#predict-loading')?.classList.add('active');
  try {
    displayPrediction(await postPredict(getPredictPayload()));
  } catch (e) {
    console.error(e);
    if ($('#result-source')) $('#result-source').textContent = 'Start Flask: python backend/app.py';
  } finally {
    $('#predict-loading')?.classList.remove('active');
  }
}

function schedulePredict() {
  clearTimeout(predictTimer);
  predictTimer = setTimeout(runPredict, 300);
}

function initPredictForm() {
  if (!$('#latitude')) {
    const form = $('#predict-form');
    if (form) {
      const latGroup = document.createElement('d' + 'iv');
      latGroup.className = 'input-group';
      latGroup.innerHTML = '<label>Latitude</label><input type="number" id="latitude" value="28.61" step="0.01" min="6.5" max="37.5" />';
      form.prepend(latGroup);
      const lonGroup = document.createElement('d' + 'iv');
      lonGroup.className = 'input-group';
      lonGroup.innerHTML = '<label>Longitude</label><input type="number" id="longitude" value="77.21" step="0.01" min="68" max="97.5" />';
      form.prepend(lonGroup);
    }
  }
  PREDICT_FIELDS.forEach((field) => {
    $(`#${field}`)?.addEventListener('input', (e) => {
      const v = e.target.value;
      const span = $(`#val-${field}`);
      if (span) span.textContent = v;
      schedulePredict();
    });
  });
  $('#latitude')?.addEventListener('change', schedulePredict);
  $('#longitude')?.addEventListener('change', schedulePredict);
  $('#season')?.addEventListener('change', schedulePredict);
  runPredict();
}

window.addEventListener('map-predict', (e) => {
  const d = e.detail;
  if ($('#latitude')) $('#latitude').value = d.latitude;
  if ($('#longitude')) $('#longitude').value = d.longitude;
  displayPrediction(d);
});

async function loadMap() {
  try {
    const cities = await fetchCityPredictions();
    bindMapControls();
    await initIndiaMap('india-map', cities, { showGrid: true, showCities: true });
    $('#map-loading')?.classList.add('hidden');
  } catch (e) {
    console.error(e);
  }
}

async function loadTrendLocations() {
  const select = $('#trend-city');
  if (!select) return;
  try {
    const locs = await fetchLocations();
    select.innerHTML = locs.map((l) =>
      `<option value="${l.name}" data-lat="${l.lat}" data-lon="${l.lon}">${l.name} (${l.state})</option>`,
    ).join('');
    loadTrend();
  } catch {
    select.innerHTML = '<option value="Delhi">Delhi</option>';
  }
}

async function loadTrend() {
  const opt = $('#trend-city')?.selectedOptions?.[0];
  const label = opt?.value || 'Delhi';
  const lat = opt?.dataset?.lat ? parseFloat(opt.dataset.lat) : null;
  const lon = opt?.dataset?.lon ? parseFloat(opt.dataset.lon) : null;
  const days = parseInt($('#trend-days')?.value || '30', 10);
  try {
    const data = await fetchTrend(label, days, lat, lon);
    const series = (data.dates || []).map((d, i) => ({ date: d, pm25: data.pm25[i] }));
    renderTrendChart('trend-chart', data, label);
    const insights = computeTrendInsights(data);
    const el = $('#trend-insights');
    if (el) {
      el.innerHTML = insights.map((i) =>
        `<div class="insight-item"><span class="val">${i.val}</span><span class="lbl">${i.lbl}</span></div>`,
      ).join('');
    }
  } catch (e) { console.error(e); }
}

async function loadMetrics() {
  try {
    const m = await fetchModelMetrics();
    const cards = $('#metrics-cards');
    if (cards) {
      cards.innerHTML = [
        { val: m.r2, name: 'R²' }, { val: m.rmse, name: 'RMSE' },
        { val: m.mae, name: 'MAE' }, { val: m.model_type || 'xgboost', name: 'Model' },
      ].map((i) => `<div class="metric-card glass-card"><span class="metric-val">${i.val}</span><span class="metric-name">${i.name}</span></div>`).join('');
    }
    renderFeatureChart('feature-chart', m.feature_importances);
    renderScatterChart('scatter-chart', m.validation_scatter);
  } catch (e) { console.error(e); }
}

async function loadRankings() {
  const list = $('#rankings-list');
  if (!list) return;
  try {
    const states = await fetchStateRankings();
    const maxPm = states[0]?.avg_pm25 || 200;
    list.innerHTML = states.map((s, i) => {
      const pm = s.avg_pm25 ?? s.pm25;
      const pct = (pm / maxPm) * 100;
      const color = pm > 120 ? '#A855F7' : pm > 60 ? '#F59E0B' : '#10B981';
      return `<div class="rank-row"><span>#${i + 1}</span><span>${s.state}</span>
        <div class="rank-bar-wrap"><div class="rank-bar" style="width:${pct}%;background:${color}"></div></div></div>
        <span style="color:${color}">${pm}</span></div>`;
    }).join('');
  } catch (e) { console.error(e); }
}

async function loadCpcb() {
  const grid = $('#cpcb-grid');
  if (!grid) return;
  try {
    const data = await fetchCpcbFeed();
    grid.innerHTML = data.slice(0, 12).map((s) => `
      <article class="cpcb-card glass-card" style="--card-accent:${s.color}">
        <p class="cpcb-station">${s.station}</p>
        <p class="cpcb-city">${s.city} · ${s.state}</p>
        <p class="cpcb-pm" style="color:${s.color}">${s.pm25} µg/m³</p>
        <span>${s.aqi}</span>
      </article>`).join('');
  } catch (e) { console.error(e); }
}

async function init() {
  initParticles();
  initReveal();
  initPredictForm();
  $('#trend-city')?.addEventListener('change', loadTrend);
  $('#trend-days')?.addEventListener('change', loadTrend);
  await checkHealth();
  loadHeroStats();
  loadMap();
  loadTrendLocations();
  loadMetrics();
  loadRankings();
  loadCpcb();
  cpcbInterval = setInterval(loadCpcb, 30000);
}

document.addEventListener('DOMContentLoaded', init);
