
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.dasha import DashaEngine
from phoenix_engine.vedic.calculations.panchanga import PanchangaEngine
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from datetime import datetime

class TimingPlugin(IChartPlugin):
    @property
    def name(self): return "Timing Systems"

    def execute(self, ctx):
        # Panchanga (only compute if not already provided by SubtleBodies)
        sun = ctx.planets['Sun'].longitude
        moon = ctx.planets['Moon'].longitude
        if 'panchanga' not in ctx.analysis:
            swe = SwissEphemeris()
            sunrise_jd, _ = swe.get_rise_set(ctx.jd_ut, ctx.input.lat, ctx.input.lon)
            ctx.analysis['panchanga'] = PanchangaEngine.calculate_panchanga(
                ctx.jd_ut, sun, moon, sunrise_jd
            )

        # Dashas (Vimshottari)
        # We need the datetime object from context input
        bd = ctx.input # BirthData
        dt = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute) # Naive is ok for logic
        
        nested = DashaEngine.calculate_vimshottari_nested(moon, dt)
        ctx.analysis['dashas'] = {"vimshottari": nested}
        ctx.analysis['current_dasha_chain'] = DashaEngine.get_current_chain(nested, datetime.now())
