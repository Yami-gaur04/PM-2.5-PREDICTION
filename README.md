# AirWatch India

**A Nationwide, Coordinate-Based PM2.5 Prediction Platform for India**

AirWatch India is a geospatial air quality prediction platform that uses satellite-based Aerosol Optical Depth (AOD), weather conditions, and ground-level monitoring data from CPCB and OpenAQ to predict PM2.5 concentrations across India.

Unlike city-dependent prediction systems, AirWatch India supports coordinate-based predictions for any location within India's geographical boundaries.

## 1. Architecture

The platform uses geographical coordinates, date and time, satellite data, and weather parameters to predict PM2.5 levels.

**Input:**
- Latitude and Longitude
- Date and Time
- Satellite AOD
- Weather Parameters
- Season

**Output:** Predicted PM2.5 concentration.

**Geographical Coverage:** 6.5°N–37.5°N latitude and 68°E–97.5°E longitude.

## 2. Project Structure

```text
AirWatchIndia/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── routes/
│   │   └── api.py
│   ├── services/
│   ├── utils/
│   ├── preprocessing/
│   ├── training/
│   ├── models/
│   └── requirements.txt
│
├── frontend/
│   ├── HTML
│   ├── CSS
│   └── JavaScript
│
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── stations/
│       └── pan_india_locations.json
│
├── notebooks/
└── requirements.txt
```

## 3. Installation and Setup

```bash
cd AirWatchIndia
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Data Preprocessing Pipeline

Place the required CSV files (CPCB, weather and AOD) inside `datasets/raw/`.

Run the preprocessing scripts:

```bash
python backend/preprocessing/load_cpcb.py --input datasets/raw/cpcb.csv

python backend/preprocessing/load_weather.py --input datasets/raw/weather.csv

python backend/preprocessing/load_aod.py --input datasets/raw/aod.csv

python backend/preprocessing/merge_datasets.py
```

For testing without actual datasets:

```bash
python backend/preprocessing/merge_datasets.py --sample
```

## 5. Model Training and Evaluation

The platform supports multiple machine learning models:

- Random Forest
- XGBoost 
- LightGBM 

Train the model using:

```bash
python backend/training/train.py --data datasets/processed/merged_training_data.csv --export xgboost

python backend/training/evaluate.py
```

The training process generates:

- `xgboost_pm25_model.joblib`
- `feature_columns.joblib`
- `model_metrics.json`
- `model_comparison.json`

A demo model can also be generated for local testing:

```bash
python backend/scripts/build_demo_model.py
```

The training pipeline uses a station-based holdout split to reduce spatial data leakage during model evaluation.

## 6. Running the Application

Start the Flask backend:

```bash
cd backend
python app.py
```

Open the dashboard at:

`http://localhost:5000`

For the complete NASA-inspired dashboard theme, the optional frontend CSS can be copied from the sibling project.

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks API status and model availability |
| POST | `/predict` | Predicts PM2.5 using input parameters |
| GET | `/predict-at?lat=&lon=` | Predicts PM2.5 at specific coordinates |
| GET | `/city-predictions` | Retrieves station-based predictions |
| GET | `/grid-predictions?step=2` | Generates geographical grid predictions |
| GET | `/trend?label=&days=30` | Retrieves historical trends |
| GET | `/model-metrics` | Returns model performance metrics |
| GET | `/state-rankings` | Ranks states by average PM2.5 |
| GET | `/cpcb-feed` | Retrieves ground monitoring station data |

### Sample Prediction Request

**POST `/predict`**

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

## 8. Technology Stack

**Backend & Machine Learning**
- Python
- Flask
- Scikit-learn
- XGBoost
- Pandas
- GeoPandas

**Frontend & Visualization**
- HTML5
- CSS3
- JavaScript
- Axios
- Chart.js
- Leaflet.js

## 9. License

This project is licensed under the MIT License and is intended for research, educational purposes and environmental awareness.

---

**Project:** AirWatch India  
**Category:** Geospatial Machine Learning | Environmental AI | Air Quality Prediction  
**Repository:** PM-2.5-PREDICTION
