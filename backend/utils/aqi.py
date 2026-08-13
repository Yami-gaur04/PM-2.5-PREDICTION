"""Indian AQI categories for PM2.5 (CPCB-style bands)."""


def get_aqi_category(pm25: float) -> dict:
    """Return label and hex color for PM2.5 concentration."""
    pm = float(pm25)
    if pm <= 30:
        return {'label': 'Good', 'color': '#10B981', 'severity': 1}
    if pm <= 60:
        return {'label': 'Satisfactory', 'color': '#84CC16', 'severity': 2}
    if pm <= 90:
        return {'label': 'Moderate', 'color': '#F59E0B', 'severity': 3}
    if pm <= 120:
        return {'label': 'Poor', 'color': '#EF4444', 'severity': 4}
    if pm <= 250:
        return {'label': 'Very Poor', 'color': '#A855F7', 'severity': 5}
    return {'label': 'Severe', 'color': '#7F1D1D', 'severity': 6}


def pm25_to_aqi_index(pm25: float) -> int:
    """Approximate CPCB AQI sub-index from PM2.5."""
    pm = float(pm25)
    breaks = [(0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
              (91, 120, 201, 300), (121, 250, 301, 400), (251, 500, 401, 500)]
    for lo, hi, aqi_lo, aqi_hi in breaks:
        if lo <= pm <= hi:
            return int(round(aqi_lo + (pm - lo) * (aqi_hi - aqi_lo) / max(hi - lo, 1)))
    return 500
