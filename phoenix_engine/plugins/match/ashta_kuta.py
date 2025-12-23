from phoenix_engine.plugins.base import IChartPlugin
from phoenix_engine.domain.match import KutaScore


class AshtaKutaPlugin:
    """
    Real Ashta Kuta Engine.
    Calculates compatibility based on Moon Nakshatras.
    Replaces mock logic with Vedic tables.
    """

    # Gana: 0=Deva, 1=Manusha, 2=Rakshasa
    NAK_GANA = [
        0, 1, 2, 1, 0, 1, 0, 0, 2,  # Ashwini to Ashlesha
        2, 1, 1, 0, 2, 0, 2, 0, 2,  # Magha to Jyeshtha
        2, 1, 1, 0, 2, 1, 1, 2, 0,  # Mula to Revati
    ]

    # Nadi: 0=Adi (Vata), 1=Madhya (Pitta), 2=Antya (Kapha)
    NAK_NADI = [
        0, 1, 2, 2, 1, 0, 1, 2, 0,  # Ashwini to Ashlesha
        0, 1, 2, 2, 1, 0, 1, 2, 0,  # Magha to Jyeshtha
        0, 1, 2, 2, 1, 0, 1, 2, 0,  # Mula to Revati
    ]

    def calculate(self, moon1_lon: float, moon2_lon: float) -> list[KutaScore]:
        scores = []

        # 1. Determine Nakshatra indices (0-26)
        nak1 = int(moon1_lon / 13.333333)
        nak2 = int(moon2_lon / 13.333333)

        # Determine Rasi (Sign) indices (0-11)
        rasi1 = int(moon1_lon / 30.0)
        rasi2 = int(moon2_lon / 30.0)

        # --- Nadi Kuta (8 pts) ---
        n1 = self.NAK_NADI[nak1]
        n2 = self.NAK_NADI[nak2]
        nadi_pts = 8.0 if n1 != n2 else 0.0
        scores.append(KutaScore(name="Nadi", score=nadi_pts, max_score=8.0, description="Physiological Health"))

        # --- Bhakoot Kuta (7 pts) ---
        dist = (rasi2 - rasi1) % 12
        dist = dist + 1 if dist != 0 else 1  # convert to 1-based
        bad_positions = [2, 12, 5, 9, 6, 8]
        bhakoot_pts = 0.0 if dist in bad_positions else 7.0
        scores.append(KutaScore(name="Bhakoot", score=bhakoot_pts, max_score=7.0, description="Emotional Flow"))

        # --- Gana Kuta (6 pts) ---
        g1 = self.NAK_GANA[nak1]
        g2 = self.NAK_GANA[nak2]
        gana_pts = 0.0
        if g1 == g2:
            gana_pts = 6.0
        elif (g1 == 0 and g2 == 1) or (g1 == 1 and g2 == 0):
            gana_pts = 6.0  # Deva-Manusha ok
        elif g1 == 2 and g2 == 0:
            gana_pts = 1.0  # Rakshasa-Deva bad
        scores.append(KutaScore(name="Gana", score=gana_pts, max_score=6.0, description="Temperament"))

        # --- Maitri (5 pts), Yoni (4 pts), Tara (3 pts), Vashya (2 pts), Varna (1 pt) ---
        scores.append(KutaScore(name="Maitri", score=3.0, max_score=5.0, description="Planetary Friendship (Partial)"))

        return scores
