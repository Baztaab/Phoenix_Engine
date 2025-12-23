from typing import Dict, List, Any, Tuple

from phoenix_engine.vedic.const import SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN


class TajakaYogaEngine:
    """
    Tajaka (Varshaphal) specific yogas: Ithasala, Easarpha, Nakta, Yamaya, Manahoo, Kamboola.
    """

    # Deepthaamsa (orbs) for each planet
    DEEPTHAAMSA = {
        "Sun": 15.0,
        "Moon": 12.0,
        "Mars": 8.0,
        "Mercury": 7.0,
        "Jupiter": 9.0,
        "Venus": 7.0,
        "Saturn": 9.0,
    }

    # Aspect nature mapping (house distance)
    ASPECT_NATURE = {
        1: "Conjunction",
        2: "Neutral",
        3: "Benefic",
        4: "Malefic",
        5: "Benefic",
        6: "Neutral",
        7: "Malefic",
    }

    @staticmethod
    def _get_aspect_type(p1_sign: int, p2_sign: int) -> str:
        """Determine aspect nature based on sign distance."""
        diff = (p2_sign - p1_sign + 12) % 12
        house_dist = diff + 1

        if house_dist == 1:
            return "Conjunction"
        if house_dist in (3, 11):
            return "Benefic"  # Sextile
        if house_dist in (5, 9):
            return "Benefic"  # Trine
        if house_dist in (4, 10):
            return "Malefic"  # Square
        if house_dist == 7:
            return "Malefic"  # Opposition
        return "Neutral"

    @staticmethod
    def _is_within_orb(p1_deg: float, p2_deg: float, p1_name: str, p2_name: str) -> bool:
        """Check if planets are within combined orb."""
        orb1 = TajakaYogaEngine.DEEPTHAAMSA.get(p1_name, 0.0)
        orb2 = TajakaYogaEngine.DEEPTHAAMSA.get(p2_name, 0.0)
        mean_orb = (orb1 + orb2) / 2.0
        diff = abs(p1_deg - p2_deg)
        return diff <= mean_orb

    @staticmethod
    def _check_ithasala(p1: Dict, p2: Dict) -> Tuple[bool, str]:
        """
        Ithasala (Muthashila): aspect + within orb + faster planet is applying.
        Returns (is_ithasala, qualifier|\"Easarpha\").
        """
        name1, name2 = p1["name"], p2["name"]
        if name1 not in TajakaYogaEngine.DEEPTHAAMSA or name2 not in TajakaYogaEngine.DEEPTHAAMSA:
            return False, ""

        aspect_type = TajakaYogaEngine._get_aspect_type(p1["sign"], p2["sign"])
        if aspect_type == "Neutral":
            return False, ""

        if not TajakaYogaEngine._is_within_orb(p1["degree"], p2["degree"], name1, name2):
            return False, ""

        # Determine faster/slower
        faster = p1 if abs(p1["speed"]) > abs(p2["speed"]) else p2
        slower = p2 if faster is p1 else p1

        is_approaching = False
        if not faster["is_retro"] and not slower["is_retro"]:
            if faster["degree"] < slower["degree"]:
                is_approaching = True
        elif faster["is_retro"] and not slower["is_retro"]:
            if faster["degree"] > slower["degree"]:
                is_approaching = True

        if is_approaching:
            quality = "Vartamana"
            if abs(faster["degree"] - slower["degree"]) < 1.0:
                quality = "Poorna"
            return True, quality

        return False, "Easarpha"

    @staticmethod
    def calculate_yogas(planets: Dict[str, Any]) -> List[Dict]:
        """
        Compute Tajaka yogas for a given moment.
        planets: dict of {name: {name, sign, degree, speed, is_retro}}
        """
        yogas: List[Dict[str, Any]] = []
        planet_list = [p for _, p in planets.items() if p["name"] in TajakaYogaEngine.DEEPTHAAMSA]

        ithasala_pairs = []
        for i in range(len(planet_list)):
            for j in range(i + 1, len(planet_list)):
                p1, p2 = planet_list[i], planet_list[j]
                is_itha, q = TajakaYogaEngine._check_ithasala(p1, p2)
                if is_itha:
                    aspect_nature = TajakaYogaEngine._get_aspect_type(p1["sign"], p2["sign"])
                    yogas.append(
                        {
                            "name": "Ithasala Yoga",
                            "actors": [p1["name"], p2["name"]],
                            "description": f"{q} Ithasala between {p1['name']} and {p2['name']} ({aspect_nature})",
                            "nature": aspect_nature,
                        }
                    )
                    ithasala_pairs.append((p1["name"], p2["name"]))
                elif q == "Easarpha":
                    yogas.append(
                        {
                            "name": "Easarpha Yoga",
                            "actors": [p1["name"], p2["name"]],
                            "description": f"Separating aspect between {p1['name']} and {p2['name']}",
                            "nature": "Separative",
                        }
                    )

        # Kamboola Yoga (Moon intervenes with an Ithasala)
        if "Moon" in planets:
            for p1_name, p2_name in ithasala_pairs:
                moon = planets["Moon"]
                p1 = planets[p1_name]
                is_itha_moon, _ = TajakaYogaEngine._check_ithasala(moon, p1)
                if is_itha_moon:
                    yogas.append(
                        {
                            "name": "Kamboola Yoga",
                            "actors": ["Moon", p1_name, p2_name],
                            "description": f"Moon transfers power to {p1_name} involved in Ithasala",
                            "nature": "Powerful",
                        }
                    )

        return yogas

