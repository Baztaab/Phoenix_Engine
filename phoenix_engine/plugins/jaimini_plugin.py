from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.jaimini.karakas import KarakaEngine
from phoenix_engine.vedic.calculations.jaimini.arudhas import ArudhaEngine
from phoenix_engine.vedic.calculations.jaimini.jaimini_yogas import JaiminiYogaEngine


class JaiminiIndicatorsPlugin(IChartPlugin):
    @property
    def name(self): return "Jaimini Indicators & Yogas (Phase 4+5)"

    def execute(self, ctx):
        if 'jaimini' not in ctx.analysis:
            ctx.analysis['jaimini'] = {}
            
        # 1. Karakas
        karakas = KarakaEngine.calculate_chara_karakas(ctx.planets, use_8_karakas=False)
        ctx.analysis['jaimini']['karakas'] = karakas
        
        # 2. Arudhas
        asc_sign = int(ctx.ascendant / 30) + 1
        arudhas = ArudhaEngine.calculate_arudhas(asc_sign, ctx.planets)
        
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        arudhas_verbose = {}
        for k, sign_id in arudhas.items():
            arudhas_verbose[k] = {
                "sign_id": sign_id,
                "sign_name": sign_names[sign_id-1]
            }
        ctx.analysis['jaimini']['arudhas'] = arudhas_verbose
        
        # 3. Jaimini Yogas (Phase 5)
        yogas = JaiminiYogaEngine.check_raja_yogas(karakas, ctx.planets, asc_sign)
        ctx.analysis['jaimini']['yogas'] = yogas
