
from pydantic import BaseModel

class PlanetPosition(BaseModel):
    id: int
    name: str
    longitude: float
    speed: float
    is_retrograde: bool
    sign: int
    sign_name: str
    degree: float
    house: int
    nakshatra: str
    nakshatra_pada: int

class AspectInfo(BaseModel):
    aspecting_planet: str
    aspected_planet: str
    angle: float
    is_special: bool
    orb: float
