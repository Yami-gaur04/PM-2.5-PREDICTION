/**
 * AirWatch India API client (Axios)
 */
const API_BASE =
  window.location.protocol.startsWith('http')
    ? window.location.origin
    : 'http://localhost:5000';

const client = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

async function get(path, params = {}) {
  const { data } = await client.get(path, { params });
  return data;
}

export const fetchHealth = () => get('/health');

export const postPredict = (payload) =>
  client.post('/predict', payload).then((r) => r.data);

export const fetchCityPredictions = (season = null) => {
  const params = {};
  if (season != null) params.season = season;
  return get('/city-predictions', params);
};

export const fetchLocations = fetchCityPredictions;

export const fetchCoverageSummary = () => get('/coverage-summary');

export const fetchTrend = (labelOrCity = 'Delhi', days = 30, lat = null, lon = null) => {
  const params = { days };
  if (lat != null && lon != null) {
    params.lat = lat;
    params.lon = lon;
    if (labelOrCity) params.label = labelOrCity;
  } else {
    params.label = labelOrCity;
  }
  return get('/trend', params);
};

export const fetchModelMetrics = () => get('/model-metrics');
export const fetchStateRankings = () => get('/state-rankings');
export const fetchCpcbFeed = () => get('/cpcb-feed');

export const fetchPredictAt = (lat, lon, season = null) => {
  const params = { lat, lon };
  if (season != null) params.season = season;
  return get('/predict-at', params);
};

export const fetchGridPredictions = (step = 2, season = null) => {
  const params = { step };
  if (season != null) params.season = season;
  return get('/grid-predictions', params);
};

export { API_BASE };
