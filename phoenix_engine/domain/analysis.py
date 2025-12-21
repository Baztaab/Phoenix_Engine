
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from .timing import CharaDashaPeriod

class ShadbalaInfo(BaseModel):
    total: float
    breakdown: Dict[str, float]
    is_strong: bool

class JaiminiInfo(BaseModel):
    karakas: Dict[str, str]
    padas: Dict[str, int]
    chara_dasha: List[CharaDashaPeriod]

class DoshaResult(BaseModel):
    manglik: Dict[str, Any]
    kala_sarpa: Dict[str, Any]

# Placeholder for others that are just Dicts currently:
# Varga, Ashtakavarga, Yoga, Maitri, Avastha, BhavaBala, Phala
# We will define them strictly in Phase 2.

# --- Defined Types (Aliases for now) ---
VargaInfo = Dict[str, Any]
AshtakavargaInfo = Dict[str, Any]
YogaInfo = List[str]
MaitriInfo = Dict[str, Any]
AvasthaInfo = Dict[str, Any]
BhavaBalaInfo = Dict[str, float]
PhalaInfo = Dict[str, Any]
