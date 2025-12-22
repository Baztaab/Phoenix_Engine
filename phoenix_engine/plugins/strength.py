from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.strength import ShadbalaEngine


class StrengthPlugin(IChartPlugin):
    @property
    def name(self): return "Shadbala Strength Engine (Phase 6)"

    def execute(self, ctx):
        if 'shadbala' not in ctx.analysis:
            ctx.analysis['shadbala'] = {}
            
        shadbala_results = ShadbalaEngine.calculate(
            ctx.planets, 
            ctx.ascendant, 
            ctx.jd_ut, 
            ctx.input.lat,
            ctx.input.lon
        )
        
        ctx.analysis['shadbala'] = shadbala_results
        
        # Update Planets with Ishta/Kashta approximation based on total strength
        for p_name, p_data in ctx.planets.items():
            if p_name in shadbala_results:
                total = shadbala_results[p_name]["total_rupas"]
                ratio = total / 6.0
                ishta_val = min(60.0, ratio * 30.0)
                kashta_val = max(0.0, 60.0 - ishta_val)
                p_data.ishta = ishta_val
                p_data.kashta = kashta_val
