from datetime import datetime
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.vedic.calculations.transit_calc import TransitCalculator
from phoenix_engine.vedic.calculations.gochar import GocharEngine


class TransitAnalysisPlugin(IChartPlugin):
    @property
    def name(self): return "Transit Analysis System (Smart Gochar - Phase 8)"

    def execute(self, ctx):
        if 'transits' not in ctx.analysis:
            ctx.analysis['transits'] = {}

        # 1. Fetch SAV
        sav_scores = [25] * 12
        if 'ashtakavarga' in ctx.analysis and 'sav' in ctx.analysis['ashtakavarga']:
            sav_list = ctx.analysis['ashtakavarga']['sav']
            sav_scores = [item['score'] for item in sav_list]

        # 2. Build Context (karakas, active dasha lords)
        context = {
            "karakas": {},
            "active_dasha_lords": []
        }
        if 'jaimini' in ctx.analysis and 'karakas' in ctx.analysis['jaimini']:
            context["karakas"] = ctx.analysis['jaimini']['karakas']
        
        target_date = getattr(ctx, 'prediction_start_date', datetime.now()).strftime("%Y-%m-%d")
        if 'dashas' in ctx.analysis and 'vimshottari' in ctx.analysis['dashas']:
            for d in ctx.analysis['dashas']['vimshottari']:
                if d['start'] <= target_date <= d['end']:
                    context["active_dasha_lords"].append(d['lord'])
                    break
        
        # 3. Calc Raw Transits
        start_date = getattr(ctx, 'prediction_start_date', datetime.now())
        raw_transits = TransitCalculator.get_daily_transits(start_date, days_count=30)
        
        # 4. Ingress Events
        ingress_events = TransitCalculator.detect_ingress(raw_transits)
        
        # 5. Smart Analysis
        asc_sign = int(ctx.ascendant / 30) + 1
        smart_data = GocharEngine.analyze_smart_series(
            raw_transits,
            ctx.planets,
            asc_sign,
            sav_scores,
            context
        )
        
        # 6. Output
        ctx.analysis['transits'] = {
            "meta": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "duration": "30 Days",
                "active_dasha": context["active_dasha_lords"]
            },
            "events": ingress_events,
            "forecast": smart_data
        }
