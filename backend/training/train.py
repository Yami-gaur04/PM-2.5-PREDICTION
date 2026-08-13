"""
Train PM2.5 models (Random Forest, XGBoost, LightGBM).
Default export: XGBoost → backend/models/xgboost_pm25_model.joblib

Usage (from AirWatchIndia/):
  python backend/training/train.py
  python backend/training/train.py --data datasets/processed/merged_training_data.csv
"""
import argparse
import os
import sys

import numpy as np

# Project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND = os.path.join(ROOT, 'backend')
sys.path.insert(0, BACKEND)

from config import MERGED_CSV, MODEL_DIR
from training.preprocessing import load_and_prepare, get_xy, FEATURE_COLUMNS
from training.utils import regression_metrics, save_artifacts, station_group_split, feature_importance_dict


def build_models():
    from sklearn.ensemble import RandomForestRegressor
    import xgboost as xgb

    models = {
        'random_forest': RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_leaf=5,
            n_jobs=-1, random_state=42,
        ),
        'xgboost': xgb.XGBRegressor(
            n_estimators=300, max_depth=8, learning_rate=0.08,
            subsample=0.85, colsample_bytree=0.85,
            objective='reg:squarederror', random_state=42, n_jobs=-1,
        ),
    }
    try:
        import lightgbm as lgb
        models['lightgbm'] = lgb.LGBMRegressor(
            n_estimators=300, max_depth=8, learning_rate=0.08,
            subsample=0.85, colsample_bytree=0.85, random_state=42, verbose=-1,
        )
    except ImportError:
        print('LightGBM not installed — skipping (pip install lightgbm)')
    return models


def main():
    parser = argparse.ArgumentParser(description='Train AirWatch India PM2.5 models')
    parser.add_argument('--data', default=MERGED_CSV, help='Merged training CSV path')
    parser.add_argument('--test-size', type=float, default=0.2, help='Station holdout fraction')
    parser.add_argument('--export', default='xgboost', choices=['random_forest', 'xgboost', 'lightgbm'])
    args = parser.parse_args()

    print(f'Loading data: {args.data}')
    df = load_and_prepare(args.data)
    train_df, test_df = station_group_split(df, test_size=args.test_size)

    X_train, y_train, cols = get_xy(train_df)
    X_test, y_test, _ = get_xy(test_df)

    print(f'Train rows: {len(X_train)} | Test rows: {len(X_test)} | Stations held out: {test_df["station_id"].nunique()}')

    models = build_models()
    comparison = {}

    best_model = None
    best_name = None
    best_metrics = None

    for name, model in models.items():
        print(f'\nTraining {name}…')
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        metrics = regression_metrics(y_test, pred)
        metrics['train_samples'] = len(X_train)
        metrics['test_samples'] = len(X_test)
        metrics['feature_importances'] = feature_importance_dict(model, cols)
        comparison[name] = metrics
        print(f'  R²={metrics["r2"]}  RMSE={metrics["rmse"]}  MAE={metrics["mae"]}')

        if name == args.export:
            best_model = model
            best_name = name
            best_metrics = metrics

    if best_model is None:
        best_name = args.export
        best_model = models[best_name]
        best_metrics = comparison[best_name]

    best_metrics['model_type'] = best_name
    best_metrics['features'] = cols

    paths = save_artifacts(best_model, cols, best_metrics, MODEL_DIR, comparison)
    print(f'\n✅ Exported {best_name} to:')
    for p in paths:
        print(f'   {p}')


if __name__ == '__main__':
    main()
