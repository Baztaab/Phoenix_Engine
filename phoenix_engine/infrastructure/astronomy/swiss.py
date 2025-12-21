
import swisseph as swe
from typing import Dict, Optional

class SwissEphemeris:
    def __init__(self, ephe_path: Optional[str] = None, sidereal_mode: int = swe.SIDM_LAHIRI):
        if ephe_path:
            swe.set_ephe_path(str(ephe_path))
        
        self.sidereal_mode = sidereal_mode
        swe.set_sid_mode(sidereal_mode, 0, 0)
        
        self.BODY_MAP = {
            swe.SUN: "Sun", swe.MOON: "Moon", swe.MARS: "Mars",
            swe.MERCURY: "Mercury", swe.JUPITER: "Jupiter",
            swe.VENUS: "Venus", swe.SATURN: "Saturn",
            swe.TRUE_NODE: "Rahu"
        }

    def get_ayanamsa(self, jd_ut: float) -> float:
        return swe.get_ayanamsa_ut(jd_ut)

    def calculate_all_bodies(self, jd_ut: float) -> Dict[str, Dict]:
        "محاسبه دقیق موقعیت سیارات (Legacy Name)"
        return self._calc(jd_ut)

    def calculate_planets(self, jd_ut: float) -> Dict[str, Dict]:
        "محاسبه دقیق موقعیت سیارات (Standard Name)"
        return self._calc(jd_ut)

    def _calc(self, jd_ut: float) -> Dict[str, Dict]:
        results = {}
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        
        for body_id, body_name in self.BODY_MAP.items():
            try:
                res = swe.calc_ut(jd_ut, body_id, flags)
                results[body_name] = {
                    "id": body_id,
                    "name": body_name,
                    "longitude": res[0][0],
                    "speed": res[0][3],
                    "is_retrograde": res[0][3] < 0,
                    "nakshatra": int(res[0][0] / 13.333333) + 1
                }
            except swe.Error:
                pass
        
        # محاسبه کتو
        if "Rahu" in results:
            rahu = results["Rahu"]
            ketu_long = (rahu["longitude"] + 180.0) % 360.0
            results["Ketu"] = {
                "id": 11, "name": "Ketu",
                "longitude": ketu_long,
                "speed": rahu["speed"],
                "is_retrograde": True,
                "nakshatra": int(ketu_long / 13.333333) + 1
            }
        return results

    def calculate_houses_sidereal(self, jd_ut: float, lat: float, lon: float, system: bytes = b'P') -> Dict:
        cusps_trop, ascmc_trop = swe.houses_ex(jd_ut, lat, lon, system)
        ayanamsa = self.get_ayanamsa(jd_ut)
        
        # ترفند برای دقت بالاتر: اگر بخواهیم دقیق‌تر باشیم از مدی که ست کردیم استفاده می‌کنیم
        # اما فعلاً منطق قبلی را حفظ می‌کنیم تا چیزی نشکند
        asc_sidereal = (ascmc_trop[0] - ayanamsa) % 360.0
        mc_sidereal = (ascmc_trop[1] - ayanamsa) % 360.0
        cusps_sidereal = [(c - ayanamsa) % 360.0 for c in cusps_trop]
        
        return {
            "ascendant": asc_sidereal,
            "mc": mc_sidereal,
            "ayanamsa": ayanamsa,
            "houses": cusps_sidereal
        }
