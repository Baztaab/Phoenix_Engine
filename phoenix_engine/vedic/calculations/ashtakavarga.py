
from typing import Dict, List, Any

class AshtakavargaEngine:
    """
    موتور محاسباتی Ashtakavarga (سیستم امتیازدهی ۸ گانه)
    منطبق بر استاندارد Parashara Light و JHora.
    """

    # جداول نقاط فرخنده (Benefic Points / Rekhas)
    # فرمت: 'Giver': [Houses from Giver where point is given]
    
    # 1. Sun's Ashtakavarga
    SUN_BAV = {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [3, 4, 6, 10, 11, 12]
    }

    # 2. Moon's Ashtakavarga
    MOON_BAV = {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [3, 6, 10, 11]
    }

    # 3. Mars's Ashtakavarga
    MARS_BAV = {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 3, 6, 10, 11]
    }

    # 4. Mercury's Ashtakavarga
    MERCURY_BAV = {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11]
    }

    # 5. Jupiter's Ashtakavarga
    JUPITER_BAV = {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11]
    }

    # 6. Venus's Ashtakavarga
    VENUS_BAV = {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 4, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
    }

    # 7. Saturn's Ashtakavarga
    SATURN_BAV = {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11]
    }

    RULES_MAP = {
        "Sun": SUN_BAV,
        "Moon": MOON_BAV,
        "Mars": MARS_BAV,
        "Mercury": MERCURY_BAV,
        "Jupiter": JUPITER_BAV,
        "Venus": VENUS_BAV,
        "Saturn": SATURN_BAV
    }

    @staticmethod
    def calculate_bav(planet_name: str, positions: Dict[str, int]) -> List[int]:
        """
        محاسبه Bhinna Ashtakavarga برای یک سیاره خاص.
        خروجی: لیستی با ۱۲ عدد (امتیاز هر نشان از حمل تا حوت).
        """
        if planet_name not in AshtakavargaEngine.RULES_MAP:
            return [0] * 12
            
        rules = AshtakavargaEngine.RULES_MAP[planet_name]
        scores = [0] * 12 # Index 0=Aries, 11=Pisces
        
        # Iterate through givers (Sun..Sat + Asc)
        for giver, offsets in rules.items():
            if giver not in positions: continue
            
            giver_sign = positions[giver] # 1 to 12
            
            for offset in offsets:
                # Calculate target sign index (0-11)
                # Formula: (SignIndex - 1 + HouseOffset - 1) % 12
                # e.g. Sun in Aries(1), Offset 1 -> Aries(0)
                target_idx = (giver_sign - 1 + offset - 1) % 12
                scores[target_idx] += 1
                
        return scores

    @staticmethod
    def calculate_all(positions: Dict[str, int]) -> Dict[str, Any]:
        """
        محاسبه تمام BAV ها و SAV کلی
        """
        bav_results = {}
        sarva_scores = [0] * 12
        
        planets_to_calc = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        
        for p in planets_to_calc:
            bav = AshtakavargaEngine.calculate_bav(p, positions)
            bav_results[p] = bav
            
            # Add to Sarvashtakavarga
            for i in range(12):
                sarva_scores[i] += bav[i]
                
        return {
            "bav": bav_results,
            "sav": sarva_scores
        }
