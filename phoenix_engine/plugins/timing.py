
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.dasha import DashaEngine
from phoenix_engine.vedic.calculations.panchanga import PanchangaEngine
from datetime import datetime

class TimingPlugin(IChartPlugin):
    @property
    def name(self): return "Timing Systems"

    def execute(self, ctx):
        # Panchanga
        sun = ctx.planets['Sun'].longitude
        moon = ctx.planets['Moon'].longitude
        ctx.analysis['panchanga'] = {
            "tithi": PanchangaEngine.calculate_tithi(sun, moon),
            "nakshatra": PanchangaEngine.calculate_nakshatra(moon),
            "yoga": PanchangaEngine.calculate_yoga(sun, moon),
            # Vara requires JD which context has
            "vara": PanchangaEngine.calculate_vara(ctx.jd_ut)
        }

        # Dashas (Vimshottari)
        # We need the datetime object from context input
        bd = ctx.input # BirthData
        dt = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute) # Naive is ok for logic
        
        nested = DashaEngine.calculate_vimshottari_nested(moon, dt)
        ctx.analysis['dashas'] = {"vimshottari": nested}
        ctx.analysis['current_dasha_chain'] = DashaEngine.get_current_chain(nested, datetime.now())
