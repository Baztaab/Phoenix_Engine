import swisseph as swe
from typing import Dict, Optional, Tuple
from datetime import datetime


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

    def calculate_planets(self, jd_ut: float) -> Dict[str, Dict]:
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
        
        # Ketu
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
        
        asc_sidereal = (ascmc_trop[0] - ayanamsa) % 360.0
        # MC, ARMC etc can be added here
        
        cusps_sidereal = [(c - ayanamsa) % 360.0 for c in cusps_trop]
        
        return {
            "ascendant": asc_sidereal,
            "houses": cusps_sidereal,
            "ayanamsa": ayanamsa
        }

    # --- SUNRISE/SUNSET CALCULATION ---
    def get_rise_set(self, jd_ut: float, lat: float, lon: float) -> Tuple[float, float]:
        """
        Returns (sunrise_jd, sunset_jd).
        Fix: Unpacks geopos into (lon, lat, height) to match the strict 7-argument signature of this swisseph version.
        Signature used: (tjd, body, flag, rsmi, lon, lat, height)
        """
        start_jd = jd_ut - 1.0
        
        try:
            rise_res = swe.rise_trans(
                start_jd, 
                swe.SUN, 
                swe.FLG_SWIEPH, 
                swe.CALC_RISE | swe.BIT_DISC_CENTER, 
                lon, 
                lat, 
                0.0  # Height
            )
            
            set_res = swe.rise_trans(
                start_jd, 
                swe.SUN, 
                swe.FLG_SWIEPH, 
                swe.CALC_SET | swe.BIT_DISC_CENTER, 
                lon, 
                lat, 
                0.0  # Height
            )
            
            rise_jd = rise_res[1][0] if rise_res and len(rise_res) > 1 else 0.0
            set_jd = set_res[1][0] if set_res and len(set_res) > 1 else 0.0
                
            return rise_jd, set_jd

        except swe.Error as e:
            print(f"SwissEph Error: {e}")
            return 0.0, 0.0
