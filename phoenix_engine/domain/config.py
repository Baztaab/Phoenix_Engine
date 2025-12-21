
from pydantic import BaseModel, Field
from typing import List, Optional
from .enums import AyanamsaSystem, HouseSystem, NodeType, DashaSystem

class OutputOptions(BaseModel):
    include_vargas: bool = True
    include_shadbala: bool = True
    include_ashtakavarga: bool = True
    include_yogas: bool = True
    include_jaimini: bool = True
    include_maitri: bool = True
    include_aspects: bool = True
    include_avasthas: bool = True
    include_bhavabala: bool = True
    include_phala: bool = True
    include_doshas: bool = True      # Added for Dosha Plugin
    include_semantics: bool = False

class ChartConfig(BaseModel):
    ayanamsa: AyanamsaSystem = AyanamsaSystem.LAHIRI
    house_system: HouseSystem = HouseSystem.PLACIDUS
    node_type: NodeType = NodeType.TRUE_NODE
    dashas: List[DashaSystem] = [DashaSystem.VIMSHOTTARI]
    output: OutputOptions = Field(default_factory=OutputOptions)
