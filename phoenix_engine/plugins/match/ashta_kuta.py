
from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.domain.match import KutaScore

class AshtaKutaPlugin:
    "پلاگین محاسبه 8 کوتای اصلی (Varna, Vashya, Tara, Yoni, Maitri, Gana, Bhakoot, Nadi)"
    
    def calculate(self, moon1_lon: float, moon2_lon: float) -> list[KutaScore]:
        scores = []
        
        # 1. Nakshatra Calc
        nak1 = int(moon1_lon / 13.333333) + 1
        nak2 = int(moon2_lon / 13.333333) + 1
        
        # 2. Mock Logic for Structure (JHora Logic goes here)
        # Nadi (8 points) - Most important
        nadi_score = 8.0 if (nak1 % 3) != (nak2 % 3) else 0.0
        scores.append(KutaScore(name="Nadi", score=nadi_score, max_score=8.0, description="Physiological Compatibility"))

        # Bhakoot (7 points)
        bhakoot_score = 7.0 # Simplify
        scores.append(KutaScore(name="Bhakoot", score=bhakoot_score, max_score=7.0, description="Emotional Compatibility"))

        # Gana (6 points)
        gana_score = 6.0
        scores.append(KutaScore(name="Gana", score=gana_score, max_score=6.0, description="Temperament"))
        
        # Maitri (5 points)
        scores.append(KutaScore(name="Maitri", score=5.0, max_score=5.0, description="Friendship"))

        # Yoni (4 points)
        scores.append(KutaScore(name="Yoni", score=4.0, max_score=4.0, description="Instinctive Compatibility"))
        
        # Tara (3 points)
        scores.append(KutaScore(name="Tara", score=3.0, max_score=3.0, description="Destiny"))
        
        # Vashya (2 points)
        scores.append(KutaScore(name="Vashya", score=2.0, max_score=2.0, description="Attraction"))

        # Varna (1 point)
        scores.append(KutaScore(name="Varna", score=1.0, max_score=1.0, description="Work Compatibility"))

        return scores
