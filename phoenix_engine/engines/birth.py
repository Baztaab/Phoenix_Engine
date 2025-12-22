
from phoenix_engine.core.context import ChartContext
from phoenix_engine.core.factory import ChartFactory
from phoenix_engine.domain.input import BirthData
from phoenix_engine.domain.config import ChartConfig
from phoenix_engine.domain.output import ChartOutput
from phoenix_engine.infrastructure.time.manager import TimeEngine
from datetime import datetime

class BirthChartEngine:
    def __init__(self, dt_aware: datetime, lat: float, lon: float, config: ChartConfig = None):
        self.dt = dt_aware
        self.lat = lat
        self.lon = lon
        self.config = config if config else ChartConfig()
        
        # Prepare BirthData for Context
        self.birth_data = BirthData(
            year=dt_aware.year, month=dt_aware.month, day=dt_aware.day,
            hour=dt_aware.hour, minute=dt_aware.minute,
            lat=lat, lon=lon, timezone=str(dt_aware.tzinfo)
        )

    def process(self) -> ChartOutput:
        # 1. Initialize Context
        ctx = ChartContext(self.birth_data, self.config)
        
        # 2. Manual Astronomy Injection (Legacy bridge)
        # Since PlanetaryPositionsPlugin might mock data in current state, 
        # we calculate JD here to be safe or ensure plugin does it right.
        # For V13 Alpha, let's keep using TimeEngine here to seed the context.
        time_engine = TimeEngine()
        ctx.jd_ut = time_engine.get_julian_day(self.dt)
        
        # 3. Get Pipeline
        pipeline = ChartFactory.create_pipeline("BIRTH", self.config)
        
        # 4. Execute Pipeline
        for plugin in pipeline:
            # print(f"Running {plugin.name}...") 
            plugin.execute(ctx)
            
        # 5. Map Context Analysis to ChartOutput
        # This mapping converts the dynamic dict back to the strict Pydantic model
        analysis = ctx.analysis
        
        return ChartOutput(
            meta={
                "datetime": self.dt.isoformat(),
                "location": {"lat": self.lat, "lon": self.lon},
                "algorithm": "Phoenix V13 Cosmic (Plugin Architecture)"
            },
            ascendant=ctx.ascendant,
            ayanamsha=analysis.get('ayanamsha', 0.0), # Need to ensure astro plugin sets this
            houses=ctx.houses,
            planets=ctx.planets,
            
            vargas=analysis.get('vargas'),
            shadbala=analysis.get('shadbala'),
            ashtakavarga=analysis.get('ashtakavarga'),
            jaimini=analysis.get('jaimini'),
            yogas=analysis.get('yogas'),
            parasari_yogas=analysis.get('parasari_yogas'),
            panchanga=analysis.get('panchanga'),
            dashas=analysis.get('dashas'),
            current_dasha_chain=analysis.get('current_dasha_chain'),
            
            # Nested fields
            avasthas=analysis.get('avasthas'),
            bhava_bala=analysis.get('bhava_bala'),
            phala=analysis.get('phala'),
            
            # Dosha (Construct Model if needed, or pass dict if compatible)
            dosha=analysis.get('dosha')
        )
