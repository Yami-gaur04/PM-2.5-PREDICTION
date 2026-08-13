"""Coordinate-based PM2.5 prediction service."""
from datetime import datetime

from utils import model_loader
from utils.spatial import is_in_india, latlon_to_state, estimate_aod, month_to_season, season_name
from utils.geo_features import build_features_from_request


def predict_at_coordinate(lat, lon, payload=None):
    payload = payload or {}
    if not is_in_india(lat, lon):
        raise ValueError('Coordinates outside India coverage bounds')

    data = {
        'latitude': lat,
        'longitude': lon,
        'datetime': payload.get('datetime'),
        'aod': payload.get('aod', estimate_aod(lat, lon)),
        'temperature': payload.get('temperature', payload.get('temp_avg', 28)),
        'humidity': payload.get('humidity', 55),
        'wind_speed': payload.get('wind_speed', 2.5),
        'pressure': payload.get('pressure', 1010),
        'rainfall': payload.get('rainfall', 0),
        'season': payload.get('season'),
        'elevation': payload.get('elevation'),
        'population_density': payload.get('population_density'),
    }
    pm25, aqi, source, features = model_loader.predict_pm25(data)
    season = int(features.get('season', month_to_season()))

    return {
        'latitude': lat,
        'longitude': lon,
        'pm25': pm25,
        'aqi_category': aqi['label'],
        'aqi_color': aqi['color'],
        'severity': aqi['severity'],
        'state': latlon_to_state(lat, lon),
        'season': season,
        'season_name': season_name(season),
        'features_used': {k: features[k] for k in (
            'aod', 'temperature', 'humidity', 'wind_speed', 'pressure', 'rainfall', 'month'
        )},
        'source': source,
        'unit': 'µg/m³',
        'timestamp': datetime.now().isoformat(),
    }


def predict_from_body(body):
    lat = float(body.get('latitude', body.get('lat')))
    lon = float(body.get('longitude', body.get('lon')))
    return predict_at_coordinate(lat, lon, body)
