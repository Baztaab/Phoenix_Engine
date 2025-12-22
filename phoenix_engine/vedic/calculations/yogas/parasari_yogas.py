from typing import Dict, List, Any


class ParasariYogaEngine:
    """
    محاسبه یوگاهای مهم پاراشاری (بر اساس منطق JHora).
    شامل: Dharma-Karmadhipati, Vipareeta, Neecha Bhanga.
    """

    @staticmethod
    def get_house_lord(house_id: int, planets: Dict[str, Any]) -> str:
        """پیدا کردن حاکم یک خانه (1-12)."""
        rulers = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                  7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"}
        return rulers.get(house_id)

    @staticmethod
    def check_association(p1_name: str, p2_name: str, planets: Dict[str, Any]) -> bool:
        """بررسی اتصال (قران) یا نظر متقابل (Graha Drishti ساده)."""
        if p1_name not in planets or p2_name not in planets:
            return False
        
        p1 = planets[p1_name]
        p2 = planets[p2_name]
        
        if p1.sign == p2.sign:
            return True
        
        dist = abs(p1.sign - p2.sign)
        if dist == 6:
            return True
        
        return False

    @staticmethod
    def calculate_yogas(asc_sign: int, planets: Dict[str, Any]) -> List[Dict]:
        yogas = []
        
        # --- 1. Dharma-Karmadhipati Yoga (9L + 10L) ---
        house_9 = asc_sign + 8
        if house_9 > 12:
            house_9 -= 12
        house_10 = asc_sign + 9
        if house_10 > 12:
            house_10 -= 12
        
        lord_9 = ParasariYogaEngine.get_house_lord(house_9, planets)
        lord_10 = ParasariYogaEngine.get_house_lord(house_10, planets)
        
        if lord_9 and lord_10 and ParasariYogaEngine.check_association(lord_9, lord_10, planets):
            yogas.append({
                "name": "Dharma-Karmadhipati Yoga",
                "description": "Association of 9th and 10th Lords (Success & Destiny).",
                "actors": f"{lord_9} - {lord_10}"
            })

        # --- 2. Vipareeta Raja Yoga (6, 8, 12 Lords in 6, 8, 12) ---
        h6_sign = (asc_sign + 5)
        if h6_sign > 12:
            h6_sign -= 12
        h8_sign = (asc_sign + 7)
        if h8_sign > 12:
            h8_sign -= 12
        h12_sign = (asc_sign + 11)
        if h12_sign > 12:
            h12_sign -= 12
        
        dusthanas = [h6_sign, h8_sign, h12_sign]
        
        l6 = ParasariYogaEngine.get_house_lord(h6_sign, planets)
        l8 = ParasariYogaEngine.get_house_lord(h8_sign, planets)
        l12 = ParasariYogaEngine.get_house_lord(h12_sign, planets)
        
        if l6 and l6 in planets and planets[l6].sign in dusthanas:
            yogas.append({"name": "Vipareeta Raja Yoga (Harsha)", "description": "6th Lord in Dusthana.", "actors": l6})
        
        if l8 and l8 in planets and planets[l8].sign in dusthanas:
            yogas.append({"name": "Vipareeta Raja Yoga (Sarala)", "description": "8th Lord in Dusthana.", "actors": l8})
            
        if l12 and l12 in planets and planets[l12].sign in dusthanas:
            yogas.append({"name": "Vipareeta Raja Yoga (Vimala)", "description": "12th Lord in Dusthana.", "actors": l12})

        return yogas
