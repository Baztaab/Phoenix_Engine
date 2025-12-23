from typing import Dict, Any

import math

from phoenix_engine.vedic.calculations.tajaka.tajaka_calc import TajakaCalculator
from phoenix_engine.vedic.calculations.tajaka.tajaka_yogas import TajakaYogaEngine


class TajakaEngine:
    """
    Comprehensive Varshaphal (Tajaka) engine with Pancha Vargeeya Bala (PVB) logic.
    Inspired by JHora workflows.
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

    PLANET_LORDS = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",
        "Pisces": "Jupiter",
    }

    SIGN_TO_ID = {
        "Aries": 1,
        "Taurus": 2,
        "Gemini": 3,
        "Cancer": 4,
        "Leo": 5,
        "Virgo": 6,
        "Libra": 7,
        "Scorpio": 8,
        "Sagittarius": 9,
        "Capricorn": 10,
        "Aquarius": 11,
        "Pisces": 12,
    }

    TRI_RASI_LORDS = {
        1: ["Sun", "Jupiter"],
        2: ["Venus", "Moon"],
        3: ["Saturn", "Mercury"],
        4: ["Venus", "Mars"],
        5: ["Jupiter", "Sun"],
        6: ["Moon", "Venus"],
        7: ["Mercury", "Saturn"],
        8: ["Mars", "Venus"],
        9: ["Saturn", "Saturn"],
        10: ["Mars", "Mars"],
        11: ["Jupiter", "Jupiter"],
        12: ["Venus", "Moon"],
    }

    EXALTATION_POINTS = {
        "Sun": 10,
        "Moon": 33,
        "Mars": 298,
        "Mercury": 165,
        "Jupiter": 95,
        "Venus": 357,
        "Saturn": 200,
    }

    # Hadda/Terms per sign: list of (upper degree limit, lord)
    HADDA_TABLE = {
        1: [(6, "Jupiter"), (12, "Venus"), (20, "Mercury"), (25, "Mars"), (30, "Saturn")],
        2: [(8, "Venus"), (14, "Mercury"), (22, "Jupiter"), (27, "Saturn"), (30, "Mars")],
        3: [(6, "Mercury"), (12, "Venus"), (17, "Jupiter"), (24, "Mars"), (30, "Saturn")],
        4: [(7, "Mars"), (13, "Venus"), (19, "Mercury"), (26, "Jupiter"), (30, "Saturn")],
        5: [(6, "Jupiter"), (11, "Venus"), (18, "Saturn"), (24, "Mercury"), (30, "Mars")],
        6: [(7, "Mercury"), (17, "Venus"), (21, "Jupiter"), (28, "Mars"), (30, "Saturn")],
        7: [(6, "Saturn"), (14, "Mercury"), (21, "Jupiter"), (28, "Venus"), (30, "Mars")],
        8: [(7, "Mars"), (11, "Venus"), (19, "Mercury"), (24, "Jupiter"), (30, "Saturn")],
        9: [(12, "Jupiter"), (17, "Venus"), (21, "Mercury"), (26, "Saturn"), (30, "Mars")],
        10: [(7, "Mercury"), (14, "Jupiter"), (22, "Venus"), (26, "Saturn"), (30, "Mars")],
        11: [(7, "Venus"), (13, "Mercury"), (20, "Jupiter"), (25, "Mars"), (30, "Saturn")],
        12: [(12, "Venus"), (16, "Jupiter"), (19, "Mercury"), (28, "Mars"), (30, "Saturn")],
    }

    NATURAL_RELATIONSHIPS = {
        "Sun": {"Friends": ["Moon", "Mars", "Jupiter"], "Enemies": ["Venus", "Saturn"], "Neutral": ["Mercury"]},
        "Moon": {"Friends": ["Sun", "Mercury"], "Enemies": [], "Neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
        "Mars": {"Friends": ["Sun", "Moon", "Jupiter"], "Enemies": ["Mercury"], "Neutral": ["Venus", "Saturn"]},
        "Mercury": {"Friends": ["Sun", "Venus"], "Enemies": ["Moon"], "Neutral": ["Mars", "Jupiter", "Saturn"]},
        "Jupiter": {"Friends": ["Sun", "Moon", "Mars"], "Enemies": ["Mercury", "Venus"], "Neutral": ["Saturn"]},
        "Venus": {"Friends": ["Mercury", "Saturn"], "Enemies": ["Sun", "Moon"], "Neutral": ["Mars", "Jupiter"]},
        "Saturn": {"Friends": ["Mercury", "Venus"], "Enemies": ["Sun", "Moon", "Mars"], "Neutral": ["Jupiter"]},
    }

    def __init__(self, chart_factory):
        self.chart_factory = chart_factory

    # Utility to normalize planet data structures
    def _sign_name(self, sign_id: int) -> str:
        idx = (sign_id - 1) % 12
        return self.SIGN_NAMES[idx]

    def _planet_coords(self, varsha_chart: Dict, planet: str) -> Dict[str, Any]:
        pdata = varsha_chart["planets"][planet]
        coords = pdata.get("coordinates", {})
        lon = coords.get("longitude", pdata.get("longitude", 0.0))
        deg = coords.get("degree_in_sign", pdata.get("degree", lon % 30.0))
        sign_id = coords.get("sign_id", pdata.get("sign_id", int(lon / 30) + 1))
        return {
            "lon": lon,
            "deg": deg,
            "sign_id": sign_id,
            "sign_name": pdata.get("sign_name", self._sign_name(sign_id)),
            "speed": pdata.get("speed", coords.get("speed", 0.0)),
            "retro": pdata.get("is_retrograde", pdata.get("is_retro", coords.get("is_retro", False))),
        }

    # ------------------------------------------------------------------ main
    def generate_annual_report(self, natal_data: Dict, target_year: int) -> Dict[str, Any]:
        """
        Generate full annual report with high-precision solar return and PVB-based Varsheshwara.
        Expects natal_data structured with meta/planets/houses similar to ChartOutput mapping.
        """
        birth_meta = natal_data.get("meta", {})
        birth_jd = birth_meta.get("jd", 0.0)
        birth_year = int(birth_meta.get("birth_date", "2000-01-01").split("-")[0])
        # Solar return
        return_jd, return_dt = TajakaCalculator.get_solar_return_time(
            birth_jd, target_year, birth_year
        )

        # Annual chart (Varsha Kundali) at birth location
        loc = birth_meta.get("location", {}) or {}
        varsha_chart = self.chart_factory.create_chart(
            dt=return_dt, lat=loc.get("lat", 0.0), lon=loc.get("lon", 0.0)
        )

        # Muntha
        birth_asc_sign = natal_data["ascendant"]["sign_id"]
        muntha_data = TajakaCalculator.calculate_muntha(birth_asc_sign, birth_year, target_year)

        # Candidates & Varsheshwara
        candidates = self._identify_candidates(natal_data, varsha_chart, muntha_data, return_dt)
        year_lord = self._select_year_lord_with_pvb(candidates, varsha_chart)

        # Yogas (normalize structure for yoga engine)
        yoga_planets = {}
        for name in varsha_chart["planets"]:
            c = self._planet_coords(varsha_chart, name)
            yoga_planets[name] = {
                "name": name,
                "sign": c["sign_id"],
                "degree": c["deg"],
                "speed": c["speed"],
                "is_retro": c["retro"],
            }
        yogas = TajakaYogaEngine.calculate_yogas(yoga_planets)

        return {
            "meta": {
                "type": "Tajaka Varshaphal (High Precision)",
                "target_year": target_year,
                "solar_return_jd": return_jd,
                "solar_return_moment": return_dt.isoformat(),
            },
            "varsheshwara": year_lord,
            "muntha": muntha_data,
            "candidates": candidates,
            "yogas": yogas,
            "chart_planets": varsha_chart["planets"],
        }

    # ------------------------------------------------------------------ helpers
    def _get_relationship(self, planet: str, host_planet: str, varsha_chart: Dict) -> str:
        """
        Compound relationship (Panchadha Maitri) for PVB.
        Friend/Neutral/Enemy based on natural + temporal relations.
        """
        if planet == host_planet:
            return "Own"

        # Natural
        nat_rel = "Neutral"
        if host_planet in self.NATURAL_RELATIONSHIPS[planet]["Friends"]:
            nat_rel = "Friend"
        elif host_planet in self.NATURAL_RELATIONSHIPS[planet]["Enemies"]:
            nat_rel = "Enemy"

        # Temporal: houses 2,3,4,10,11,12 from the planet are temporary friends
        p1_sign = self._planet_coords(varsha_chart, planet)["sign_id"]
        p2_sign = self._planet_coords(varsha_chart, host_planet)["sign_id"]
        dist = (p2_sign - p1_sign + 12) % 12 + 1
        temp_rel = "Friend" if dist in [2, 3, 4, 10, 11, 12] else "Enemy"

        score = 0
        if nat_rel == "Friend":
            score += 1
        elif nat_rel == "Enemy":
            score -= 1
        if temp_rel == "Friend":
            score += 1
        elif temp_rel == "Enemy":
            score -= 1

        if score >= 1:
            return "Friend"
        if score == 0:
            return "Neutral"
        return "Enemy"

    def _get_hadda_lord(self, sign_id: int, degree: float) -> str:
        terms = self.HADDA_TABLE.get(sign_id, [])
        for limit, lord in terms:
            if degree < limit:
                return lord
        return terms[-1][1] if terms else "Saturn"

    def _calculate_varga_sign(self, lon: float, division: int) -> int:
        """
        Compute sign placement in varga by math (D1/D3/D9 implemented).
        """
        sign_idx = int(lon / 30)
        deg_in_sign = lon % 30
        curr_sign = sign_idx + 1

        if division == 1:
            return curr_sign

        if division == 3:
            part = int(deg_in_sign / 10)  # 0,1,2
            if part == 0:
                return curr_sign
            if part == 1:
                return (curr_sign + 4 - 1) % 12 + 1
            if part == 2:
                return (curr_sign + 8 - 1) % 12 + 1

        if division == 9:
            part = int(deg_in_sign / (30 / 9))  # 0..8
            offsets = {1: 0, 5: 0, 9: 0, 2: 9, 6: 9, 10: 9, 3: 6, 7: 6, 11: 6, 4: 3, 8: 3, 12: 3}
            start_offset = offsets[curr_sign]
            return (start_offset + part) % 12 + 1

        return curr_sign

    def _calculate_pvb(self, planet: str, varsha_chart: Dict) -> float:
        """
        Pancha Vargeeya Bala calculation (simplified but close to JHora).
        """
        if planet in ["Rahu", "Ketu"]:
            return 0.0

        coords = self._planet_coords(varsha_chart, planet)
        lon = coords["lon"]
        deg = coords["deg"]
        sign = coords["sign_id"]

        # 1. Kshetra Bala (D1)
        lord_d1 = self.PLANET_LORDS[coords["sign_name"]]
        rel_d1 = self._get_relationship(planet, lord_d1, varsha_chart)
        kb = 15.0
        if planet == lord_d1:
            kb = 30.0
        elif rel_d1 == "Friend":
            kb = 22.5
        elif rel_d1 == "Enemy":
            kb = 7.5

        # 2. Uccha Bala
        exalt_point = self.EXALTATION_POINTS.get(planet, 0)
        diff = abs(lon - exalt_point)
        if diff > 180:
            diff = 360 - diff
        ub = (180 - diff) / 9.0  # 0..20

        # 3. Hadda Bala
        hadda_lord = self._get_hadda_lord(sign, deg)
        rel_hadda = self._get_relationship(planet, hadda_lord, varsha_chart)
        hb = 7.5
        if planet == hadda_lord:
            hb = 15.0
        elif rel_hadda == "Friend":
            hb = 7.5
        elif rel_hadda == "Enemy":
            hb = 3.75

        # 4. Drekkana Bala (D3)
        sign_d3 = self._calculate_varga_sign(lon, 3)
        lord_d3_name = [k for k, v in self.SIGN_TO_ID.items() if v == sign_d3][0]
        lord_d3 = self.PLANET_LORDS[lord_d3_name]
        rel_d3 = self._get_relationship(planet, lord_d3, varsha_chart)
        db = 5.0
        if planet == lord_d3:
            db = 10.0
        elif rel_d3 == "Friend":
            db = 5.0
        elif rel_d3 == "Enemy":
            db = 2.5

        # 5. Navamsa Bala (D9)
        sign_d9 = self._calculate_varga_sign(lon, 9)
        lord_d9_name = [k for k, v in self.SIGN_TO_ID.items() if v == sign_d9][0]
        lord_d9 = self.PLANET_LORDS[lord_d9_name]
        rel_d9 = self._get_relationship(planet, lord_d9, varsha_chart)
        nb = 2.5
        if planet == lord_d9:
            nb = 5.0
        elif rel_d9 == "Friend":
            nb = 2.5
        elif rel_d9 == "Enemy":
            nb = 1.25

        total_pvb = (kb + ub + hb + db + nb) / 4.0
        return round(total_pvb, 2)

    def _select_year_lord_with_pvb(self, candidates: Dict, varsha_chart: Dict) -> Dict:
        """
        Select Varsheshwara using PVB scoring and Tajaka aspect eligibility.
        """
        unique_candidates = list(set(candidates.values()))
        scored_candidates = []

        lagna_sign = varsha_chart["houses"][1]["sign_id"]

        for planet in unique_candidates:
            if planet not in varsha_chart["planets"]:
                continue

            coords = self._planet_coords(varsha_chart, planet)
            p_sign = coords["sign_id"]
            dist = (lagna_sign - p_sign + 12) % 12 + 1
            has_aspect = dist in [1, 3, 4, 5, 7, 9, 10, 11]
            is_muntha_lord = planet == candidates.get("Muntha_Lord")
            status = "Eligible" if (has_aspect or is_muntha_lord) else "Ineligible (No Aspect)"

            pvb_score = self._calculate_pvb(planet, varsha_chart)
            scored_candidates.append(
                {
                    "name": planet,
                    "pvb_score": pvb_score,
                    "status": status,
                    "roles": [r for r, p in candidates.items() if p == planet],
                }
            )

        eligible = [c for c in scored_candidates if c["status"] == "Eligible"]
        winner = max(eligible or scored_candidates, key=lambda x: x["pvb_score"])

        return {"winner": winner["name"], "score": winner["pvb_score"], "details": scored_candidates}

    def _identify_candidates(self, natal_chart: Dict, varsha_chart: Dict, muntha: Dict, return_dt: Any) -> Dict[str, str]:
        """
        Identify Pancha Adhikari candidates (Muntha lord, birth lagna lord, varsha lagna lord, tri-rasi lord, din/ratri lord).
        """
        candidates: Dict[str, str] = {}

        candidates["Muntha_Lord"] = self.PLANET_LORDS[muntha["sign_name"]]

        # Birth Lagna Lord
        bl_sign = natal_chart["houses"][1]["sign_name"]
        candidates["Birth_Lagna_Lord"] = self.PLANET_LORDS[bl_sign]

        # Varsha Lagna Lord
        vl_sign = varsha_chart["houses"][1]["sign_name"]
        candidates["Varsha_Lagna_Lord"] = self.PLANET_LORDS[vl_sign]

        # Tri-Rasi
        is_day = 6 <= return_dt.hour < 18
        vl_id = varsha_chart["houses"][1]["sign_id"]
        idx = 0 if is_day else 1
        candidates["Tri_Rasi_Lord"] = self.TRI_RASI_LORDS.get(vl_id, ["Saturn", "Saturn"])[idx]

        # Din-Ratri
        src = "Sun" if is_day else "Moon"
        sign_id = self._planet_coords(varsha_chart, src)["sign_id"]
        candidates["Din_Ratri_Lord"] = self.PLANET_LORDS[self._sign_name(sign_id)]

        return candidates
