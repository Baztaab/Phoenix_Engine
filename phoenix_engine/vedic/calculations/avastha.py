from typing import Dict, Any

from phoenix_engine.core.context import ChartContext
from phoenix_engine.domain.celestial import PlanetPosition


class AvasthaEngine:
    """
    Advanced Avastha Engine (JHora/BPHS Standard).
    Calculates:
    1. Baladi (Age): Infant, Young, etc.
    2. Jagradadi (Consciousness): Awake, Dreaming, Sleep.
    3. Lajjitaadi (Mood/State): The most critical predictive avasthas (Shamed, Proud, Starved, etc.).
    """

    @staticmethod
    def calculate_avasthas(ctx: ChartContext) -> Dict[str, Dict[str, Any]]:
        results = {}
        planets = ctx.planets

        for name, p in planets.items():
            if name in ["Rahu", "Ketu", "Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue

            baladi = AvasthaEngine._calc_baladi(p.degree, p.sign)
            jagradadi = AvasthaEngine._calc_jagradadi(p)
            lajjitaadi = AvasthaEngine._calc_lajjitaadi(p, planets)

            results[name] = {
                "baladi": baladi,
                "jagradadi": jagradadi,
                "lajjitaadi": lajjitaadi,
                "summary": f"{baladi} | {jagradadi}"
            }

        return results

    @staticmethod
    def _calc_baladi(degree: float, sign: int) -> str:
        is_odd = (sign % 2 != 0)

        if 0 <= degree < 6:
            return "Bala (Infant)" if is_odd else "Mrit (Dead)"
        elif 6 <= degree < 12:
            return "Kumara (Young)" if is_odd else "Vriddha (Old)"
        elif 12 <= degree < 18:
            return "Yuva (Adult)"
        elif 18 <= degree < 24:
            return "Vriddha (Old)" if is_odd else "Kumara (Young)"
        else:
            return "Mrit (Dead)" if is_odd else "Bala (Infant)"

    @staticmethod
    def _calc_jagradadi(p: PlanetPosition) -> str:
        if p.is_retrograde:
            return "Jagrat (Awake)"
        return "Swapna (Dreaming)"

    @staticmethod
    def _calc_lajjitaadi(p: PlanetPosition, all_planets: Dict[str, PlanetPosition]) -> Dict[str, bool]:
        states = {
            "Lajjita (Shamed)": False,
            "Garvita (Proud)": False,
            "Kshudhita (Starved)": False,
            "Trishita (Thirsty)": False,
            "Mudita (Delighted)": False,
            "Kshobhita (Agitated)": False
        }

        is_joined_sun = False
        is_joined_saturn = False
        is_joined_mars = False
        is_joined_rahu_ketu = False

        for other_name, other_p in all_planets.items():
            if other_name == p.name:
                continue
            if other_p.sign == p.sign:
                if other_name == "Sun":
                    is_joined_sun = True
                if other_name == "Saturn":
                    is_joined_saturn = True
                if other_name == "Mars":
                    is_joined_mars = True
                if other_name in ["Rahu", "Ketu"]:
                    is_joined_rahu_ketu = True

        if p.house == 5 and (is_joined_rahu_ketu or is_joined_sun or is_joined_saturn or is_joined_mars):
            states["Lajjita (Shamed)"] = True

        exalt_map = {"Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6, "Jupiter": 4, "Venus": 12, "Saturn": 7}
        if p.sign == exalt_map.get(p.name):
            states["Garvita (Proud)"] = True

        if p.name != "Saturn" and is_joined_saturn:
            states["Kshudhita (Starved)"] = True

        watery_signs = [4, 8, 12]
        if p.sign in watery_signs and (is_joined_sun or is_joined_saturn or is_joined_mars):
            states["Trishita (Thirsty)"] = True

        joined_jupiter = any(k == "Jupiter" and v.sign == p.sign for k, v in all_planets.items())
        if joined_jupiter and p.name != "Jupiter":
            states["Mudita (Delighted)"] = True

        if is_joined_sun and (is_joined_mars or is_joined_saturn):
            states["Kshobhita (Agitated)"] = True

        return {k: v for k, v in states.items() if v}
