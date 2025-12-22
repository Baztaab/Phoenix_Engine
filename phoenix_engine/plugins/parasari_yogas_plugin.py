from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.yogas.parasari_yogas import ParasariYogaEngine


class ParasariYogasPlugin(IChartPlugin):
    @property
    def name(self): return "Parasari Raja Yogas (Phase 5.5)"

    def execute(self, ctx):
        if 'yogas' not in ctx.analysis:
            ctx.analysis['yogas'] = []
            
        asc_sign = int(ctx.ascendant / 30) + 1
        
        parasari_list = ParasariYogaEngine.calculate_yogas(asc_sign, ctx.planets)
        
        ctx.analysis['parasari_yogas'] = parasari_list
