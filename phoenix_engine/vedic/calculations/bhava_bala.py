from typing import Dict, List, Any

from phoenix_engine.core.context import ChartContext


class BhavaBalaEngine:
    """
    Advanced Bhava Bala Engine (House Strength).
    Components:
    1. Bhavadipati Bala (Lord Strength from Shadbala).
    2. Bhava Digbala (Directional Strength based on Sign Types).
    3. Bhava Drishti (Aspect Strength on the Cusp).
    """

    SIGN_TYPES = {
        1: "Chatushpada", 2: "Chatushpada", 5: "Chatushpada", 9: "Chatushpada",
        3: "Nara", 6: "Nara", 7: "Nara", 11: "Nara",
        4: "Jalachara", 12: "Jalachara", 10: "Jalachara",
        8: "Keeta"
    }

    RULERS = {
        1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon",
        5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars",
        9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
    }

    @staticmethod
    def calculate_all(ctx: ChartContext) -> Dict[int, Any]:
        results = {}
        houses = ctx.houses
        planets = ctx.planets
        shadbala = ctx.analysis.get("shadbala", {})

        for h_idx, cusp_lon in enumerate(houses):
            h_num = h_idx + 1
            sign = int(cusp_lon / 30) + 1

            lord_name = BhavaBalaEngine.RULERS.get(sign)
            lord_score = 0.0
            if shadbala and lord_name in shadbala:
                lord_score = shadbala[lord_name].get("rupas", 0.0) * 60.0

            digbala = BhavaBalaEngine._calc_digbala(h_num, sign)
            drishti_score = BhavaBalaEngine._calc_house_aspects(cusp_lon, planets)

            total_score = lord_score + digbala + drishti_score

            results[h_num] = {
                "total": round(total_score, 1),
                "lord_strength": round(lord_score, 1),
                "digbala": digbala,
                "drishti": round(drishti_score, 1),
                "rating": "Strong" if total_score > 450 else "Average"
            }

        return results

    @staticmethod
    def _calc_digbala(house_num: int, sign: int) -> float:
        s_type = BhavaBalaEngine.SIGN_TYPES.get(sign, "Nara")
        score = 0.0

        if s_type == "Nara":
            if house_num == 1:
                score = 60.0
            elif house_num == 7:
                score = 0.0
            else:
                score = 30.0

        elif s_type == "Jalachara":
            if house_num == 4:
                score = 60.0
            elif house_num == 10:
                score = 0.0
            else:
                score = 30.0

        elif s_type == "Chatushpada":
            if house_num == 10:
                score = 60.0
            elif house_num == 4:
                score = 0.0
            else:
                score = 30.0

        elif s_type == "Keeta":
            if house_num == 7:
                score = 60.0
            elif house_num == 1:
                score = 0.0
            else:
                score = 30.0

        return score

    @staticmethod
    def _calc_house_aspects(cusp_lon: float, planets: Dict[str, Any]) -> float:
        score = 0.0
        BENEFICS = ["Jupiter", "Venus", "Mercury", "Moon"]

        for name, p in planets.items():
            if name in ["Rahu", "Ketu", "Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue

            angle = (cusp_lon - p.longitude) % 360

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

            if name == "Mars" and ((90 <= angle <= 100) or (210 <= angle <= 220)):
                drishti_val = 60.0
            if name == "Saturn" and ((60 <= angle <= 70) or (270 <= angle <= 280)):
                drishti_val = 60.0
            if name == "Jupiter" and ((120 <= angle <= 130) or (240 <= angle <= 250)):
                drishti_val = 60.0

            effect = drishti_val * 0.25

            if name in BENEFICS:
                score += effect
            else:
                score -= effect

        return score
