
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.core.context import ChartContext

class KalaSarpaPlugin(IChartPlugin):
    @property
    def name(self):
        return "Kala Sarpa Analyzer"

    def execute(self, ctx: ChartContext):
        if not ctx.config.output.include_doshas:
            return

        rahu = ctx.planets.get("Rahu")
        ketu = ctx.planets.get("Ketu")
        if not rahu or not ketu: return
        
        # Simplified Logic for Demo
        # Real logic is in previous scripts, can be fully pasted here
        has_dosha = False 
        # (Assuming logic check passed...)
        
        result = {
            "has_dosha": has_dosha,
            "type": "None"
        }
        
        if "dosha" not in ctx.analysis: ctx.analysis["dosha"] = {}
        ctx.analysis["dosha"]["kala_sarpa"] = result
