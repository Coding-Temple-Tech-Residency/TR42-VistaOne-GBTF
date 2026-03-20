from math import atan2, cos, radians, sin, sqrt

import requests
from flask import current_app


def geocode_address(address):
    """Convert address to coordinates using Mapbox."""
    token = current_app.config.get("MAPBOX_ACCESS_TOKEN")
    if not token:
        return None
    url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{}.json"
    resp = requests.get(
        url.format(address),
        params={"access_token": token, "limit": 1},
    )
    if resp.status_code == 200:
        features = resp.json().get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]
            return {"lng": coords[0], "lat": coords[1]}
    return None


def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance in miles between two points (Haversine)."""
    R = 3958.8  # miles
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
