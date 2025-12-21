
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

# --- Dasha Models ---
class DashaPeriod(BaseModel):
    # This structure might need to be more generic for JHora
    # But keeping V12.3 structure for now
    lord: str
    start: str
    end: str
    # duration_years: float (Optional)

class CharaAntarDasha(BaseModel):
    sign: int
    start: str
    end: str

class CharaDashaPeriod(BaseModel):
    sign: int
    lord_sign: int
    duration_years: int
    start: str
    end: str
    sub_periods: List[CharaAntarDasha]

# --- Panchanga Models ---
# Keeping generic Dict for now to avoid complexity, 
# but ideally should have explicit models like TithiInfo, etc.
