"""Named station / city predictions (derived from coordinate engine)."""
import json
import os
from datetime import datetime

from config import PAN_INDIA_PATH
from services.prediction_service import predict_at_coordinate
from utils.spatial import month_to_season
from services.database import init_db, get_db


def load_stations():
    if os.path.isfile(PAN_INDIA_PATH):
        with open(PAN_INDIA_PATH, encoding='utf-8') as f:
            return json.load(f)
    return [
        {'name': 'Delhi', 'station': 'Anand Vihar CPCB', 'lat': 28.61, 'lon': 77.21, 'state': 'Delhi', 'type': 'cpcb'},
        {'name': 'Mumbai', 'station': 'Bandra East CPCB', 'lat': 19.08, 'lon': 72.88, 'state': 'Maharashtra', 'type': 'cpcb'},
        {'name': 'Kolkata', 'station': 'Jadavpur CPCB', 'lat': 22.57, 'lon': 88.36, 'state': 'West Bengal', 'type': 'cpcb'},
        {'name': 'Chennai', 'station': 'Alandur CPCB', 'lat': 13.08, 'lon': 80.27, 'state': 'Tamil Nadu', 'type': 'cpcb'},
        {'name': 'Bengaluru', 'station': 'BTM Layout CPCB', 'lat': 12.97, 'lon': 77.59, 'state': 'Karnataka', 'type': 'cpcb'},
        {'name': 'Hyderabad', 'station': 'Bollaram CPCB', 'lat': 17.39, 'lon': 78.49, 'state': 'Telangana', 'type': 'cpcb'},
    ]


def build_city_predictions(season=None, persist=True):
    season = season if season is not None else month_to_season()
    records = []
    for loc in load_stations():
        pred = predict_at_coordinate(loc['lat'], loc['lon'], {'season': season})
        records.append({
            'name': loc.get('name', 'Unknown'),
            'city': loc.get('name', 'Unknown'),
            'station': loc.get('station', f"{loc.get('name')} — ML estimate"),
            'lat': loc['lat'],
            'lon': loc['lon'],
            'state': loc.get('state', pred['state']),
            'location_type': loc.get('type', 'cpcb'),
            'season': season,
            'pm25': pred['pm25'],
            'aod': pred['features_used']['aod'],
            'aqi_category': pred['aqi_category'],
            'color': pred['aqi_color'],
            'updated_at': datetime.now().isoformat(),
        })

    if persist:
        init_db()
        with get_db() as conn:
            conn.execute('DELETE FROM locations WHERE season = ?', (season,))
            conn.executemany(
                """INSERT INTO locations (
                    name, lat, lon, state, location_type, station, season,
                    pm25, aod, aqi_category, color, updated_at, location_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [(
                    r['name'], r['lat'], r['lon'], r['state'], r['location_type'],
                    r['station'], r['season'], r['pm25'], r['aod'],
                    r['aqi_category'], r['color'], r['updated_at'], f"{r['name']}_{season}",
                ) for r in records],
            )
    return records


def get_city_predictions(season=None):
    season = season if season is not None else month_to_season()
    init_db()
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM locations WHERE season = ? ORDER BY pm25 DESC',
            (season,),
        ).fetchall()
    if rows:
        return [dict(r) for r in rows]
    return build_city_predictions(season, persist=True)
