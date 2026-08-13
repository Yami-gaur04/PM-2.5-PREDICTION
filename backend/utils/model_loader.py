"""Load trained PM2.5 model and run coordinate-based inference."""
import json
import os

import joblib
import numpy as np

from config import MODEL_PATH, FEATURES_PATH, METRICS_PATH, DEFAULT_MODEL_LABEL
from utils.aqi import get_aqi_category
from utils.geo_features import (
    BASE_FEATURE_COLUMNS,
    build_features_from_request,
    demo_pm25_formula,
    features_to_vector,
)

_model = None
_feature_columns = None
_metrics = None


def load_model():
    global _model, _feature_columns, _metrics
    try:
        _model = joblib.load(MODEL_PATH)
        _feature_columns = joblib.load(FEATURES_PATH)
        if os.path.isfile(METRICS_PATH):
            with open(METRICS_PATH, encoding='utf-8') as f:
                _metrics = json.load(f)
        print(f'✅ Model loaded: {MODEL_PATH}')
        print(f'✅ Features: {len(_feature_columns)} columns')
        return True
    except Exception as exc:
        print(f'⚠️  Model not loaded ({exc}). Using demo formula.')
        _model = None
        _feature_columns = BASE_FEATURE_COLUMNS
        _metrics = None
        return False


def model_loaded():
    return _model is not None


def feature_names():
    return list(_feature_columns or BASE_FEATURE_COLUMNS)


def get_stored_metrics():
    return _metrics or {}


def predict_pm25(data: dict, source_label=None):
    features = build_features_from_request(data)
    cols = _feature_columns or BASE_FEATURE_COLUMNS
    X = features_to_vector(features, cols)

    if _model is not None:
        pm25 = float(_model.predict(X)[0])
        label = source_label or DEFAULT_MODEL_LABEL
        if _metrics and 'r2' in _metrics:
            source = f'{label} (R²={_metrics["r2"]:.4f})'
        else:
            source = label
    else:
        pm25 = demo_pm25_formula(features)
        source = 'Demo geospatial formula (train model to enable ML)'

    pm25 = round(max(5.0, min(500.0, pm25)), 2)
    aqi = get_aqi_category(pm25)
    return pm25, aqi, source, features
