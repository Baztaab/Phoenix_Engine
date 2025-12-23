from typing import Dict, List, Any

import swisseph as swe

from phoenix_engine.core.context import ChartContext


class DashaEngine:
    """
    High-Precision Vimshottari Dasha Engine.
    Standard: Matches Jagannatha Hora (JHora) logic strictly.

    Refactored by Kai to use Julian Day (JD) arithmetic exclusively.
    Eliminates Leap Year drift errors by bypassing calendar logic during calculation.
    """

    DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    DASHA_YEARS = {
        "Ketu": 7,
        "Venus": 20,
        "Sun": 6,
        "Moon": 10,
        "Mars": 7,
        "Rahu": 18,
        "Jupiter": 16,
        "Saturn": 19,
        "Mercury": 17,
    }

    # JHora Constants Reference:
    # sidereal_year = 365.256364 (Default in JHora)
    # savana_year = 360
    # average_gregorian_year = 365.2425
    #
    # We use Sidereal Year by default to match JHora's primary logic unless configured otherwise.
    SIDEREAL_YEAR = 365.256364
    SAVANA_YEAR = 360.0
    GREGORIAN_YEAR = 365.2425

    def __init__(self, config: Any = None):
        self.config = config
        # Default to JHora Standard (Sidereal) if not specified
        self.year_length = self.SIDEREAL_YEAR

        # Future-proofing: Allow config to override year type (Savana/Gregorian)
        if config and hasattr(config, "dasha_year_type"):
            if config.dasha_year_type == "SAVANA":
                self.year_length = self.SAVANA_YEAR
            elif config.dasha_year_type == "GREGORIAN":
                self.year_length = self.GREGORIAN_YEAR

    @staticmethod
    def _jd_to_date_str(jd: float) -> str:
        """Converts Julian Day to YYYY-MM-DD string safely."""
        y, m, d, _ = swe.revjul(jd)
        return f"{y:04d}-{m:02d}-{int(d):02d}"

    def _get_sub_periods_jd(
        self, main_lord: str, start_jd: float, main_duration_years: float, level: int
    ) -> List[Dict]:
        """Recursive JD-based sub-period calculator."""
        if level > 3:
            return []

        sub_periods: List[Dict[str, Any]] = []
        current_jd = start_jd

        start_idx = self.DASHA_LORDS.index(main_lord)
        ordered_lords = self.DASHA_LORDS[start_idx:] + self.DASHA_LORDS[:start_idx]

        for sub_lord in ordered_lords:
            # Formula: SubPeriod = (MainPeriod * SubPeriodYears) / 120
            sub_duration_years = (main_duration_years * self.DASHA_YEARS[sub_lord]) / 120.0
            duration_days = sub_duration_years * self.year_length

            end_jd = current_jd + duration_days

            period_data = {
                "lord": sub_lord,
                "start": self._jd_to_date_str(current_jd),
                "end": self._jd_to_date_str(end_jd),
                "start_jd": current_jd,
                "end_jd": end_jd,
                "duration_years": round(sub_duration_years, 4),
                "level": level,
                "sub_periods": [],
            }

            sub_periods.append(period_data)
            current_jd = end_jd

        return sub_periods

    def calculate_vimshottari(self, ctx: ChartContext) -> List[Dict]:
        """
        Calculates Vimshottari Dasha using strict Julian Day arithmetic.
        """
        moon = ctx.get_planet("Moon")
        if not moon:
            return []

        moon_lon = moon.longitude
        birth_jd = ctx.jd_ut

        # 1. Determine Starting State (Nakshatra)
        nak_span = 13.333333333
        nak_index_float = moon_lon / nak_span
        nak_index = int(nak_index_float)

        # Fraction of Nakshatra passed
        passed_fraction = nak_index_float - nak_index

        # Determine First Lord (Standard Sequence)
        first_lord_idx = nak_index % 9
        first_lord = self.DASHA_LORDS[first_lord_idx]

        # 2. Calculate Balance at Birth
        full_years_first = self.DASHA_YEARS[first_lord]
        spent_years = full_years_first * passed_fraction

        # 3. Determine Theoretical Start of the First Mahadasha
        spent_days = spent_years * self.year_length
        theoretical_start_jd = birth_jd - spent_days

        dashas: List[Dict[str, Any]] = []
        current_jd = theoretical_start_jd

        # 4. Generate Cycles (Covering 120+ years)
        for _ in range(2):  # two cycles cover 240 years
            for i in range(9):
                curr_lord_idx = (first_lord_idx + i) % 9
                lord = self.DASHA_LORDS[curr_lord_idx]

                duration_years = self.DASHA_YEARS[lord]
                duration_days = duration_years * self.year_length

                end_jd = current_jd + duration_days

                if end_jd > birth_jd:
                    antardashas = self._get_sub_periods_jd(lord, current_jd, duration_years, 2)

                    valid_antars = []
                    for ad in antardashas:
                        if ad["end_jd"] > birth_jd:
                            if ad["start_jd"] < birth_jd:
                                ad["start"] = self._jd_to_date_str(birth_jd)
                            valid_antars.append(ad)

                    display_start = self._jd_to_date_str(max(birth_jd, current_jd))

                    dasha_entry = {
                        "lord": lord,
                        "start": display_start,
                        "end": self._jd_to_date_str(end_jd),
                        "start_jd": max(birth_jd, current_jd),
                        "end_jd": end_jd,
                        "duration_years": duration_years,
                        "level": 1,
                        "sub_periods": valid_antars,
                    }
                    dashas.append(dasha_entry)

                current_jd = end_jd
                if len(dashas) >= 15:
                    break
            if len(dashas) >= 15:
                break

        return dashas
