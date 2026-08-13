/**
 * Chart.js modules for AirWatch India
 */
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(0, 212, 255, 0.15)';
Chart.defaults.font.family = "'Rajdhani', sans-serif";

let trendChart = null;
let featureChart = null;
let scatterChart = null;

function resetCanvas(canvas) {
  if (!canvas) return;
  canvas.style.removeProperty('width');
  canvas.style.removeProperty('height');
}

function destroy(chart, canvas) {
  if (chart) chart.destroy();
  resetCanvas(canvas);
}

export function renderTrendChart(canvasId, data, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const labels = (data.dates || []).map((d) => {
    const dt = new Date(d);
    return dt.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
  });
  const values = data.pm25 || [];
  destroy(trendChart, ctx);
  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'PM2.5 — ' + label,
        data: values,
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0,212,255,0.15)',
        fill: true,
        tension: 0.35,
        pointRadius: 2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
      },
    },
  });
}

export function computeTrendInsights(data) {
  if (data.avg != null) {
    return [
      { val: data.avg, lbl: 'Average' },
      { val: data.max, lbl: 'Peak' },
      { val: data.min, lbl: 'Low' },
    ];
  }
  const vals = (data.pm25 || []);
  if (!vals.length) return [];
  const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
  return [
    { val: vals[vals.length - 1].toFixed(1), lbl: 'Latest' },
    { val: avg.toFixed(1), lbl: 'Average' },
    { val: Math.max(...vals).toFixed(1), lbl: 'Peak' },
  ];
}

export function renderFeatureChart(canvasId, importances) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !importances) return;
  const entries = Object.entries(importances).sort((a, b) => b[1] - a[1]).slice(0, 12);
  destroy(featureChart, ctx);
  featureChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: entries.map(([k]) => k),
      datasets: [{
        data: entries.map(([, v]) => (v <= 1 ? v * 100 : v)),
        backgroundColor: 'rgba(168,85,247,0.75)',
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
    },
  });
}

export function renderScatterChart(canvasId, scatter) {
  const ctx = document.getElementById(canvasId);
  if (!ctx || !scatter) return;
  const points = scatter.observed.map((o, i) => ({ x: o, y: scatter.predicted[i] }));
  destroy(scatterChart, ctx);
  scatterChart = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        { data: points, backgroundColor: 'rgba(0,212,255,0.5)' },
        {
          data: [{ x: 0, y: 0 }, { x: 300, y: 300 }],
          showLine: true,
          pointRadius: 0,
          borderColor: '#a855f7',
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}
