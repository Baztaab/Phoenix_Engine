from datetime import datetime
from zoneinfo import ZoneInfo
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.dashas.yogini import YoginiDashaEngine
from phoenix_engine.vedic.calculations.dashas.chara import CharaDashaEngine
from phoenix_engine.vedic.calculations.dashas.narayana import NarayanaDashaEngine
from phoenix_engine.vedic.calculations.dashas.sudasa import SudasaDashaEngine


class AdvancedDashasPlugin(IChartPlugin):
    @property
    def name(self): return "Advanced Dasha Systems (Phase 3)"

    def execute(self, ctx):
        # Init container if not exists
        if 'dashas' not in ctx.analysis:
            ctx.analysis['dashas'] = {}
            
        # Build aware datetime from context input
        try:
            tz = ZoneInfo(ctx.input.timezone)
            birth_dt = datetime(
                ctx.input.year, ctx.input.month, ctx.input.day,
                ctx.input.hour, ctx.input.minute, tzinfo=tz
            )
        except Exception:
            birth_dt = datetime(
                ctx.input.year, ctx.input.month, ctx.input.day,
                ctx.input.hour, ctx.input.minute
            )
        
        # 1. Yogini Dasha
        if 'Moon' in ctx.planets:
            moon_lon = ctx.planets['Moon'].longitude
            yogini_list = YoginiDashaEngine.calculate(moon_lon, birth_dt)
            ctx.analysis['dashas']['yogini'] = yogini_list
            
        # 2. Chara Dasha (K.N. Rao)
        asc_sign = int(ctx.ascendant / 30) + 1
        chara_list = CharaDashaEngine.calculate(asc_sign, ctx.planets, birth_dt)
        ctx.analysis['dashas']['chara_knr'] = chara_list

        # 3. Narayana Dasha (General)
        narayana_list = NarayanaDashaEngine.calculate(asc_sign, ctx.planets, birth_dt)
        ctx.analysis['dashas']['narayana'] = narayana_list

        # 4. Sudasa Dasha (JHora Logic)
        sudasa_list = SudasaDashaEngine.calculate(ctx.ascendant, ctx.planets, birth_dt)
        ctx.analysis['dashas']['sudasa'] = sudasa_list
