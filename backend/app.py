"""
AirWatch India — Flask API
Run from backend/:  python app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS

from config import FRONTEND_DIR
from routes.api import api
from utils import model_loader
from services.database import init_db
from services.location_service import build_city_predictions
from services.grid_service import get_grid
from utils.spatial import month_to_season

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)
app.register_blueprint(api)


@app.route('/<path:path>')
def static_files(path):
    from flask import send_from_directory
    return send_from_directory(FRONTEND_DIR, path)


if __name__ == '__main__':
    print('\n🛰️  AirWatch India — Nationwide PM2.5 Engine')
    init_db()
    model_loader.load_model()

    season = month_to_season()
    try:
        print('Building location cache…')
        locs = build_city_predictions(season)
        print(f'  → {len(locs)} stations')
        print('Building grid cache (step=2.0 for fast startup)…')
        grid = get_grid(step=2.0, season=season, rebuild=True)
        print(f'  → {grid["count"]} grid cells')
    except Exception as exc:
        print(f'⚠️  Cache build skipped: {exc}')

    print('   http://localhost:5000\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
