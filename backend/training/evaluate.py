"""
Evaluate a saved PM2.5 model on held-out stations.

Usage:
  python backend/training/evaluate.py --data datasets/processed/merged_training_data.csv
"""
import argparse
import json
import os
import sys

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND = os.path.join(ROOT, 'backend')
sys.path.insert(0, BACKEND)

from config import MERGED_CSV, MODEL_DIR, MODEL_PATH, FEATURES_PATH, METRICS_PATH
from training.preprocessing import load_and_prepare, get_xy
from training.utils import regression_metrics, station_group_split


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default=MERGED_CSV)
    parser.add_argument('--test-size', type=float, default=0.2)
    args = parser.parse_args()

    model = joblib.load(MODEL_PATH)
    features = joblib.load(FEATURES_PATH)

    df = load_and_prepare(args.data)
    _, test_df = station_group_split(df, test_size=args.test_size)
    X_test, y_test, _ = get_xy(test_df)
    X_test = X_test[features]

    pred = model.predict(X_test)
    metrics = regression_metrics(y_test, pred)
    metrics['scatter'] = {
        'observed': np.round(y_test.values, 2).tolist()[:500],
        'predicted': np.round(pred, 2).tolist()[:500],
    }

    with open(METRICS_PATH, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    out_plot = os.path.join(MODEL_DIR, 'validation_scatter.png')
    plt.figure(figsize=(6, 6))
    plt.scatter(y_test, pred, alpha=0.4, s=12, c='#00d4ff')
    lim = max(y_test.max(), pred.max()) * 1.05
    plt.plot([0, lim], [0, lim], '--', color='#a855f7')
    plt.xlabel('Observed PM2.5')
    plt.ylabel('Predicted PM2.5')
    plt.title(f'Validation (R²={metrics["r2"]}, RMSE={metrics["rmse"]})')
    plt.tight_layout()
    plt.savefig(out_plot, dpi=120)
    plt.close()

    print('Evaluation metrics:', metrics)
    print(f'Scatter plot: {out_plot}')


if __name__ == '__main__':
    main()
