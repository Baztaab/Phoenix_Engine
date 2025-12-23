from typing import Optional, Dict

import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder


class GeoLocator:
    """
    Advanced global geo-spatial resolver.
    1) Offline cache for speed.
    2) Online lookup (Nominatim) for full coverage.
    3) Timezone detection via coordinates (DST-aware).
    """

    _INTERNAL_DB = {
        "tehran": {"lat": 35.6892, "lon": 51.3890, "tz": "Asia/Tehran"},
        "karaj": {"lat": 35.8355, "lon": 50.9915, "tz": "Asia/Tehran"},
        "mashhad": {"lat": 36.2605, "lon": 59.6168, "tz": "Asia/Tehran"},
        "shiraz": {"lat": 29.5918, "lon": 52.5837, "tz": "Asia/Tehran"},
        "isfahan": {"lat": 32.6546, "lon": 51.6680, "tz": "Asia/Tehran"},
        "london": {"lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
        "new york": {"lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
    }

    def __init__(self):
        self.geolocator = Nominatim(user_agent="phoenix_engine_v2")
        self.tf = TimezoneFinder()

    def resolve_city(self, city_name: str) -> Optional[Dict]:
        """
        Find coordinates and timezone. Cache first, then online lookup.
        """
        key = city_name.lower().strip()

        if key in self._INTERNAL_DB:
            print(f"   ⚡ [Cache Hit] Found '{city_name}' internally.")
            return self._INTERNAL_DB[key]

        try:
            print(f"   📡 [Online] Searching global grid for '{city_name}'...")
            location = self.geolocator.geocode(city_name)
            if location:
                lat, lon = location.latitude, location.longitude
                tz_str = self.tf.timezone_at(lng=lon, lat=lat) or "UTC"
                return {
                    "lat": lat,
                    "lon": lon,
                    "tz": tz_str,
                    "address": getattr(location, "address", city_name),
                }
        except Exception as e:
            print(f"   ⚠️ Geo-Lookup Error: {e}")

        return None


geo_instance = GeoLocator()


def resolve_city_wrapper(city_name: str):
    """Simple wrapper for CLI usage."""
    return geo_instance.resolve_city(city_name)

