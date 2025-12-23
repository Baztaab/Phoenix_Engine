import swisseph as swe

from phoenix_engine.core.config import ChartConfig


class BirthChartEngine:
    """
    Pure calculation engine for natal charts.
    Computes planetary positions and houses without invoking any plugins.
    """

    def __init__(self, config: ChartConfig):
        self.config = config

    def calculate_natal_chart(
        self,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        lat: float,
        lon: float,
        name: str = "User",
    ):
        # 1) Julian Day
        hour_decimal = hour + (minute / 60.0) + (second / 3600.0)
        jd = swe.julday(year, month, day, hour_decimal)

        # 2) Sidereal mode (default Lahiri)
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # 3) Planets
        planets = {}
        planet_ids = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mars": swe.MARS,
            "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS,
            "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE,
        }

        for p_name, p_id in planet_ids.items():
            flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
            res = swe.calc_ut(jd, p_id, flags)
            lon_val = res[0][0]
            speed_val = res[0][3]

            planets[p_name] = {
                "name": p_name,
                "longitude": lon_val,
                "speed": speed_val,
                "is_retrograde": speed_val < 0,
                "coordinates": {
                    "sign_id": int(lon_val / 30) + 1,
                    "degree_in_sign": lon_val % 30,
                },
                "sign_name": self._get_sign_name(int(lon_val / 30) + 1),
            }

            if p_name == "Rahu":
                k_lon = (lon_val + 180) % 360
                planets["Ketu"] = {
                    "name": "Ketu",
                    "longitude": k_lon,
                    "speed": speed_val,
                    "is_retrograde": True,
                    "coordinates": {"sign_id": int(k_lon / 30) + 1, "degree_in_sign": k_lon % 30},
                    "sign_name": self._get_sign_name(int(k_lon / 30) + 1),
                }

        # 4) Houses / Ascendant (Placidus by default)
        h_sys = b"P"
        cusps, ascmc = swe.houses(jd, lat, lon, h_sys)
        asc_lon = ascmc[0]

        houses_data = {}
        for i, cusp in enumerate(cusps):
            sign_id = int(cusp / 30) + 1
            houses_data[i + 1] = {
                "longitude": cusp,
                "sign_id": sign_id,
                "sign_name": self._get_sign_name(sign_id),
            }

        return {
            "meta": {
                "jd": jd,
                "birth_date": f"{year}-{month:02d}-{day:02d}",
                "birth_time": f"{hour:02d}:{minute:02d}:{second:02d}",
                "location": {"lat": lat, "lon": lon},
                "name": name,
            },
            "planets": planets,
            "houses": houses_data,
            "ascendant": {
                "longitude": asc_lon,
                "sign_id": int(asc_lon / 30) + 1,
                "sign_name": self._get_sign_name(int(asc_lon / 30) + 1),
            },
        }

    def _get_sign_name(self, sign_id: int) -> str:
        signs = [
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
        return signs[sign_id - 1] if 1 <= sign_id <= 12 else "Unknown"

