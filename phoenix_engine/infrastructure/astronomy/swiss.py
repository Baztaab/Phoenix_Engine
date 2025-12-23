import swisseph as swe
from typing import Any, Dict, List, Optional, Tuple


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

    # --- Core Astronomy ---
    def get_ayanamsa(self, jd_ut: float) -> float:
        return swe.get_ayanamsa_ut(jd_ut)

    def calculate_planets(self, jd_ut: float) -> Dict[str, Dict]:
        results = {}
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL
        for body_id, body_name in self.BODY_MAP.items():
            try:
                res = swe.calc_ut(jd_ut, body_id, flags)
                results[body_name] = {
                    "id": body_id, "name": body_name,
                    "longitude": res[0][0], "speed": res[0][3],
                    "is_retrograde": res[0][3] < 0,
                    "nakshatra": int(res[0][0] / 13.333333) + 1
                }
            except swe.Error:
                pass
        if "Rahu" in results:
            rahu = results["Rahu"]
            ketu_long = (rahu["longitude"] + 180.0) % 360.0
            results["Ketu"] = {
                "id": 11, "name": "Ketu", "longitude": ketu_long,
                "speed": rahu["speed"], "is_retrograde": True,
                "nakshatra": int(ketu_long / 13.333333) + 1
            }
        return results

    def calculate_houses_sidereal(self, jd_ut: float, lat: float, lon: float, system: bytes = b'P') -> Dict:
        cusps_trop, ascmc_trop = swe.houses_ex(jd_ut, lat, lon, system)
        ayanamsa = self.get_ayanamsa(jd_ut)
        asc_sidereal = (ascmc_trop[0] - ayanamsa) % 360.0
        cusps_sidereal = [(c - ayanamsa) % 360.0 for c in cusps_trop]
        return {"ascendant": asc_sidereal, "houses": cusps_sidereal, "ayanamsa": ayanamsa}

    # --- THE FINAL FIX: Inspired by JHora + Windows Compatibility ---
    def get_rise_set(self, jd_ut: float, lat: float, lon: float) -> Tuple[float, float]:
        """
        Returns (sunrise_jd, sunset_jd).
        Strategy: Tries JHora style (kwargs) first, then falls back to Unpacked args for Windows C-Builds.
        """
        start_jd = jd_ut - 1.0  # Search starting from previous day
        geopos = (lon, lat, 0.0)
        
        def _calc(mode):
            # 1. JHora Style: Modern Keyword Arguments (Cleanest)
            try:
                return swe.rise_trans(start_jd, swe.SUN, geopos=geopos, rsmi=swe.FLG_SWIEPH | mode)
            except (TypeError, ValueError):
                pass

            # 2. Windows C-Extension Style (Unpacked Coordinates - No Tuple)
            # This fixes 'must be real number, not tuple'
            try:
                # Arg order: tjd, body, starname, epheflag, rsmi, lon, lat, height, press, temp
                # Note: Some versions skip starname for Planets.
                return swe.rise_trans(start_jd, swe.SUN, "", swe.FLG_SWIEPH, mode, lon, lat, 0.0, 0.0, 0.0)
            except (TypeError, ValueError):
                pass

            # 3. Minimalist / Old Version
            try:
                return swe.rise_trans(start_jd, swe.SUN, swe.FLG_SWIEPH, mode, lon, lat, 0.0)
            except (TypeError, ValueError):
                pass
            
            return None

        # Execute
        rise_flag = swe.CALC_RISE | swe.BIT_DISC_CENTER
        set_flag = swe.CALC_SET | swe.BIT_DISC_CENTER
        
        rise_res = _calc(rise_flag)
        set_res = _calc(set_flag)
        
        rise_jd = rise_res[1][0] if rise_res else 0.0
        set_jd = set_res[1][0] if set_res else 0.0
        
        return rise_jd, set_jd

    def get_ascendant(self, jd_ut: float, lat: float, lon: float) -> float:
        """
        Calculates just the Ascendant for a specific time.
        Used for Gulika/Mandi longitude calculation.
        """
        cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P')
        ayanamsa = self.get_ayanamsa(jd_ut)
        asc_sidereal = (ascmc[0] - ayanamsa) % 360.0
        return asc_sidereal


