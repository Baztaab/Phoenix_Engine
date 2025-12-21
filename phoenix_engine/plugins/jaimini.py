
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.jaimini import JaiminiEngine
from datetime import datetime

class JaiminiPlugin(IChartPlugin):
    @property
    def name(self): return "Jaimini Sutras"

    def execute(self, ctx):
        if not ctx.config.output.include_jaimini: return
        
        asc_sign = int(ctx.ascendant / 30) + 1
        bd = ctx.input
        dt = datetime(bd.year, bd.month, bd.day, bd.hour, bd.minute)

        ctx.analysis['jaimini'] = {
            "karakas": JaiminiEngine.calculate_charakarakas(ctx.planets),
            "padas": JaiminiEngine.calculate_arudha_padas(asc_sign, ctx.planets),
            "chara_dasha": JaiminiEngine.calculate_chara_dasha(asc_sign, ctx.planets, dt)
        }
