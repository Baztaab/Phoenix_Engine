import math
from typing import Dict, List, Any


class ShadbalaEngine:
    """
    Advanced Shadbala engine (sixfold planetary strength).
    Components: Sthana, Dig, Kaala, Chesta, Naisargika, Drik.
    """

    NAISARGIKA_BALA = {
        "Sun": 60.0,
        "Moon": 51.43,
        "Mars": 17.14,
        "Mercury": 25.71,
        "Jupiter": 34.28,
        "Venus": 42.86,
        "Saturn": 8.57,
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

    def __init__(self, config: Any = None):
        self.config = config

    def calculate_shadbala(self, planets: Dict, asc_lon: float, is_day_birth: bool) -> Dict[str, Any]:
        report = {}

        sthana = self._calc_sthana_bala(planets, asc_lon)
        dig = self._calc_dig_bala(planets, asc_lon)
        kaala = self._calc_kaala_bala(planets, is_day_birth)
        chesta = self._calc_chesta_bala(planets)
        naisargika = self.NAISARGIKA_BALA
        drik = self._calc_drik_bala(planets)

        for p in self.NAISARGIKA_BALA.keys():
            if p not in planets:
                continue

            total_score = (
                sthana.get(p, 0)
                + dig.get(p, 0)
                + kaala.get(p, 0)
                + chesta.get(p, 0)
                + naisargika.get(p, 0)
                + drik.get(p, 0)
            )

            rupas = round(total_score / 60.0, 2)

            required = 5.0
            if p in ["Mercury", "Jupiter"]:
                required = 7.0
            elif p == "Moon":
                required = 6.0
            elif p in ["Sun", "Venus"]:
                required = 5.5

            ratio = round(rupas / required, 2)
            strength_label = "Strong" if ratio >= 1.0 else "Weak"

            report[p] = {
                "total_shastiamsas": round(total_score, 1),
                "rupas": rupas,
                "strength_ratio": ratio,
                "status": strength_label,
                "breakdown": {
                    "sthana": round(sthana.get(p, 0), 1),
                    "dig": round(dig.get(p, 0), 1),
                    "kaala": round(kaala.get(p, 0), 1),
                    "chesta": round(chesta.get(p, 0), 1),
                    "naisargika": round(naisargika.get(p, 0), 1),
                    "drik": round(drik.get(p, 0), 1),
                },
            }
        return report

    def _calc_sthana_bala(self, planets: Dict, asc_lon: float) -> Dict[str, float]:
        scores = {p: 0.0 for p in self.NAISARGIKA_BALA}
        for p_name, p_data in planets.items():
            if p_name not in scores:
                continue
            lon = p_data["longitude"]

            exalt = self.EXALTATION_POINTS[p_name]
            diff = abs(lon - exalt)
            if diff > 180:
                diff = 360 - diff
            scores[p_name] += (180 - diff) / 3.0

            house_idx = int((lon - asc_lon + 360) % 360 / 30) + 1
            if house_idx in [1, 4, 7, 10]:
                scores[p_name] += 60.0
            elif house_idx in [2, 5, 8, 11]:
                scores[p_name] += 30.0
            else:
                scores[p_name] += 15.0

            deg_in_sign = lon % 30
            decan = int(deg_in_sign / 10) + 1
            if p_name in ["Sun", "Mars", "Jupiter"] and decan == 1:
                scores[p_name] += 15.0
            elif p_name in ["Saturn", "Mercury"] and decan == 2:
                scores[p_name] += 15.0
            elif p_name in ["Venus", "Moon"] and decan == 3:
                scores[p_name] += 15.0

            sign_id = int(lon / 30) + 1
            is_even = sign_id % 2 == 0
            if p_name in ["Moon", "Venus"] and is_even:
                scores[p_name] += 15.0
            elif p_name not in ["Moon", "Venus"] and not is_even:
                scores[p_name] += 15.0
        return scores

    def _calc_dig_bala(self, planets: Dict, asc_lon: float) -> Dict[str, float]:
        scores = {}
        offsets = {"Mercury": 0, "Jupiter": 0, "Sun": 270, "Mars": 270, "Saturn": 180, "Venus": 90, "Moon": 90}
        for p_name, p_data in planets.items():
            if p_name not in offsets:
                continue
            target_angle = (asc_lon + offsets[p_name]) % 360
            diff = abs(p_data["longitude"] - target_angle)
            if diff > 180:
                diff = 360 - diff
            scores[p_name] = round((180 - diff) / 3.0, 2)
        return scores

    def _calc_chesta_bala(self, planets: Dict) -> Dict[str, float]:
        scores = {}
        for p_name, p_data in planets.items():
            if p_name in ["Sun", "Moon"]:
                scores[p_name] = 30.0
                continue
            speed = p_data.get("speed", 0)
            if p_data.get("is_retrograde", False):
                scores[p_name] = 60.0
            elif speed < 0.05:
                scores[p_name] = 15.0
            elif speed > 1.0:
                scores[p_name] = 45.0
            else:
                scores[p_name] = 30.0
        return scores

    def _calc_kaala_bala(self, planets: Dict, is_day: bool) -> Dict[str, float]:
        scores = {p: 0.0 for p in self.NAISARGIKA_BALA}
        for p in scores:
            if p == "Mercury":
                scores[p] += 60.0
            elif p in ["Sun", "Jupiter", "Venus"]:
                scores[p] += 60.0 if is_day else 0.0
            else:
                scores[p] += 0.0 if is_day else 60.0
            scores[p] += 30.0  # Placeholder
        return scores

    def _calc_drik_bala(self, planets: Dict) -> Dict[str, float]:
        scores = {p: 0.0 for p in self.NAISARGIKA_BALA}
        benefics = ["Jupiter", "Venus", "Moon", "Mercury"]
        planet_list = [k for k in planets.keys() if k in self.NAISARGIKA_BALA]
        for observer in planet_list:
            obs_lon = planets[observer]["longitude"]
            for target in planet_list:
                if observer == target:
                    continue
                angle = (planets[target]["longitude"] - obs_lon + 360) % 360
                strength = 0.0
                if 120 < angle < 240:
                    if abs(180 - angle) < 60:
                        strength = 60 - abs(180 - angle)
                if observer == "Mars":
                    if 90 <= angle <= 120:
                        strength = max(strength, 45)
                    if 210 <= angle <= 240:
                        strength = max(strength, 45)
                if observer == "Saturn":
                    if 60 <= angle <= 90:
                        strength = max(strength, 45)
                    if 270 <= angle <= 300:
                        strength = max(strength, 45)
                if observer == "Jupiter":
                    if 120 <= angle <= 150:
                        strength = max(strength, 60)
                    if 240 <= angle <= 270:
                        strength = max(strength, 60)

                impact = strength / 4.0
                scores[target] += impact if observer in benefics else -impact
        return scores

