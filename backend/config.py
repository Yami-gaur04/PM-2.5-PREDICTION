"""AirWatch India — central configuration."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

# Artifact paths (place trained model here after Colab/Kaggle training)
MODEL_DIR = os.path.join(ROOT_DIR, 'backend', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'xgboost_pm25_model.joblib')
FEATURES_PATH = os.path.join(MODEL_DIR, 'feature_columns.joblib')
METRICS_PATH = os.path.join(MODEL_DIR, 'model_metrics.json')
COMPARISON_PATH = os.path.join(MODEL_DIR, 'model_comparison.json')

# Data paths
DATASETS_DIR = os.path.join(ROOT_DIR, 'datasets')
RAW_DIR = os.path.join(DATASETS_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATASETS_DIR, 'processed')
MERGED_CSV = os.path.join(PROCESSED_DIR, 'merged_training_data.csv')

STATIONS_PATH = os.path.join(DATASETS_DIR, 'stations', 'india_stations.json')
PAN_INDIA_PATH = os.path.join(DATASETS_DIR, 'stations', 'pan_india_locations.json')

CACHE_DIR = os.path.join(DATASETS_DIR, 'cache')
DB_PATH = os.path.join(CACHE_DIR, 'airwatch.db')
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')

# India bounding box
INDIA_LAT = (6.5, 37.5)
INDIA_LON = (68.0, 97.5)

# Grid
DEFAULT_GRID_STEP = 1.0
MIN_GRID_STEP = 0.5
MAX_GRID_STEP = 3.0

API_VERSION = '3.0.0'

# Default model type label
DEFAULT_MODEL_LABEL = 'XGBoost Geospatial'
