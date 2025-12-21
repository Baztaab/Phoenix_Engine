
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.yoga import YogaEngine
from phoenix_engine.vedic.calculations.ashtakavarga import AshtakavargaEngine

class PredictionPlugin(IChartPlugin):
    @property
    def name(self): return "Predictive Analytics"

    def execute(self, ctx):
        if ctx.config.output.include_yogas:
            yogas = YogaEngine.check_yogas(ctx.planets, ctx.ascendant)
            ctx.analysis['yogas'] = [f"{y['name']}: {y['description']}" for y in yogas]

        if ctx.config.output.include_ashtakavarga:
            sign_positions = {name: p.sign for name, p in ctx.planets.items()}
            sign_positions['Ascendant'] = int(ctx.ascendant / 30) + 1
            ctx.analysis['ashtakavarga'] = AshtakavargaEngine.calculate_all(sign_positions)
