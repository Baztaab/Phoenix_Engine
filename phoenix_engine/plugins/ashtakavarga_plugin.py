from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.ashtakavarga import AshtakavargaEngine


class AshtakavargaPlugin(IChartPlugin):
    @property
    def name(self): return "Ashtakavarga System (Phase 7)"

    def execute(self, ctx):
        if 'ashtakavarga' not in ctx.analysis:
            ctx.analysis['ashtakavarga'] = {}
            
        asc_sign = int(ctx.ascendant / 30) + 1
        
        bav = AshtakavargaEngine.calculate_bav(ctx.planets, asc_sign)
        sav = AshtakavargaEngine.calculate_sav(bav)
        sodhita_data = AshtakavargaEngine.calculate_sodhita_and_pinda(bav, ctx.planets)
        
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        sav_verbose = []
        for i in range(12):
            sav_verbose.append({
                "sign": sign_names[i],
                "score": sav[i],
                "is_strong": sav[i] >= 28
            })
            
        ctx.analysis['ashtakavarga'] = {
            "bav": bav,
            "sav": sav_verbose,
            "details": sodhita_data
        }
