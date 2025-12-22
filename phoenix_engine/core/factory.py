
from typing import List
from phoenix_engine.domain.config import ChartConfig
from phoenix_engine.plugins.base import IChartPlugin

# Import ALL Plugins
from phoenix_engine.plugins.astronomy.positions import PlanetaryPositionsPlugin
from phoenix_engine.plugins.vargas import VargaPlugin
from phoenix_engine.plugins.strength import StrengthPlugin
from phoenix_engine.plugins.prediction import PredictionPlugin
from phoenix_engine.plugins.timing import TimingPlugin
from phoenix_engine.plugins.jaimini import JaiminiPlugin
from phoenix_engine.plugins.doshas.kuja import KujaDoshaPlugin
from phoenix_engine.plugins.doshas.sarpa import KalaSarpaPlugin
from phoenix_engine.plugins.subtle import SubtleBodiesPlugin
from phoenix_engine.plugins.advanced_dashas import AdvancedDashasPlugin
# Note: Matching plugins are called separately in MatchEngine

class ChartFactory:
    "مغز متفکر خط تولید"
    
    @staticmethod
    def create_pipeline(chart_type: str, config: ChartConfig) -> List[IChartPlugin]:
        pipeline = []
        
        if chart_type == "BIRTH":
            # 1. Base Astronomy (Always First)
            pipeline.append(PlanetaryPositionsPlugin())
            pipeline.append(SubtleBodiesPlugin())
            
            # 2. Core Vedic Calculations
            pipeline.append(VargaPlugin())
            pipeline.append(StrengthPlugin())
            pipeline.append(PredictionPlugin())
            pipeline.append(TimingPlugin())
            pipeline.append(JaiminiPlugin())
            pipeline.append(AdvancedDashasPlugin())
            
            # 3. Optional Features
            if config.output.include_doshas:
                pipeline.append(KujaDoshaPlugin())
                pipeline.append(KalaSarpaPlugin())
                
        return pipeline
