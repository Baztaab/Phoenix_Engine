
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from .celestial import PlanetPosition, AspectInfo
from .analysis import ShadbalaInfo, JaiminiInfo, DoshaResult
from .enums import AyanamsaSystem, HouseSystem

class SemanticOutput(BaseModel):
    motif_tags: List[str]
    linguistic_facts: Dict[str, List[str]]

class ChartOutput(BaseModel):
    meta: Dict[str, Any]
    ascendant: float
    ayanamsha: float
    houses: List[float]
    planets: Dict[str, PlanetPosition]
    
    # Analysis Modules
    vargas: Optional[Dict[str, Any]] = None
    shadbala: Optional[Dict[str, ShadbalaInfo]] = None
    ashtakavarga: Optional[Dict[str, Any]] = None
    jaimini: Optional[JaiminiInfo] = None # Using model
    yogas: Optional[List[str]] = None
    
    # Timing
    panchanga: Optional[Dict[str, Any]] = None
    dashas: Optional[Dict[str, Any]] = None
    current_dasha_chain: Optional[List[Any]] = None
    
    # Extended Vedic
    maitri: Optional[Dict[str, Dict[str, str]]] = None
    aspects: Optional[List[AspectInfo]] = None
    avasthas: Optional[Dict[str, Dict[str, str]]] = None
    bhava_bala: Optional[Dict[int, float]] = None
    phala: Optional[Dict[str, Dict[str, float]]] = None
    
    # New Plugins
    dosha: Optional[DoshaResult] = None
    semantics: Optional[SemanticOutput] = None
