from typing import List, Dict, Optional

from pydantic import BaseModel

from phoenix_engine.core.context import ChartContext
from phoenix_engine.domain.celestial import PlanetPosition


class YogaDefinition(BaseModel):
    name: str
    description: str
    benefits: str
    category: str  # 'Raja', 'Dhana', 'Nabhasa', 'Solar', 'Lunar'


class YogaResult(BaseModel):
    yoga: YogaDefinition
    planets_involved: List[str]
    strength_score: float = 0.0
    is_active: bool = True


class YogaUtils:
    """Shared utilities for Yoga calculations (Lordships, Aspects)"""

    RULERSHIP = {
        1: "Mars",
        2: "Venus",
        3: "Mercury",
        4: "Moon",
        5: "Sun",
        6: "Mercury",
        7: "Venus",
        8: "Mars",
        9: "Jupiter",
        10: "Saturn",
        11: "Saturn",
        12: "Jupiter",
    }

    @staticmethod
    def get_lord(sign: int) -> str:
        return YogaUtils.RULERSHIP.get(sign, "")

    @staticmethod
    def get_house_lord(ascendant_sign: int, house_num: int) -> str:
        sign_on_cusp = (ascendant_sign + house_num - 2) % 12 + 1
        return YogaUtils.get_lord(sign_on_cusp)

    @staticmethod
    def get_lords_of_houses(asc_sign: int, houses: List[int]) -> List[str]:
        return [YogaUtils.get_house_lord(asc_sign, h) for h in houses]

    @staticmethod
    def are_conjunct(p1: PlanetPosition, p2: PlanetPosition) -> bool:
        return p1.sign == p2.sign

    @staticmethod
    def has_aspect(p1: PlanetPosition, p2: PlanetPosition, planet_name: str) -> bool:
        dist = (p2.sign - p1.sign + 12) % 12
        if dist == 0:
            dist = 12

        aspects = [7]
        if planet_name == "Mars":
            aspects.extend([4, 8])
        elif planet_name == "Jupiter":
            aspects.extend([5, 9])
        elif planet_name == "Saturn":
            aspects.extend([3, 10])

        house_dist = (p2.sign - p1.sign) % 12 + 1
        return house_dist in aspects
