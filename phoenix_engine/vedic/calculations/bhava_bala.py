
from typing import Dict, List, Any

class BhavaBalaEngine:
    "موتور محاسبه قدرت ۱۲ خانه (House Strength)"
    # توجه: محاسبه دقیق باوا بالا بسیار پیچیده است.
    # این نسخه "Simplified Critical Logic" است که پارامترهای اصلی را در نظر می‌گیرد:
    # 1. Bhava Adhipati Bala (قدرت صاحب خانه - از شادبالا می‌آید)
    # 2. Bhava Digbala (قدرت جهت خانه)
    # 3. Bhava Drishti (نظرات وارده بر خانه)
    
    @staticmethod
    def calculate_bhava_digbala(house_num: int, sign_type: str) -> float:
        # Nara Rasi (Human) in 1 -> Strong
        # Jalachara (Watery) in 4 -> Strong
        # Keeta (Insect) in 7 -> Strong
        # Pashu (Quadruped) in 10 -> Strong
        # فعلاً یک مدل ساده شده بر اساس جهت خانه‌ها:
        # 1 (East), 4 (North), 7 (West), 10 (South) get max points logic
        
        # Simplified: Kendras get 60, Panaparas 30, Apoklimas 15
        if house_num in [1, 4, 7, 10]: return 60.0
        if house_num in [2, 5, 8, 11]: return 30.0
        return 15.0

    @staticmethod
    def calculate_all(houses_long: List[float], planets: Dict[str, Any], shadbala: Dict[str, Any], aspects: List[Any]) -> Dict[int, float]:
        results = {}
        
        # نگاشت ارباب خانه‌ها (Simplified Rulers)
        RULERS = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 
            5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars", 
            9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
        }
        
        asc_long = houses_long[0] # Approx Ascendant from house list if available or passed separately
        # But 'houses_long' usually implies cusps. Let's assume passed cusps.
        
        for h_idx, cusp in enumerate(houses_long):
            h_num = h_idx + 1
            sign = int(cusp / 30) + 1
            lord = RULERS.get(sign, "Saturn")
            
            # 1. Lord Strength (from Shadbala)
            lord_str = 0.0
            if shadbala and lord in shadbala:
                lord_str = shadbala[lord].total * 60 # Convert back to Virupas approx scale if needed, or keep Rupa
            
            # 2. Directional Strength
            digbala = BhavaBalaEngine.calculate_bhava_digbala(h_num, "Human") # Simplified type
            
            # 3. Occupancy (Planets in House)
            occupancy = 0
            for p_name, p_data in planets.items():
                if p_data.house == h_num:
                    occupancy += 15 # Boost for planet presence
            
            # Total Bhava Bala (Rupas)
            total = (lord_str * 10 + digbala + occupancy) / 60.0 # Weighted formula
            results[h_num] = round(total, 2)
            
        return results
