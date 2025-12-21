
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.core.context import ChartContext
from phoenix_engine.domain.analysis import DoshaResult

class KujaDoshaPlugin(IChartPlugin):
    @property
    def name(self):
        return "Kuja Dosha Analyzer"

    def execute(self, ctx: ChartContext):
        if not ctx.config.output.include_doshas:
            return

        # Logic Copied & Adapted from Phase 1
        mars = ctx.planets.get("Mars")
        if not mars: return
        
        asc_sign = int(ctx.ascendant / 30) + 1
        mars_house = (mars.sign - asc_sign) % 12 + 1
        if mars_house <= 0: mars_house += 12
        
        # Houses: 1, 2, 4, 7, 8, 12
        is_manglik = mars_house in [1, 2, 4, 7, 8, 12]
        is_cancelled = False
        reasons = []

        # Simple Exception (Example)
        if mars.sign in [1, 8]: # Own sign
            is_cancelled = True
            reasons.append("Mars in Own Sign")
            
        result = {
            "is_manglik": is_manglik and not is_cancelled,
            "mars_house": mars_house,
            "is_cancelled": is_cancelled,
            "reason": ", ".join(reasons)
        }
        
        # Store in analysis bucket
        if "dosha" not in ctx.analysis: ctx.analysis["dosha"] = {}
        ctx.analysis["dosha"]["manglik"] = result
