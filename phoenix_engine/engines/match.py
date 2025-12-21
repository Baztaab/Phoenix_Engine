
from phoenix_engine.domain.match import MatchRequest, MatchResult
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.infrastructure.time.manager import TimeEngine
from phoenix_engine.plugins.match.ashta_kuta import AshtaKutaPlugin
from datetime import datetime

class MatchingEngine:
    def process(self, req: MatchRequest) -> MatchResult:
        # 1. Calculate Moons for both
        swe = SwissEphemeris()
        time_eng = TimeEngine()
        
        # P1
        dt1 = datetime(req.p1.year, req.p1.month, req.p1.day, req.p1.hour, req.p1.minute)
        # In real app, apply timezone!
        jd1 = time_eng.get_julian_day(dt1) # Simplified call
        p1_planets = swe.calculate_planets(jd1)
        
        # P2
        dt2 = datetime(req.p2.year, req.p2.month, req.p2.day, req.p2.hour, req.p2.minute)
        jd2 = time_eng.get_julian_day(dt2)
        p2_planets = swe.calculate_planets(jd2)
        
        # 2. Run Plugin
        plugin = AshtaKutaPlugin()
        scores = plugin.calculate(p1_planets['Moon']['longitude'], p2_planets['Moon']['longitude'])
        
        # 3. Aggregate
        total = sum(s.score for s in scores)
        
        return MatchResult(
            total_score=total,
            kutas=scores,
            is_recommended=total > 18,
            meta={"algorithm": "Phoenix Match V1 (Ashta Kuta)"}
        )
