"""
Training-time preprocessing — aligns with inference feature schema.
Run after merge_datasets.py produces merged_training_data.csv
"""
import math
import os

import numpy as np
import pandas as pd

# Canonical feature columns (target: pm25)
FEATURE_COLUMNS = [
    'latitude', 'longitude', 'aod', 'temperature', 'humidity',
    'wind_speed', 'pressure', 'rainfall', 'month', 'season',
    'elevation', 'population_density',
    'lat_sin', 'lat_cos', 'lon_sin', 'lon_cos',
    'aod_temp_interaction', 'aod_humidity_interaction',
]

TARGET_COLUMN = 'pm25'
STATION_COLUMN = 'station_id'


def month_to_season(month):
    m = int(month)
    if m in (12, 1, 2):
        return 0
    if m in (3, 4, 5):
        return 1
    if m in (6, 7, 8, 9):
        return 2
    return 3


def _cyclical_lat_lon(lat, lon):
    lat_r = np.radians(lat)
    lon_r = np.radians(lon)
    return (
        np.sin(lat_r), np.cos(lat_r),
        np.sin(lon_r), np.cos(lon_r),
    )


def normalize_column_names(df):
    """Map common CSV column aliases to canonical names."""
    mapping = {
        'lat': 'latitude', 'lon': 'longitude', 'lng': 'longitude',
        'temp': 'temperature', 'temp_avg': 'temperature',
        'rh': 'humidity', 'relative_humidity': 'humidity',
        'wind': 'wind_speed', 'windspeed': 'wind_speed',
        'precipitation': 'rainfall', 'precip': 'rainfall', 'prcp': 'rainfall',
        'aod_value': 'aod', 'aod_550nm': 'aod',
        'pm2_5': 'pm25', 'pm2.5': 'pm25', 'PM2.5': 'pm25',
        'station': 'station_id', 'station_name': 'station_id',
        'pop_density': 'population_density',
    }
    df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
    return df


def engineer_features(df):
    df = normalize_column_names(df.copy())

    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df['month'] = df['datetime'].dt.month
    elif 'month' not in df.columns:
        df['month'] = 6

    if 'season' not in df.columns:
        df['season'] = df['month'].apply(month_to_season)

    for col in ['latitude', 'longitude', 'aod', 'temperature', 'humidity',
                'wind_speed', 'pressure', 'rainfall', 'elevation', 'population_density']:
        if col not in df.columns:
            df[col] = np.nan

    lat_sin, lat_cos, lon_sin, lon_cos = _cyclical_lat_lon(
        df['latitude'].astype(float), df['longitude'].astype(float),
    )
    df['lat_sin'] = lat_sin
    df['lat_cos'] = lat_cos
    df['lon_sin'] = lon_sin
    df['lon_cos'] = lon_cos
    df['aod_temp_interaction'] = df['aod'] * df['temperature']
    df['aod_humidity_interaction'] = df['aod'] * df['humidity']

    if STATION_COLUMN not in df.columns:
        df[STATION_COLUMN] = (
            df['latitude'].round(2).astype(str) + '_' + df['longitude'].round(2).astype(str)
        )

    return df


def handle_missing_values(df, feature_cols=None):
    feature_cols = feature_cols or FEATURE_COLUMNS
    df = df.copy()
    for col in feature_cols + [TARGET_COLUMN]:
        if col not in df.columns:
            continue
        if df[col].dtype.kind in 'fc':
            med = df[col].median()
            df[col] = df[col].fillna(med if not np.isnan(med) else 0)
    return df


def load_and_prepare(csv_path):
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(
            f'Merged dataset not found: {csv_path}\n'
            'Run: python preprocessing/merge_datasets.py'
        )
    df = pd.read_csv(csv_path)
    df = engineer_features(df)
    df = handle_missing_values(df)
    df = df.dropna(subset=[TARGET_COLUMN])
    return df


def get_xy(df):
    cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    X = df[cols].astype(float)
    y = df[TARGET_COLUMN].astype(float)
    return X, y, cols
