"""Historical PM2.5 trend simulation for dashboard charts."""
from datetime import datetime, timedelta

import numpy as np

from services.prediction_service import predict_at_coordinate
from utils.spatial import month_to_season


def get_trend(lat=None, lon=None, label=None, days=30, season=None):
    season = season if season is not None else month_to_season()
    if lat is None or lon is None:
        lat, lon = 28.61, 77.21
        label = label or 'Delhi'

    base = predict_at_coordinate(lat, lon, {'season': season})
    base_pm = base['pm25']

    rng = np.random.RandomState(int(lat * 1000 + lon * 100) % 2**31)
    dates = []
    values = []
    aqi_labels = []

    for i in range(days):
        dt = datetime.now() - timedelta(days=days - i - 1)
        noise = rng.normal(0, 6)
        seasonal = 8 * np.sin(2 * np.pi * i / 7)
        pm = max(5, base_pm + noise + seasonal)
        dates.append(dt.strftime('%Y-%m-%d'))
        values.append(round(float(pm), 1))
        from utils.aqi import get_aqi_category
        aqi_labels.append(get_aqi_category(pm)['label'])

    return {
        'label': label or f'{lat:.2f},{lon:.2f}',
        'latitude': lat,
        'longitude': lon,
        'dates': dates,
        'pm25': values,
        'aqi_categories': aqi_labels,
        'avg': round(float(np.mean(values)), 1),
        'max': round(float(np.max(values)), 1),
        'min': round(float(np.min(values)), 1),
    }
