"""
Load satellite AOD CSV (point or gridded extracts).

Expected: datetime, latitude, longitude, aod

Usage:
  python backend/preprocessing/load_aod.py --input datasets/raw/aod.csv
"""
import argparse
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from config import PROCESSED_DIR


def load_aod_csv(path):
    df = pd.read_csv(path)
    rename = {
        'lat': 'latitude', 'lon': 'longitude',
        'aod_value': 'aod', 'aod_550nm': 'aod', 'AOD': 'aod',
        'timestamp': 'datetime', 'date': 'datetime',
    }
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.dropna(subset=['datetime', 'latitude', 'longitude', 'aod'])
    df['source'] = 'aod'
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default=os.path.join(PROCESSED_DIR, 'aod_clean.csv'))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df = load_aod_csv(args.input)
    df.to_csv(args.output, index=False)
    print(f'Saved {len(df)} rows → {args.output}')


if __name__ == '__main__':
    main()