class SwissEphemerisEngine:
    """
    Thin wrapper around SwissEphemeris to provide high-level planet/house data
    tailored for ChartContext usage.
    """

    SIGN_NAMES = [
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
    ]

    def __init__(self, config: Any = None):
        # Default to Lahiri sidereal mode; ChartConfig can override in future.
        self.config = config
        self.swiss = SwissEphemeris(sidereal_mode=self._sidereal_mode())

    def sign_name(self, sign_id: int) -> str:
        idx = (sign_id - 1) % 12
        return self.SIGN_NAMES[idx]

    def _house_system_code(self, system: Any) -> bytes:
        """
        Translate house system input to Swiss code.
        Accepts first letter or bytes; defaults to Placidus.
        """
        if hasattr(system, "value"):
            return self._house_system_code(system.value)
        if isinstance(system, bytes):
            return system or b"P"
        if isinstance(system, str) and system:
            return system[0].upper().encode()
        return b"P"

    def _sidereal_mode(self) -> int:
        """
        Map configured ayanamsa to Swiss Ephemeris sidereal modes.
        Defaults to Lahiri.
        """
        aya = getattr(self.config, "ayanamsa", None)
        if hasattr(aya, "value"):
            aya = aya.value
        if isinstance(aya, str):
            key = aya.upper()
            if "RAMAN" in key:
                return swe.SIDM_RAMAN
            if key.startswith("KP"):
                return swe.SIDM_KRISHNAMURTI
            if "FAGAN" in key:
                return swe.SIDM_FAGAN_BRADLEY
        return swe.SIDM_LAHIRI

    def calculate_planets(self, jd_ut: float, lat: float, lon: float, asc_sign: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculate planetary positions; returns list of dicts ready for PlanetPosition model.
        If asc_sign provided, house is derived using simple equal-house offset.
        """
        raw_planets = self.swiss.calculate_planets(jd_ut)
        planet_list: List[Dict[str, Any]] = []

        for name, data in raw_planets.items():
            lon_val = data["longitude"]
            sign_id = int(lon_val / 30) + 1
            house_num = 0
            if asc_sign:
                house_num = (sign_id - asc_sign) % 12 + 1

            planet_list.append(
                {
                    "id": data["id"],
                    "name": name,
                    "longitude": lon_val,
                    "speed": data["speed"],
                    "is_retrograde": data["is_retrograde"],
                    "sign": sign_id,
                    "sign_name": self.sign_name(sign_id),
                    "degree": lon_val % 30,
                    "house": house_num,
                    "nakshatra": str(data.get("nakshatra", "")),
                    "nakshatra_pada": 0,
                }
            )

        return planet_list

    def calculate_houses(self, jd_ut: float, lat: float, lon: float, system: Any = b"P") -> Dict[str, Any]:
        """
        Calculate sidereal house cusps and ascendant; returns both raw cusps and structured mapping.
        """
        system_code = self._house_system_code(system)
        res = self.swiss.calculate_houses_sidereal(jd_ut, lat, lon, system_code)
        asc = res["ascendant"]
        cusps = res["houses"]

        houses_struct = {}
        for idx, cusp in enumerate(cusps, start=1):
            sign_id = int(cusp / 30) + 1
            houses_struct[idx] = {
                "longitude": cusp,
                "sign_id": sign_id,
                "sign_name": self.sign_name(sign_id),
            }

        return {
            "ascendant": asc,
            "cusps": cusps,
            "houses_struct": houses_struct,
            "ayanamsa": res.get("ayanamsa"),
        }
