# Colab training template

1. Upload `datasets/processed/merged_training_data.csv` or run merge on Colab.
2. Clone/copy `backend/training/` and `backend/preprocessing/`.
3. Run:

```python
!pip install xgboost lightgbm scikit-learn pandas joblib
!python backend/preprocessing/merge_datasets.py --sample  # or use your merged CSV
!python backend/training/train.py --export xgboost
```

4. Download `backend/models/xgboost_pm25_model.joblib` and `feature_columns.joblib`.
5. Place in local `AirWatchIndia/backend/models/` and run `python backend/app.py`.
