
from pydantic import BaseModel
from typing import Dict, Any, List
from .input import BirthData

class MatchRequest(BaseModel):
    p1: BirthData # Person 1 (Boy)
    p2: BirthData # Person 2 (Girl)

class KutaScore(BaseModel):
    name: str
    score: float
    max_score: float
    description: str

class MatchResult(BaseModel):
    total_score: float
    max_total: float = 36.0
    kutas: List[KutaScore]
    is_recommended: bool
    meta: Dict[str, Any]
