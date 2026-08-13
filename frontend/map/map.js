/**
 * Leaflet map — pan-India coordinate PM2.5
 */
import { fetchPredictAt, fetchGridPredictions } from '../utils/api.js';

let mapInstance = null;
const cityMarkers = [];
let heatLayer = null;
let clickMarker = null;
let gridLoaded = false;

const DARK_TILES = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
const INDIA_BOUNDS = L.latLngBounds([6.5, 68], [37.5, 97]);

function pmToRadius(pm) {
  return Math.max(10, Math.min(40, 8 + Math.log(pm + 1) * 8));
}

function popupHtml(title, pm25, aqi, color, extra) {
  const D = 'd' + 'iv';
  const parts = [
    '<' + D + ' class="map-popup">',
    '<h4>', title, '</h4>',
    '<p><strong>PM2.5:</strong> <span style="color:', color, '">', pm25, ' µg/m³</span></p>',
    '<p><strong>AQI:</strong> <span style="color:', color, '">', aqi, '</span></p>',
  ];
  if (extra) parts.push('<p>', extra, '</p>');
  parts.push('</' + D + '>');
  return parts.join('');
}

function ensureMap(containerId) {
  const el = document.getElementById(containerId);
  if (!el) return null;
  if (!mapInstance) {
    mapInstance = L.map(containerId, {
      center: [22.5, 79], zoom: 5, minZoom: 4, maxZoom: 12,
      maxBounds: INDIA_BOUNDS.pad(0.05), maxBoundsViscosity: 0.85,
    });
    L.tileLayer(DARK_TILES, { attribution: '&copy; OSM, CARTO', subdomains: 'abcd' }).addTo(mapInstance);
    mapInstance.on('click', onMapClick);
  }
  return mapInstance;
}

function clearCityMarkers() {
  cityMarkers.forEach((m) => mapInstance?.removeLayer(m));
  cityMarkers.length = 0;
}

export function renderCityMarkers(locations) {
  if (!mapInstance) return;
  clearCityMarkers();
  locations.forEach((loc) => {
    const r = pmToRadius(loc.pm25);
    const icon = L.divIcon({
      className: 'city-bubble',
      html: '<' + ('d' + 'iv') + ' style="width:' + r + 'px;height:' + r + 'px;background:' + loc.color +
        'aa;border:2px solid ' + loc.color + ';border-radius:50%"></' + ('d' + 'iv') + '>',
      iconSize: [r, r], iconAnchor: [r / 2, r / 2],
    });
    const marker = L.marker([loc.lat, loc.lon], { icon })
      .bindPopup(popupHtml(loc.name || loc.city, loc.pm25, loc.aqi_category, loc.color, loc.station))
      .addTo(mapInstance);
    cityMarkers.push(marker);
  });
}

export function setCitiesVisible(show) {
  cityMarkers.forEach((m) => {
    if (show && !mapInstance.hasLayer(m)) m.addTo(mapInstance);
    else if (!show && mapInstance.hasLayer(m)) mapInstance.removeLayer(m);
  });
}

export async function loadCoverageGrid(step = 2, season = null) {
  if (!mapInstance || typeof L.heatLayer !== 'function') return null;
  const status = document.getElementById('map-loading');
  if (status) { status.textContent = 'Loading grid…'; status.classList.remove('hidden'); }
  try {
    const data = await fetchGridPredictions(step, season);
    const heatPoints = data.points.map((p) => [p.lat, p.lon, Math.min(1, p.pm25 / 280)]);
    if (heatLayer) mapInstance.removeLayer(heatLayer);
    heatLayer = L.heatLayer(heatPoints, { radius: 22, blur: 18, maxZoom: 11, minOpacity: 0.35 }).addTo(mapInstance);
    gridLoaded = true;
    if (status) status.textContent = data.count + ' grid points';
    return data;
  } catch (err) {
    console.error(err);
    if (status) status.textContent = 'Grid failed';
    return null;
  }
}

export function setGridVisible(show) {
  if (!heatLayer) return;
  if (show && !mapInstance.hasLayer(heatLayer)) heatLayer.addTo(mapInstance);
  else if (!show && mapInstance.hasLayer(heatLayer)) mapInstance.removeLayer(heatLayer);
}

async function onMapClick(e) {
  const { lat, lng: lon } = e.latlng;
  const status = document.getElementById('map-click-status');
  if (status) status.textContent = 'Predicting…';
  try {
    const seasonEl = document.getElementById('map-season');
    const season = seasonEl ? parseInt(seasonEl.value, 10) : null;
    const data = await fetchPredictAt(lat, lon, season);
    if (clickMarker) mapInstance.removeLayer(clickMarker);
    clickMarker = L.circleMarker([lat, lon], {
      radius: 10, color: '#00d4ff', fillColor: data.aqi_color, fillOpacity: 0.85, weight: 3,
    }).bindPopup(popupHtml(
      lat.toFixed(2) + '°N, ' + lon.toFixed(2) + '°E',
      data.pm25, data.aqi_category, data.aqi_color, data.state + ' · ' + data.source,
    )).addTo(mapInstance).openPopup();
    if (status) status.textContent = data.pm25 + ' µg/m³ (' + data.aqi_category + ')';
    window.dispatchEvent(new CustomEvent('map-predict', { detail: data }));
  } catch (err) {
    if (status) status.textContent = err.message || 'Outside India';
  }
}

export async function initIndiaMap(containerId, cities, options = {}) {
  const map = ensureMap(containerId);
  if (!map) return;
  const { showGrid = true, showCities = true } = options;
  renderCityMarkers(cities);
  setCitiesVisible(showCities);
  const seasonEl = document.getElementById('map-season');
  const season = seasonEl ? parseInt(seasonEl.value, 10) : null;
  if (showGrid && !gridLoaded) await loadCoverageGrid(2, season);
  else if (showGrid && heatLayer) setGridVisible(true);
  if (cities.length) map.fitBounds(L.latLngBounds(cities.map((c) => [c.lat, c.lon])).pad(0.12));
  setTimeout(() => map.invalidateSize(), 200);
}

export function bindMapControls() {
  document.getElementById('map-toggle-grid')?.addEventListener('change', async (e) => {
    if (e.target.checked) {
      if (!gridLoaded) await loadCoverageGrid(2);
      else setGridVisible(true);
    } else setGridVisible(false);
  });
  document.getElementById('map-toggle-cities')?.addEventListener('change', (e) => setCitiesVisible(e.target.checked));
  document.getElementById('map-season')?.addEventListener('change', async () => {
    gridLoaded = false;
    if (document.getElementById('map-toggle-grid')?.checked) {
      await loadCoverageGrid(2, parseInt(document.getElementById('map-season').value, 10));
    }
  });
}
