"""
Standalone feature engineering on an existing merged CSV.

Usage:
  python backend/preprocessing/feature_engineering.py --input datasets/processed/merged_training_data.csv
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from training.preprocessing import engineer_features, handle_missing_values
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df = engineer_features(df)
    df = handle_missing_values(df)
    out = args.output or args.input
    df.to_csv(out, index=False)
    print(f'Engineered features saved → {out} ({len(df)} rows)')


if __name__ == '__main__':
    main()
