"""
Merge CPCB, weather, and AOD datasets on latitude, longitude, and datetime.

Nearest-neighbor spatial join within max_km, then hourly time alignment.

Usage (from AirWatchIndia/):
  python backend/preprocessing/merge_datasets.py

Place cleaned CSVs in datasets/processed/ or pass paths via CLI.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from config import PROCESSED_DIR, MERGED_CSV
from training.preprocessing import engineer_features, handle_missing_values


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlon / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def nearest_merge(left, right, max_km=25.0):
    """Merge right onto left by nearest lat/lon per datetime hour."""
    left = left.copy()
    right = right.copy()
    left['hour'] = pd.to_datetime(left['datetime']).dt.floor('h')
    right['hour'] = pd.to_datetime(right['datetime']).dt.floor('h')

    merged_rows = []
    for hour, l_grp in left.groupby('hour'):
        r_grp = right[right['hour'] == hour]
        if r_grp.empty:
            merged_rows.append(l_grp)
            continue
        for _, lrow in l_grp.iterrows():
            dists = _haversine_km(
                lrow['latitude'], lrow['longitude'],
                r_grp['latitude'].values, r_grp['longitude'].values,
            )
            idx = int(np.argmin(dists))
            if dists[idx] <= max_km:
                rrow = r_grp.iloc[idx]
                combined = {**lrow.to_dict(), **{k: rrow[k] for k in r_grp.columns if k not in lrow.index}}
                merged_rows.append(pd.Series(combined))
            else:
                merged_rows.append(lrow)

    if not merged_rows:
        return left
    return pd.DataFrame(merged_rows)


def merge_all(cpcb_path, weather_path, aod_path, output_path, max_km=25.0):
    cpcb = pd.read_csv(cpcb_path)
    weather = pd.read_csv(weather_path) if os.path.isfile(weather_path) else None
    aod = pd.read_csv(aod_path) if os.path.isfile(aod_path) else None

    cpcb['datetime'] = pd.to_datetime(cpcb['datetime'])
    df = cpcb.copy()

    if weather is not None:
        weather['datetime'] = pd.to_datetime(weather['datetime'])
        df = nearest_merge(df, weather, max_km=max_km)

    if aod is not None:
        aod['datetime'] = pd.to_datetime(aod['datetime'])
        df = nearest_merge(df, aod, max_km=max_km)

    df = engineer_features(df)
    df = handle_missing_values(df)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


def generate_sample_merged(output_path, n_rows=2000):
    """Create synthetic merged data for pipeline smoke tests (no real CPCB needed)."""
    rng = np.random.RandomState(42)
    lats = rng.uniform(8, 32, n_rows)
    lons = rng.uniform(72, 92, n_rows)
    months = rng.randint(1, 13, n_rows)
    stations = [f'S{i % 80}' for i in range(n_rows)]

    df = pd.DataFrame({
        'datetime': pd.date_range('2023-01-01', periods=n_rows, freq='3h'),
        'latitude': lats,
        'longitude': lons,
        'station_id': stations,
        'aod': np.clip(rng.normal(0.45, 0.15, n_rows), 0.1, 1.2),
        'temperature': rng.uniform(15, 38, n_rows),
        'humidity': rng.uniform(30, 90, n_rows),
        'wind_speed': rng.uniform(0.5, 8, n_rows),
        'pressure': rng.uniform(990, 1020, n_rows),
        'rainfall': rng.exponential(0.5, n_rows),
        'month': months,
        'elevation': rng.uniform(0, 2000, n_rows),
        'population_density': rng.uniform(100, 15000, n_rows),
    })
    df['season'] = df['month'].apply(lambda m: 0 if m in (12, 1, 2) else 1 if m in (3, 4, 5) else 2 if m in (6, 7, 8, 9) else 3)
    df['pm25'] = (
        df['aod'] * 160 + df['temperature'] * 0.8 + df['humidity'] * 0.2
        - df['wind_speed'] * 3 + rng.normal(0, 8, n_rows)
    )
    df['pm25'] = df['pm25'].clip(5, 400)
    df = engineer_features(df)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f'Generated sample merged data ({n_rows} rows) → {output_path}')
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cpcb', default=os.path.join(PROCESSED_DIR, 'cpcb_clean.csv'))
    parser.add_argument('--weather', default=os.path.join(PROCESSED_DIR, 'weather_clean.csv'))
    parser.add_argument('--aod', default=os.path.join(PROCESSED_DIR, 'aod_clean.csv'))
    parser.add_argument('--output', default=MERGED_CSV)
    parser.add_argument('--sample', action='store_true', help='Generate synthetic merged CSV')
    parser.add_argument('--max-km', type=float, default=25.0)
    args = parser.parse_args()

    if args.sample or not os.path.isfile(args.cpcb):
        generate_sample_merged(args.output)
        return

    df = merge_all(args.cpcb, args.weather, args.aod, args.output, args.max_km)
    print(f'Merged {len(df)} rows → {args.output}')


if __name__ == '__main__':
    main()
