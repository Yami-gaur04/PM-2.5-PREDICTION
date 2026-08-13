"""
Generate a small demo XGBoost model from synthetic data (local smoke test).

Usage (from AirWatchIndia/):
  python backend/scripts/build_demo_model.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from preprocessing.merge_datasets import generate_sample_merged
from config import MERGED_CSV, MODEL_DIR
from training.train import main as train_main


if __name__ == '__main__':
    print('Generating sample merged CSV…')
    generate_sample_merged(MERGED_CSV, n_rows=3000)
    print('Training demo XGBoost model…')
    sys.argv = ['train.py', '--data', MERGED_CSV, '--export', 'xgboost']
    train_main()
