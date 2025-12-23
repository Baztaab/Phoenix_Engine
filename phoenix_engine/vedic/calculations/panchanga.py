import math
import swisseph as swe
from typing import Dict, Any, List

from phoenix_engine.core.context import ChartContext
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.vedic.calculations.vedic_math import VedicMath


class PanchangaEngine:
    """
    JHora-Standard Panchanga Engine.
    Features:
    - Vedic Sunrise (Disc Center, No Refraction).
    - Inverse Lagrange Interpolation for precise End Times.
    """

    WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # Vedic Rise Flags: Center of Disc, No Refraction
    # This differs from Western/Standard astronomical sunrise
    VEDIC_RISE_FLAGS = swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION

    def __init__(self, config):
        self.config = config
        self.sw_engine = SwissEphemeris(getattr(config, 'ephemeris_path', None))

    def calculate(self, ctx: ChartContext) -> Dict[str, Any]:
        jd = ctx.jd_ut
        lat = ctx.birth_data.lat
        lon = ctx.birth_data.lon

        # 1. Calculate Vedic Sunrise
        rise_set = self._get_vedic_rise_set(jd, lat, lon)
        sunrise_jd = rise_set["sunrise_jd"]

        # 2. Basic Positions at Birth Time
        sun_long = self._get_sidereal_pos(jd, swe.SUN)
        moon_long = self._get_sidereal_pos(jd, swe.MOON)

        # 3. Vara (Weekday)
        vara = self._calculate_vara(jd, rise_set)

        # 4. Tithi (with Lagrange)
        tithi = self._calculate_tithi_precision(jd, sunrise_jd, lat, lon)

        # 5. Nakshatra (with Lagrange)
        nak = self._calculate_nakshatra_precision(jd, sunrise_jd, lat, lon)

        # 6. Yoga (with Lagrange)
        yoga = self._calculate_yoga_precision(jd, sunrise_jd, lat, lon)

        # 7. Karana
        karana = self._calculate_karana(tithi["index_float"])

        return {
            "vara": vara,
            "tithi": tithi,
            "nakshatra": nak,
            "yoga": yoga,
            "karana": karana,
            "meta": {
                "vedic_sunrise_jd": sunrise_jd,
                "is_day_birth": vara["is_day_birth"]
            }
        }

    def _get_vedic_rise_set(self, jd: float, lat: float, lon: float) -> Dict[str, float]:
        """Calculates Sunrise/Sunset using strict Vedic flags."""
        res_rise = swe.rise_trans(
            tjd=jd - (5.5 / 24.0),
            body=swe.SUN,
            geopos=(lon, lat, 0.0),
            rsmi=self.VEDIC_RISE_FLAGS + swe.CALC_RISE
        )
        sunrise_jd = res_rise[1][0]

        res_set = swe.rise_trans(
            tjd=jd,
            body=swe.SUN,
            geopos=(lon, lat, 0.0),
            rsmi=self.VEDIC_RISE_FLAGS + swe.CALC_SET
        )
        sunset_jd = res_set[1][0]

        return {"sunrise_jd": sunrise_jd, "sunset_jd": sunset_jd}

    def _get_sidereal_pos(self, jd: float, body: int) -> float:
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        res = swe.calc_ut(jd, body, flags)
        return res[0][0]

    def _calculate_vara(self, jd: float, rise_set: Dict) -> Dict[str, Any]:
        sunrise = rise_set["sunrise_jd"]
        sunset = rise_set["sunset_jd"]

        is_day_birth = (jd >= sunrise) and (jd < sunset)

        effective_jd = jd if jd >= sunrise else jd - 1.0
        weekday_idx = swe.day_of_week(effective_jd)

        return {
            "name": self.WEEKDAYS[weekday_idx],
            "index": weekday_idx,
            "is_day_birth": is_day_birth
        }

    def _interpolate_end_time(self, start_jd: float, offsets: List[float], values: List[float], target_val: float) -> float:
        """Helper to call VedicMath.inverse_lagrange safely."""
        unwrapped_values = VedicMath.unwrap_angles(values)
        fraction = VedicMath.inverse_lagrange(offsets, unwrapped_values, target_val)
        return start_jd + fraction

    def _calculate_tithi_precision(self, jd: float, sunrise_jd: float, lat: float, lon: float) -> Dict[str, Any]:
        offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
        diffs = []

        for off in offsets:
            t_jd = jd + off
            s_lon = self._get_sidereal_pos(t_jd, swe.SUN)
            m_lon = self._get_sidereal_pos(t_jd, swe.MOON)
            diff = (m_lon - s_lon) % 360
            diffs.append(diff)

        current_diff = diffs[0]
        tithi_float = current_diff / 12.0
        tithi_index = int(tithi_float)

        target_angle = (tithi_index + 1) * 12.0

        try:
            end_time_jd = self._interpolate_end_time(jd, offsets, diffs, target_angle)
        except Exception:
            end_time_jd = jd + 1.0

        percentage = (current_diff % 12) / 12.0 * 100

        TITHI_NAMES = [
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
            "Trayodashi", "Chaturdashi", "Purnima",
            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
            "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
            "Trayodashi", "Chaturdashi", "Amavasya"
        ]

        return {
            "index": tithi_index + 1,
            "index_float": tithi_float,
            "name": TITHI_NAMES[tithi_index],
            "paksha": "Shukla" if tithi_index < 15 else "Krishna",
            "elapsed_percentage": round(percentage, 2),
            "end_time_jd": end_time_jd
        }

    def _calculate_nakshatra_precision(self, jd: float, sunrise_jd: float, lat: float, lon: float) -> Dict[str, Any]:
        offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
        lons = []

        for off in offsets:
            lons.append(self._get_sidereal_pos(jd + off, swe.MOON))

        current_lon = lons[0]
        nak_span = 360.0 / 27.0
        nak_float = current_lon / nak_span
        nak_index = int(nak_float)

        target_angle = (nak_index + 1) * nak_span

        try:
            end_time_jd = self._interpolate_end_time(jd, offsets, lons, target_angle)
        except Exception:
            end_time_jd = jd + 1.0

        percentage = (current_lon % nak_span) / nak_span * 100

        NAK_NAMES = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
            "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]

        return {
            "index": nak_index + 1,
            "name": NAK_NAMES[nak_index],
            "elapsed_percentage": round(percentage, 2),
            "end_time_jd": end_time_jd
        }

    def _calculate_yoga_precision(self, jd: float, sunrise_jd: float, lat: float, lon: float) -> Dict[str, Any]:
        offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
        sums = []

        for off in offsets:
            t_jd = jd + off
            s = self._get_sidereal_pos(t_jd, swe.SUN)
            m = self._get_sidereal_pos(t_jd, swe.MOON)
            sums.append((s + m) % 360)

        current_sum = sums[0]
        yoga_span = 360.0 / 27.0
        yoga_index = int(current_sum / yoga_span)

        target_angle = (yoga_index + 1) * yoga_span

        try:
            end_time_jd = self._interpolate_end_time(jd, offsets, sums, target_angle)
        except Exception:
            end_time_jd = jd + 1.0

        percentage = (current_sum % yoga_span) / yoga_span * 100

        YOGA_NAMES = [
            "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", "Sukarma", "Dhriti",
            "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi",
            "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
            "Brahma", "Indra", "Vaidhriti"
        ]

        return {
            "index": yoga_index + 1,
            "name": YOGA_NAMES[yoga_index],
            "elapsed_percentage": round(percentage, 2),
            "end_time_jd": end_time_jd
        }

    def _calculate_karana(self, tithi_float: float) -> Dict[str, Any]:
        karana_float = tithi_float * 2.0
        karana_index = int(karana_float)

        KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
        FIXED = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

        name = ""
        if karana_index == 0:
            name = "Kimstughna"
        elif 57 <= karana_index <= 59:
            name = FIXED[karana_index - 57]
        else:
            name = KARANAS[(karana_index - 1) % 7]

        return {
            "index": karana_index + 1,
            "name": name,
            "elapsed_percentage": (karana_float % 1) * 100
        }
