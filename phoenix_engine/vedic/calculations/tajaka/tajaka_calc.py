import swisseph as swe
from datetime import datetime
from typing import Dict, Any, Tuple

import pytz

from phoenix_engine.vedic.const import SUN


class TajakaCalculator:
    """
    Advanced Varshaphal (annual chart) calculator inspired by JHora.
    Uses iterative refinement to find the solar return to sub-second precision.
    """

    @staticmethod
    def get_solar_return_time(natal_jd: float, target_year: int, birth_year: int) -> Tuple[float, datetime]:
        """
        Compute precise solar return (Varshaphal) moment via Newton-Raphson.
        Returns (jd_ut, datetime_utc).
        """
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

        # 1) Natal Sun longitude
        natal_sun = swe.calc_ut(natal_jd, SUN, flags)[0][0]

        # 2) Initial estimate using sidereal year
        SIDEREAL_YEAR_DAYS = 365.256363004
        years_diff = target_year - birth_year
        current_jd = natal_jd + (years_diff * SIDEREAL_YEAR_DAYS)

        # 3) Newton-Raphson refinement
        for _ in range(15):
            sun_res = swe.calc_ut(current_jd, SUN, flags | swe.FLG_SPEED)
            current_sun_lon = sun_res[0][0]
            sun_speed = sun_res[0][3]  # deg/day

            # shortest angular difference
            diff = (natal_sun - current_sun_lon + 180.0) % 360.0 - 180.0
            if abs(diff) < 0.00001:  # ~0.3 arc-sec -> sub-second time accuracy
                break

            current_jd += diff / sun_speed

        # 4) Convert JD to aware UTC datetime
        y, m, d, h_dec = swe.revjul(current_jd)
        h = int(h_dec)
        mn = int((h_dec - h) * 60)
        s = int((((h_dec - h) * 60) - mn) * 60)
        return_dt = datetime(y, m, d, h, mn, s, tzinfo=pytz.utc)

        return current_jd, return_dt

    @staticmethod
    def calculate_muntha(natal_asc_sign: int, birth_year: int, target_year: int) -> Dict[str, Any]:
        """
        Compute Muntha (progressed ascendant) sign.
        Formula: (natal_asc + years_completed) % 12
        """
        years_completed = target_year - birth_year
        muntha_sign_idx = (natal_asc_sign - 1 + years_completed) % 12
        muntha_sign = muntha_sign_idx + 1

        return {
            "sign_id": muntha_sign,
            "sign_name": [
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
                "Capricorn",
                "Aquarius",
                "Pisces",
            ][muntha_sign_idx],
            "progressed_years": years_completed,
        }

    @staticmethod
    def determine_year_lord(candidates: Dict[str, Dict], chart_strength: Dict) -> str:
        """
        Placeholder for Varsheshwara logic.
        Would compare strengths (Vimsopaka Bala, aspects to annual ascendant, etc.).
        """
        return "Not Implemented Yet"
