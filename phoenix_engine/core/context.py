
from typing import Dict, Any, List, Optional
from phoenix_engine.domain.celestial import PlanetPosition
from phoenix_engine.domain.config import ChartConfig
from phoenix_engine.domain.input import BirthData

class ChartContext:
    "ظرف هوشمندی که در طول پایپ‌لاین دست به دست می‌شود"
    def __init__(self, birth_data: BirthData, config: ChartConfig):
        self.input = birth_data
        self.config = config
        
        # State (Calculated Data)
        self.jd_ut: float = 0.0
        self.ascendant: float = 0.0
        self.houses: List[float] = []
        self.planets: Dict[str, PlanetPosition] = {}
        
        # Analysis Results (Populated by Plugins)
        # This allows dynamic extension: context.analysis['tajaka'] = ...
        self.analysis: Dict[str, Any] = {}
        self.payload: Dict[str, Any] = {} # Final JSON Output components
