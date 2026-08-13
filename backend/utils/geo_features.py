"""Coordinate-based feature engineering for inference and training alignment."""
import math
from datetime import datetime

import numpy as np

from utils.spatial import (
    estimate_aod,
    estimate_elevation,
    estimate_population_density,
    month_to_season,
)

# Must match training/training/preprocessing.py FEATURE_COLUMNS order after engineering
BASE_FEATURE_COLUMNS = [
    'latitude', 'longitude', 'aod', 'temperature', 'humidity',
    'wind_speed', 'pressure', 'rainfall', 'month', 'season',
    'elevation', 'population_density',
    'lat_sin', 'lat_cos', 'lon_sin', 'lon_cos',
    'aod_temp_interaction', 'aod_humidity_interaction',
]


def parse_datetime(value):
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(str(value)[:19], fmt)
        except ValueError:
            continue
    return datetime.now()


def cyclical_lat_lon(lat, lon):
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)
    return (
        math.sin(lat_r), math.cos(lat_r),
        math.sin(lon_r), math.cos(lon_r),
    )


def build_features_from_request(data: dict) -> dict:
    """
    Build a full feature dict from API / user input.
    Accepts lat/lon aliases and weather field aliases.
    """
    lat = float(data.get('latitude', data.get('lat', 20.0)))
    lon = float(data.get('longitude', data.get('lon', 77.0)))
    dt = parse_datetime(data.get('datetime', data.get('timestamp')))

    month = int(data.get('month', dt.month))
    season = int(data.get('season', month_to_season(month)))

    temp = float(data.get('temperature', data.get('temp_avg', 28.0)))
    humidity = float(data.get('humidity', data.get('rh', 55.0)))
    wind = float(data.get('wind_speed', data.get('wind', 2.5)))
    pressure = float(data.get('pressure', 1010.0))
    rainfall = float(data.get('rainfall', data.get('precipitation', 0.0)))
    aod = float(data.get('aod', data.get('aod_value', estimate_aod(lat, lon))))

    elevation = float(data.get('elevation', estimate_elevation(lat, lon)))
    pop_density = float(data.get(
        'population_density',
        data.get('pop_density', estimate_population_density(lat, lon)),
    ))

    lat_sin, lat_cos, lon_sin, lon_cos = cyclical_lat_lon(lat, lon)

    return {
        'latitude': lat,
        'longitude': lon,
        'aod': aod,
        'temperature': temp,
        'humidity': humidity,
        'wind_speed': wind,
        'pressure': pressure,
        'rainfall': rainfall,
        'month': month,
        'season': season,
        'elevation': elevation,
        'population_density': pop_density,
        'lat_sin': lat_sin,
        'lat_cos': lat_cos,
        'lon_sin': lon_sin,
        'lon_cos': lon_cos,
        'aod_temp_interaction': aod * temp,
        'aod_humidity_interaction': aod * humidity,
    }


def features_to_vector(feature_dict: dict, column_order: list) -> np.ndarray:
    return np.array([[float(feature_dict.get(c, 0.0)) for c in column_order]])


def demo_pm25_formula(features: dict) -> float:
    """Fallback when no trained model is present."""
    lat, lon = features['latitude'], features['longitude']
    aod = features['aod']
    temp = features['temperature']
    hum = features['humidity']
    wind = max(features['wind_speed'], 0.3)
    rain = features['rainfall']
    season = features['season']
    pop = features['population_density']

    base = aod * 180 + (temp - 20) * 1.2 + hum * 0.15
    base += pop / 8000
    base -= wind * 4
    base -= rain * 0.8
    base += (12 if season == 0 else 0) + (6 if season == 1 else 0)
    # Indo-Gangetic bump
    if 24 <= lat <= 30 and 75 <= lon <= 88:
        base += 25
    return float(max(5.0, min(500.0, base)))
