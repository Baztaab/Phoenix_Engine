from typing import Any, Dict, List, Optional, Union

from phoenix_engine.core.config import ChartConfig
from phoenix_engine.domain.celestial import PlanetPosition
from phoenix_engine.domain.input import BirthData


class ChartContext:
    """
    Kerykeion-inspired Context Model.
    This is the Single Source of Truth for the chart's state during the pipeline execution.
    It replaces the loose dictionary approach with a strong object model.
    """

    def __init__(self, birth_data: BirthData, config: ChartConfig):
        self._birth_data = birth_data
        self._config = config

        # Core Astronomical Data
        self.jd_ut: float = 0.0  # Julian Day in UT
        self.jd_et: float = 0.0  # Julian Day in Ephemeris Time
        self.ayanamsa_value: float = 0.0

        # Celestial Bodies & Houses
        # Mapped by ID and Name for O(1) access
        self._planets: Dict[str, PlanetPosition] = {}
        self._houses: Union[List[float], Dict[int, Any]] = []  # Cusp longitudes (1-12)
        self._ascendant: float = 0.0

        # Analysis Containers (Plugins will populate these)
        self.analysis: Dict[str, Any] = {}
        self.meta: Dict[str, Any] = {}

    @property
    def birth_data(self) -> BirthData:
        return self._birth_data

    @property
    def input(self) -> BirthData:
        """Alias retained for backward compatibility with existing plugins."""
        return self._birth_data

    @input.setter
    def input(self, birth_data: BirthData):
        self._birth_data = birth_data

    @property
    def config(self) -> ChartConfig:
        return self._config

    @property
    def planets(self) -> Dict[str, PlanetPosition]:
        return self._planets

    @planets.setter
    def planets(self, planets: Dict[str, PlanetPosition]):
        self._planets = planets or {}

    @property
    def houses(self) -> Union[List[float], Dict[int, Any]]:
        return self._houses

    @houses.setter
    def houses(self, cusps: Union[List[float], Dict[int, Any]]):
        self._houses = cusps or []

    @property
    def ascendant(self) -> float:
        return self._ascendant

    @ascendant.setter
    def ascendant(self, ascendant: float):
        self._ascendant = ascendant

    def set_planets(self, planets: Union[List[PlanetPosition], Dict[str, PlanetPosition]]):
        """Populates the planet registry from a list or dict of calculated positions."""
        if isinstance(planets, dict):
            self._planets = planets
            return
        self._planets = {p.name: p for p in planets}

    def set_houses(self, cusps: List[float], ascendant: float):
        """Sets house cusps and ascendant."""
        self._houses = cusps
        self._ascendant = ascendant

    def get_planet(self, name: str) -> Optional[PlanetPosition]:
        """Direct access to a planet object by name (e.g., 'Sun', 'Jupiter')."""
        return self._planets.get(name)

    def get_planet_longitude(self, name: str) -> float:
        """Helper to get longitude directly, returns 0.0 if not found (fail-safe)."""
        planet = self.get_planet(name)
        return planet.longitude if planet else 0.0

    def get_house_cusp(self, house_num: int) -> float:
        """Get cusp longitude for house 1-12."""
        if 1 <= house_num <= 12:
            if isinstance(self._houses, dict):
                cusp = self._houses.get(house_num)
                if isinstance(cusp, dict):
                    return float(cusp.get("longitude", 0.0))
                if cusp is not None:
                    try:
                        return float(cusp)
                    except (TypeError, ValueError):
                        return 0.0
            elif len(self._houses) >= house_num:
                return float(self._houses[house_num - 1])
        return 0.0
