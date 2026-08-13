"""
Load CPCB / OpenAQ air quality CSV into a normalized dataframe.

Expected columns (flexible aliases supported):
  datetime, latitude, longitude, pm25, station_id

Usage:
  python backend/preprocessing/load_cpcb.py --input datasets/raw/cpcb.csv
"""
import argparse
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from config import RAW_DIR, PROCESSED_DIR


def load_cpcb_csv(path):
    df = pd.read_csv(path)
    rename = {
        'lat': 'latitude', 'lon': 'longitude', 'lng': 'longitude',
        'pm2_5': 'pm25', 'pm2.5': 'pm25', 'PM2.5': 'pm25',
        'station': 'station_id', 'station_name': 'station_id',
        'timestamp': 'datetime', 'date': 'datetime',
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    required = {'datetime', 'latitude', 'longitude', 'pm25'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns in CPCB file: {missing}')
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime', 'latitude', 'longitude', 'pm25'])
    df['source'] = 'cpcb'
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to CPCB/OpenAQ CSV')
    parser.add_argument('--output', default=os.path.join(PROCESSED_DIR, 'cpcb_clean.csv'))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df = load_cpcb_csv(args.input)
    df.to_csv(args.output, index=False)
    print(f'Saved {len(df)} rows → {args.output}')


if __name__ == '__main__':
    main()
