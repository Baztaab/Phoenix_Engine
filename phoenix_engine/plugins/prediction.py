
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.yoga import YogaEngine

class PredictionPlugin(IChartPlugin):
    @property
    def name(self): return "Predictive Analytics"

    def execute(self, ctx):
        if ctx.config.output.include_yogas:
            yogas = YogaEngine.check_yogas(ctx.planets, ctx.ascendant)
            ctx.analysis['yogas'] = [f"{y['name']}: {y['description']}" for y in yogas]
