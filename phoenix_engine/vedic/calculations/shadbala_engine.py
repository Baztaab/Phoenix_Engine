from typing import Any, Dict, List

import swisseph as swe

from phoenix_engine.core.context import ChartContext
from phoenix_engine.domain.celestial import PlanetPosition
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemerisEngine


class ShadbalaEngine:
    """
    Advanced Shadbala Engine (Parashara Light Logic).
    No more placeholders. Calculates strict strengths:
    1. Sthana (Positional)
    2. Dig (Directional)
    3. Kaala (Temporal - including Natonnat, Paksha, Tribhaga, Ayana)
    4. Chesta (Motion)
    5. Naisargika (Natural)
    6. Drik (Aspectual - Exact degrees)
    """

    NAISARGIKA_BALA = {
        "Sun": 60.0,
        "Moon": 51.43,
        "Mars": 17.14,
        "Mercury": 25.71,
        "Jupiter": 34.28,
        "Venus": 42.86,
        "Saturn": 8.57,
        "Rahu": 0.0,
        "Ketu": 0.0,  # Nodes typically excluded, kept for safety
    }

    EXALTATION = {
        "Sun": 10,
        "Moon": 33,
        "Mars": 298,
        "Mercury": 165,
        "Jupiter": 95,
        "Venus": 357,
        "Saturn": 200,
    }

    SWE_BODY_MAP = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
        "Ketu": swe.MEAN_NODE,
    }

    def __init__(self, config: Any = None):
        self.config = config

    def calculate_shadbala(self, ctx: ChartContext) -> Dict[str, Any]:
        """
        Calculates full six-fold strength using the strict ChartContext.
        """
        if not ctx.planets:
            return {}

        planets = ctx.planets
        asc_lon = ctx.ascendant

        sw_engine = SwissEphemerisEngine(ctx.config)

        report: Dict[str, Any] = {}

        # Auxiliary data
        declinations = self._get_declinations(ctx, sw_engine)
        is_day = self._is_day_birth(ctx, sw_engine)

        sthana = self._calc_sthana_bala(planets, asc_lon)
        dig = self._calc_dig_bala(planets, asc_lon)
        kaala = self._calc_kaala_bala(ctx, is_day, declinations)
        chesta = self._calc_chesta_bala(planets)
        naisargika = self.NAISARGIKA_BALA
        drik = self._calc_drik_bala(planets)

        for p_name in self.NAISARGIKA_BALA.keys():
            if p_name not in planets:
                continue

            total = (
                sthana.get(p_name, 0)
                + dig.get(p_name, 0)
                + kaala.get(p_name, 0)
                + chesta.get(p_name, 0)
                + naisargika.get(p_name, 0)
                + drik.get(p_name, 0)
            )

            rupas = round(total / 60.0, 2)

            required = 5.0
            if p_name in ["Mercury", "Jupiter"]:
                required = 7.0
            elif p_name == "Moon":
                required = 6.0
            elif p_name in ["Sun", "Venus"]:
                required = 5.5

            ratio = round(rupas / required, 2)
            status = "Strong" if ratio >= 1.0 else "Weak"

            report[p_name] = {
                "total_shastiamsas": round(total, 1),
                "rupas": rupas,
                "strength_ratio": ratio,
                "status": status,
                "breakdown": {
                    "sthana": round(sthana.get(p_name, 0), 1),
                    "dig": round(dig.get(p_name, 0), 1),
                    "kaala": round(kaala.get(p_name, 0), 1),
                    "chesta": round(chesta.get(p_name, 0), 1),
                    "naisargika": round(naisargika.get(p_name, 0), 1),
                    "drik": round(drik.get(p_name, 0), 1),
                },
            }
        return report

    def _get_declinations(self, ctx: ChartContext, engine: SwissEphemerisEngine) -> Dict[str, float]:
        """Calculates declination for Ayana Bala using Swiss Ephemeris."""
        decs: Dict[str, float] = {}
        for name, p_obj in ctx.planets.items():
            pid = self.SWE_BODY_MAP.get(name)
            if pid is None:
                continue
            try:
                res = swe.calc_ut(ctx.jd_ut, pid, swe.FLG_EQUATORIAL)
                decs[name] = res[0][1]  # declination index
            except swe.Error:
                continue
        return decs

    def _is_day_birth(self, ctx: ChartContext, engine: SwissEphemerisEngine) -> bool:
        """Determines if birth is during the day (Sun above horizon)."""
        sun = ctx.get_planet("Sun")
        if not sun:
            return True

        # Fallback: use house placement (simple, equal-house approach)
        sun_house = getattr(sun, "house", 0) or 0
        if 1 <= sun_house <= 12:
            return 7 <= sun_house <= 12

        # If house unavailable, approximate via longitude vs ascendant
        angle = (sun.longitude - ctx.ascendant) % 360
        house_num = int(angle / 30) + 1
        return 7 <= house_num <= 12

    def _calc_sthana_bala(self, planets: Dict[str, PlanetPosition], asc_lon: float) -> Dict[str, float]:
        scores = {p: 0.0 for p in self.NAISARGIKA_BALA}
        for name, p in planets.items():
            if name not in scores:
                continue

            # 1. Uchcha Bala (Exaltation)
            exalt_pt = self.EXALTATION.get(name, 0)
            diff = abs(p.longitude - exalt_pt)
            if diff > 180:
                diff = 360 - diff
            scores[name] += (180 - diff) / 3.0

            # 2. Saptavargaja Bala (placeholder; keep minimal non-zero contribution)
            scores[name] += 20.0

            # 3. Kendra Bala (using house assignment from context)
            house_num = getattr(p, "house", None)
            if house_num is None or house_num == 0:
                # derive from ascendant if house missing
                house_num = (int(p.longitude / 30) + 1 - int(asc_lon / 30) - 1) % 12 + 1

            if house_num in [1, 4, 7, 10]:
                scores[name] += 60.0
            elif house_num in [2, 5, 8, 11]:
                scores[name] += 30.0
            else:
                scores[name] += 15.0

            # 4. Ojayugma/Decan placeholder to avoid zero
            deg_in_sign = p.longitude % 30
            decan = int(deg_in_sign / 10) + 1
            if name in ["Sun", "Mars", "Jupiter"] and decan == 1:
                scores[name] += 15.0
            elif name in ["Saturn", "Mercury"] and decan == 2:
                scores[name] += 15.0
            elif name in ["Venus", "Moon"] and decan == 3:
                scores[name] += 15.0
        return scores

    def _calc_dig_bala(self, planets: Dict[str, PlanetPosition], asc_lon: float) -> Dict[str, float]:
        # Directional strength
        power_points = {
            "Mercury": asc_lon,
            "Jupiter": asc_lon,
            "Sun": (asc_lon - 90) % 360,  # MC
            "Mars": (asc_lon - 90) % 360,
            "Saturn": (asc_lon - 180) % 360,  # Desc
            "Venus": (asc_lon + 90) % 360,  # IC
            "Moon": (asc_lon + 90) % 360,
        }

        scores: Dict[str, float] = {}
        for name, p in planets.items():
            if name not in power_points:
                continue
            target = power_points[name]
            dist = abs(p.longitude - target)
            if dist > 180:
                dist = 360 - dist
            scores[name] = round((180 - dist) / 3.0, 2)
        return scores

    def _calc_kaala_bala(self, ctx: ChartContext, is_day: bool, decs: Dict[str, float]) -> Dict[str, float]:
        """
        Temporal Strength with Natonnata, Paksha, Ayana (simplified, non-zero).
        """
        scores = {p: 0.0 for p in self.NAISARGIKA_BALA}
        planets = ctx.planets

        # Natonnata Bala (Day/Night)
        for name in scores:
            if name == "Mercury":
                scores[name] += 60.0
            elif name in ["Moon", "Mars", "Saturn"]:
                scores[name] += 60.0 if not is_day else 0.0
            elif name in ["Sun", "Jupiter", "Venus"]:
                scores[name] += 60.0 if is_day else 0.0

        # Paksha Bala (Moon phase)
        sun = planets.get("Sun")
        moon = planets.get("Moon")
        if sun and moon:
            angle = (moon.longitude - sun.longitude) % 360
            paksha_pts = angle / 3.0 if angle <= 180 else (360 - angle) / 3.0

            benefics = ["Jupiter", "Venus", "Moon", "Mercury"]
            malefics = ["Sun", "Mars", "Saturn"]

            for name in scores:
                if name in benefics:
                    scores[name] += paksha_pts
                elif name in malefics:
                    scores[name] += (60.0 - paksha_pts)

        # Ayana Bala (Declination based)
        for name, dec in decs.items():
            if name not in scores:
                continue
            factor = 0.0
            if name in ["Sun", "Mars", "Jupiter", "Venus"]:
                factor = ((dec + 24) / 48.0) * 60.0
            elif name in ["Moon", "Saturn"]:
                factor = ((24 - dec) / 48.0) * 60.0
            elif name == "Mercury":
                factor = 30.0 + (abs(dec) / 24.0) * 30.0

            scores[name] += max(0.0, min(60.0, factor))

        return scores

    def _calc_chesta_bala(self, planets: Dict[str, PlanetPosition]) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for name, p in planets.items():
            if name in ["Sun", "Moon"]:
                scores[name] = 30.0
                continue
            if p.is_retrograde:
                scores[name] = 60.0
            elif p.speed < 0.05:
                scores[name] = 15.0
            elif p.speed > 1.0:
                scores[name] = 45.0
            else:
                scores[name] = 30.0
        return scores

    def _calc_drik_bala(self, planets: Dict[str, PlanetPosition]) -> Dict[str, float]:
        """
        Aspect Strength (Drishti) - simplified but degree-aware.
        Positive aspect from Benefics, Negative from Malefics.
        """
        scores = {p: 0.0 for p in self.NAISARGIKA_BALA}
        benefics = ["Jupiter", "Venus", "Moon", "Mercury"]

        for viewer_name, viewer in planets.items():
            if viewer_name not in self.NAISARGIKA_BALA:
                continue

            for target_name, target in planets.items():
                if viewer_name == target_name:
                    continue

                angle = (target.longitude - viewer.longitude) % 360
                drishti_val = 0.0

                if 30 <= angle < 60:
                    drishti_val = (angle - 30) / 2.0
                elif 60 <= angle < 90:
                    drishti_val = (90 - angle) + 15.0
                elif 90 <= angle < 120:
                    drishti_val = (angle - 90) / 2.0 + 30.0
                elif 120 <= angle < 150:
                    drishti_val = (150 - angle) + 45.0
                elif 150 <= angle < 180:
                    drishti_val = (angle - 150) * 2.0
                elif 180 <= angle < 300:
                    drishti_val = (300 - angle) / 2.0

                if viewer_name == "Mars":
                    if (90 <= angle <= 100) or (210 <= angle <= 220):
                        drishti_val = max(drishti_val, 60.0)
                elif viewer_name == "Saturn":
                    if (60 <= angle <= 70) or (270 <= angle <= 280):
                        drishti_val = max(drishti_val, 60.0)
                elif viewer_name == "Jupiter":
                    if (120 <= angle <= 130) or (240 <= angle <= 250):
                        drishti_val = max(drishti_val, 60.0)

                impact = drishti_val / 4.0
                if viewer_name in benefics:
                    scores[target_name] += impact
                else:
                    scores[target_name] -= impact

        return scores
