
# -------------------------------------------------------------------
# BRIDGING FILE
# This file imports from phoenix_engine.domain to maintain backward compatibility.
# -------------------------------------------------------------------

from phoenix_engine.domain.enums import AyanamsaSystem, HouseSystem, NodeType, DashaSystem
from phoenix_engine.domain.config import ChartConfig, OutputOptions
from phoenix_engine.domain.input import BirthData, ChartRequest
from phoenix_engine.domain.celestial import PlanetPosition, AspectInfo
from phoenix_engine.domain.timing import DashaPeriod, CharaDashaPeriod, CharaAntarDasha
from phoenix_engine.domain.analysis import ShadbalaInfo, JaiminiInfo, DoshaResult
from phoenix_engine.domain.output import ChartOutput, SemanticOutput
