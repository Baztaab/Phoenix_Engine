
from pydantic import BaseModel, Field
from typing import Optional
from .config import ChartConfig

class BirthData(BaseModel):
    year: int = Field(..., ge=1000, le=3000)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    timezone: str = Field(..., description="IANA Timezone string (e.g., Asia/Tehran, UTC)")
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

class ChartRequest(BaseModel):
    birth_data: BirthData
    config: Optional[ChartConfig] = Field(default_factory=ChartConfig)
    name: Optional[str] = "User"
    chart_type: str = "BIRTH" # Future: ANNUAL, PRASHNA, MATCHING
