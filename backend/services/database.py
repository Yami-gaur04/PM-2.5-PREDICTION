"""SQLite cache for grid and location predictions."""
import os
import sqlite3
from contextlib import contextmanager

from config import DB_PATH, CACHE_DIR


def init_db():
    os.makedirs(CACHE_DIR, exist_ok=True)
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_key TEXT, name TEXT, lat REAL, lon REAL,
                state TEXT, location_type TEXT, station TEXT,
                season INTEGER, pm25 REAL, aod REAL,
                aqi_category TEXT, color TEXT, updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS grid_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lat REAL, lon REAL, state TEXT, season INTEGER,
                step REAL, pm25 REAL, aqi_category TEXT, color TEXT
            );
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY, value TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_loc_season ON locations(season);
            CREATE INDEX IF NOT EXISTS idx_grid ON grid_points(season, step);
        """)


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def set_meta(key, value):
    with get_db() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)',
            (key, value),
        )
