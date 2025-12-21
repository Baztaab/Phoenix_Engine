
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.varga import VargaEngine
from phoenix_engine.domain.analysis import VargaInfo # Assuming model exists or dict

class VargaPlugin(IChartPlugin):
    @property
    def name(self): return "Shodashavarga"

    def execute(self, ctx):
        if not ctx.config.output.include_vargas: return
        
        # Prepare simple longitude dict needed by VargaEngine
        longitudes = {name: p.longitude for name, p in ctx.planets.items()}
        longitudes['Ascendant'] = ctx.ascendant
        
        raw_vargas = VargaEngine.compute_vargas(longitudes)
        ctx.analysis['vargas'] = raw_vargas # Store in context
