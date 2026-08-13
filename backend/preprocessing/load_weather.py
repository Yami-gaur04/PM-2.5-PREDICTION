"""
Load weather station / reanalysis CSV.

Expected: datetime, latitude, longitude, temperature, humidity, wind_speed, pressure, rainfall

Usage:
  python backend/preprocessing/load_weather.py --input datasets/raw/weather.csv
"""
import argparse
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from config import PROCESSED_DIR


def load_weather_csv(path):
    df = pd.read_csv(path)
    rename = {
        'lat': 'latitude', 'lon': 'longitude',
        'temp': 'temperature', 'temp_avg': 'temperature',
        'rh': 'humidity', 'wind': 'wind_speed',
        'precipitation': 'rainfall', 'precip': 'rainfall',
        'timestamp': 'datetime',
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime', 'latitude', 'longitude'])
    df['source'] = 'weather'
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default=os.path.join(PROCESSED_DIR, 'weather_clean.csv'))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df = load_weather_csv(args.input)
    df.to_csv(args.output, index=False)
    print(f'Saved {len(df)} rows → {args.output}')


if __name__ == '__main__':
    main()
