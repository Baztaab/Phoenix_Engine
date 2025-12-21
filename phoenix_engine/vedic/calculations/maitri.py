
from typing import Dict, List

class MaitriEngine:
    """
    موتور محاسبه روابط سیارات (Friendship/Enmity)
    """
    
    # روابط طبیعی (Naisargika Maitri)
    # 1=Friend, 0=Neutral, -1=Enemy
    NATURAL_RELATION = {
        "Sun":     {"friend": ["Moon", "Mars", "Jupiter"], "enemy": ["Venus", "Saturn"]},
        "Moon":    {"friend": ["Sun", "Mercury"], "enemy": []}, # Moon has no enemies
        "Mars":    {"friend": ["Sun", "Moon", "Jupiter"], "enemy": ["Mercury"]},
        "Mercury": {"friend": ["Sun", "Venus"], "enemy": ["Moon"]},
        "Jupiter": {"friend": ["Sun", "Moon", "Mars"], "enemy": ["Mercury", "Venus"]},
        "Venus":   {"friend": ["Mercury", "Saturn"], "enemy": ["Sun", "Moon"]},
        "Saturn":  {"friend": ["Mercury", "Venus"], "enemy": ["Sun", "Moon", "Mars"]},
        "Rahu":    {"friend": ["Venus", "Saturn"], "enemy": ["Sun", "Moon", "Mars"]},
        "Ketu":    {"friend": ["Mars", "Venus"], "enemy": ["Sun", "Moon", "Saturn"]}
    }
    
    # ارباب خانه‌ها
    RULERS = {
        1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 
        5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars", 
        9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
    }

    @staticmethod
    def get_natural_relation(planet: str, other: str) -> int:
        if planet == other: return 0
        data = MaitriEngine.NATURAL_RELATION.get(planet, {"friend": [], "enemy": []})
        if other in data["friend"]: return 1
        if other in data["enemy"]: return -1
        return 0 # Neutral

    @staticmethod
    def get_compound_relation(planet: str, sign_number: int, planet_sign: int) -> str:
        """
        محاسبه رابطه مرکب (Panchadha Maitri)
        """
        lord = MaitriEngine.RULERS.get(sign_number)
        if not lord: return "Neutral" # Should not happen if signs are 1-12
        if lord == planet: return "Own" # Swakshetra
        
        # 1. Natural
        natural = MaitriEngine.get_natural_relation(planet, lord)
        
        # 2. Temporary (Tatkalika)
        # Planets in 2,3,4, 10,11,12 from planet are friends
        dist = (sign_number - planet_sign) % 12
        if dist < 0: dist += 12
        # dist indices: 0=1st, 1=2nd, etc.
        # Temp Friends: 2nd(1), 3rd(2), 4th(3), 10th(9), 11th(10), 12th(11)
        is_temp_friend = dist in [1, 2, 3, 9, 10, 11]
        temp = 1 if is_temp_friend else -1
        
        # 3. Compound Score
        score = natural + temp
        
        if score == 2: return "Adhi Mitra"
        if score == 1: return "Mitra"
        if score == 0: return "Sama"
        if score == -1: return "Satru"
        if score == -2: return "Adhi Satru"
        return "Sama"
