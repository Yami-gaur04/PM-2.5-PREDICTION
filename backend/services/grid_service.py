"""Pan-India grid predictions for map visualization."""
import numpy as np

from config import INDIA_LAT, INDIA_LON, DEFAULT_GRID_STEP
from services.prediction_service import predict_at_coordinate
from services.database import init_db, get_db
from utils.spatial import month_to_season, latlon_to_state


def generate_grid(step=1.0, season=None):
    season = season if season is not None else month_to_season()
    lat_min, lat_max = INDIA_LAT
    lon_min, lon_max = INDIA_LON

    lats = np.arange(lat_min, lat_max + step * 0.5, step)
    lons = np.arange(lon_min, lon_max + step * 0.5, step)

    points = []
    for lat in lats:
        for lon in lons:
            pred = predict_at_coordinate(float(lat), float(lon), {'season': season})
            points.append({
                'lat': float(lat),
                'lon': float(lon),
                'state': pred['state'],
                'pm25': pred['pm25'],
                'aqi_category': pred['aqi_category'],
                'color': pred['aqi_color'],
            })
    return points


def get_grid(step=DEFAULT_GRID_STEP, season=None, rebuild=False):
    season = season if season is not None else month_to_season()
    if not rebuild:
        init_db()
        with get_db() as conn:
            rows = conn.execute(
                'SELECT lat, lon, state, pm25, aqi_category, color FROM grid_points WHERE season=? AND step=?',
                (season, step),
            ).fetchall()
        if rows:
            pts = [dict(r) for r in rows]
            return {'step': step, 'season': season, 'count': len(pts), 'points': pts, 'source': 'cache'}

    points = generate_grid(step, season)
    init_db()
    with get_db() as conn:
        conn.execute('DELETE FROM grid_points WHERE season=? AND step=?', (season, step))
        conn.executemany(
            'INSERT INTO grid_points (lat, lon, state, season, step, pm25, aqi_category, color) VALUES (?,?,?,?,?,?,?,?)',
            [(p['lat'], p['lon'], p['state'], season, step, p['pm25'], p['aqi_category'], p['color']) for p in points],
        )
    return {'step': step, 'season': season, 'count': len(points), 'points': points, 'source': 'computed'}


def state_rankings(step=DEFAULT_GRID_STEP, season=None):
    grid = get_grid(step, season)
    by_state = {}
    for p in grid['points']:
        st = p['state']
        by_state.setdefault(st, []).append(p['pm25'])
    rankings = [
        {
            'state': st,
            'avg_pm25': round(float(np.mean(vals)), 1),
            'max_pm25': round(float(np.max(vals)), 1),
            'stations': len(vals),
        }
        for st, vals in by_state.items()
    ]
    rankings.sort(key=lambda x: -x['avg_pm25'])
    for i, r in enumerate(rankings, 1):
        r['rank'] = i
    return rankings
