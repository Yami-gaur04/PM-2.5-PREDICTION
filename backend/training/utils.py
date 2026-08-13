"""Training utilities — metrics, splits, and artifact I/O."""
import json
import os

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {'r2': round(r2, 4), 'rmse': round(rmse, 4), 'mae': round(mae, 4)}


def save_artifacts(model, feature_columns, metrics, model_dir, comparison=None):
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'xgboost_pm25_model.joblib')
    features_path = os.path.join(model_dir, 'feature_columns.joblib')
    metrics_path = os.path.join(model_dir, 'model_metrics.json')

    joblib.dump(model, model_path)
    joblib.dump(list(feature_columns), features_path)
    with open(metrics_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    if comparison is not None:
        with open(os.path.join(model_dir, 'model_comparison.json'), 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)

    return model_path, features_path, metrics_path


def station_group_split(df, station_col='station_id', test_size=0.2, random_state=42):
    """Hold out entire stations to avoid spatial leakage."""
    stations = df[station_col].dropna().unique()
    rng = np.random.RandomState(random_state)
    rng.shuffle(stations)
    n_test = max(1, int(len(stations) * test_size))
    test_stations = set(stations[:n_test])
    mask = df[station_col].isin(test_stations)
    return df[~mask].copy(), df[mask].copy()


def feature_importance_dict(model, feature_names):
    if hasattr(model, 'feature_importances_'):
        imp = model.feature_importances_
        pairs = sorted(zip(feature_names, imp), key=lambda x: -x[1])
        total = sum(imp) or 1.0
        return {k: round(float(v) / total, 4) for k, v in pairs}
    return {}
