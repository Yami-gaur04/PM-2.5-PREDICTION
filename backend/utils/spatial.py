"""Geospatial helpers for pan-India coverage."""
from datetime import datetime
import math

from config import INDIA_LAT, INDIA_LON

STATE_BOXES = [
    ('Jammu & Kashmir', 32.0, 36.5, 73.0, 80.5),
    ('Ladakh', 32.5, 36.2, 75.0, 80.0),
    ('Himachal Pradesh', 30.5, 33.5, 75.5, 79.5),
    ('Punjab', 29.5, 32.5, 73.5, 77.5),
    ('Uttarakhand', 28.5, 31.5, 77.0, 81.5),
    ('Haryana', 27.5, 30.5, 74.5, 77.8),
    ('Delhi', 28.4, 28.9, 76.8, 77.4),
    ('Rajasthan', 23.0, 30.5, 69.5, 78.5),
    ('Uttar Pradesh', 23.5, 30.5, 77.0, 84.5),
    ('Bihar', 24.0, 27.5, 83.0, 88.5),
    ('Jharkhand', 21.5, 25.5, 83.0, 88.0),
    ('West Bengal', 21.5, 27.5, 85.5, 89.5),
    ('Odisha', 17.5, 22.5, 81.5, 87.5),
    ('Chhattisgarh', 17.5, 24.5, 80.0, 84.5),
    ('Madhya Pradesh', 21.0, 26.5, 74.0, 82.5),
    ('Gujarat', 20.0, 24.5, 68.5, 74.5),
    ('Maharashtra', 15.5, 22.5, 72.5, 80.5),
    ('Goa', 14.5, 15.8, 73.5, 74.5),
    ('Karnataka', 11.5, 18.5, 74.0, 78.5),
    ('Kerala', 8.0, 12.5, 74.5, 77.5),
    ('Tamil Nadu', 8.0, 13.5, 76.0, 80.5),
    ('Andhra Pradesh', 12.5, 19.5, 76.5, 84.5),
    ('Telangana', 15.5, 20.0, 77.0, 81.5),
    ('Assam', 24.0, 28.5, 89.0, 96.5),
    ('Arunachal Pradesh', 26.5, 29.5, 91.5, 97.5),
    ('Manipur', 23.5, 25.5, 93.0, 94.5),
    ('Meghalaya', 25.0, 26.5, 89.5, 92.5),
    ('Mizoram', 22.0, 24.5, 92.0, 93.5),
    ('Nagaland', 25.0, 27.5, 93.0, 95.5),
    ('Tripura', 22.5, 24.5, 91.0, 92.5),
    ('Sikkim', 26.5, 28.5, 87.5, 89.5),
    ('Puducherry', 11.5, 12.2, 79.5, 79.9),
    ('Chandigarh', 30.6, 30.85, 76.6, 76.85),
    ('Andaman & Nicobar', 6.5, 14.5, 92.0, 94.5),
]

POLLUTION_BELTS = [
    {'lat': 27.0, 'lon': 82.0, 'weight': 0.55},
    {'lat': 28.5, 'lon': 76.0, 'weight': 0.35},
    {'lat': 24.0, 'lon': 86.0, 'weight': 0.40},
]


def month_to_season(month=None):
    month = month or datetime.now().month
    if month in (12, 1, 2):
        return 0
    if month in (3, 4, 5):
        return 1
    if month in (6, 7, 8, 9):
        return 2
    return 3


def season_name(season):
    return ['Winter', 'Summer', 'Monsoon', 'Post-Monsoon'][int(season)]


def is_in_india(lat, lon):
    return INDIA_LAT[0] <= float(lat) <= INDIA_LAT[1] and INDIA_LON[0] <= float(lon) <= INDIA_LON[1]


def latlon_to_state(lat, lon):
    for name, lat_min, lat_max, lon_min, lon_max in STATE_BOXES:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return name
    return 'India'


def deg_distance(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)


def estimate_aod(lat, lon):
    """INSAT-style regional AOD prior when satellite AOD is unavailable."""
    aod = 0.18
    for belt in POLLUTION_BELTS:
        d = deg_distance(lat, lon, belt['lat'], belt['lon'])
        aod += belt['weight'] * max(0, 0.5 - d * 0.06)
    if lat < 14 or lon > 92:
        aod *= 0.80
    if lat > 30 and lon < 76:
        aod *= 0.86
    return float(max(0.10, min(1.20, aod)))


def estimate_elevation(lat, lon):
    """Lightweight elevation proxy (m) — replace with DEM in production."""
    return float(max(0, 2500 - abs(lat - 23) * 80 - abs(lon - 78) * 40))


def estimate_population_density(lat, lon):
    """Population density proxy (people/km²)."""
    urban_centers = [
        (28.61, 77.21, 25000), (19.08, 72.88, 22000), (12.97, 77.59, 18000),
        (22.57, 88.36, 19000), (17.39, 78.49, 15000),
    ]
    density = 200.0
    for clat, clon, peak in urban_centers:
        d = deg_distance(lat, lon, clat, clon)
        density += peak * max(0, 1 - d * 0.15)
    return float(min(density, 30000))
