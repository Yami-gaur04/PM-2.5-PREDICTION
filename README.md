# AirWatch India

Nationwide **coordinate-based** PM2.5 prediction platform for India using satellite AOD, weather, CPCB/OpenAQ ground data, and geospatial machine learning (XGBoost default).

## Architecture

```
(latitude, longitude, datetime, AOD, weather, season) → PM2.5
```

Not city-dependent — predicts at **any** location inside India (6.5°N–37.5°N, 68°E–97.5°E).

## Project structure

```
AirWatchIndia/
├── backend/
│   ├── app.py                 # Flask entry
│   ├── config.py
│   ├── routes/api.py          # REST API
│   ├── services/              # Prediction, grid, trends
│   ├── utils/                 # AQI, spatial, model loader
│   ├── preprocessing/         # CPCB, weather, AOD, merge
│   ├── training/              # train.py, evaluate.py
│   ├── models/                # Place trained .joblib here
│   └── requirements.txt
├── frontend/                  # HTML, CSS, JS, Leaflet, Chart.js
├── datasets/
│   ├── raw/                   # Your CSV uploads
│   ├── processed/
│   └── stations/pan_india_locations.json
├── notebooks/                 # Colab/Kaggle notebooks
└── requirements.txt
```

## Setup

```bash
cd AirWatchIndia
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Data pipeline

1. Place CSVs in `datasets/raw/` (cpcb, weather, aod).
2. Clean and merge:

```bash
python backend/preprocessing/load_cpcb.py --input datasets/raw/cpcb.csv
python backend/preprocessing/load_weather.py --input datasets/raw/weather.csv
python backend/preprocessing/load_aod.py --input datasets/raw/aod.csv
python backend/preprocessing/merge_datasets.py
```

For a **smoke-test** without real data:

```bash
python backend/preprocessing/merge_datasets.py --sample
```

## Training (Kaggle / Colab / local)

```bash
python backend/training/train.py --data datasets/processed/merged_training_data.csv --export xgboost
python backend/training/evaluate.py
```

Outputs:

- `backend/models/xgboost_pm25_model.joblib`
- `backend/models/feature_columns.joblib`
- `backend/models/model_metrics.json`
- `backend/models/model_comparison.json`

Quick local demo model:

```bash
python backend/scripts/build_demo_model.py
```

## Run API + dashboard

```bash
cd backend
python app.py
```

Open http://localhost:5000

### One-time frontend fix (if hero/nav HTML has extra closing tags)

```bash
python patch_frontend.py
```

## Optional: full theme CSS

For the complete NASA-style dashboard theme, copy from the sibling project:

`copy ..\frontend\style.css frontend\style.css` (Windows)

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Status, model loaded |
| POST | `/predict` | Body: `latitude`, `longitude`, `aod`, `temperature`, `humidity`, … |
| GET | `/predict-at?lat=&lon=` | Quick coordinate predict |
| GET | `/city-predictions` | All station predictions |
| GET | `/grid-predictions?step=2` | Map grid |
| GET | `/trend?label=&days=30` or `lat&lon` | Trend series |
| GET | `/model-metrics` | R², RMSE, feature importance |
| GET | `/state-rankings` | States by avg PM2.5 |
| GET | `/cpcb-feed` | Live station feed |

### POST /predict example

```json
{
  "latitude": 28.61,
  "longitude": 77.21,
  "aod": 0.52,
  "temperature": 32,
  "humidity": 65,
  "wind_speed": 2.1,
  "pressure": 1008,
  "rainfall": 0,
  "season": 2
}
```

## Models compared in training

- Random Forest
- **XGBoost** (default export)
- LightGBM (optional)

Station-based holdout split prevents spatial leakage.

## Tech stack

**Backend:** Python, Flask, scikit-learn, XGBoost, pandas, geopandas  
**Frontend:** HTML5, CSS3, vanilla JS, Axios, Chart.js, Leaflet.js

## License

MIT — use responsibly for research and environmental awareness.
