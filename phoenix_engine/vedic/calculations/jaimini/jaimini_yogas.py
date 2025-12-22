from typing import Dict, List, Any
from phoenix_engine.vedic.calculations.jaimini.drishti import JaiminiDrishtiEngine


class JaiminiYogaEngine:
    """
    شناسایی یوگاهای جایمینی (Jaimini Raja Yogas).
    تمرکز بر اتصال (Connection) بین کاراکاهای اصلی: AK, AmK, PK, DK, 5th Lord.
    """
    
    @staticmethod
    def check_raja_yogas(karakas: Dict[str, str], planets: Dict[str, Any], asc_sign: int) -> List[Dict]:
        yogas = []
        
        # 1. شناسایی لرد پنجم (5th Lord from Lagna) - Punya Lord
        house_5_sign = (asc_sign + 4)
        if house_5_sign > 12:
            house_5_sign -= 12
        
        rulers = {1:"Mars", 2:"Venus", 3:"Mercury", 4:"Moon", 5:"Sun", 6:"Mercury", 
                  7:"Venus", 8:"Mars", 9:"Jupiter", 10:"Saturn", 11:"Saturn", 12:"Jupiter"}
        lord_5_name = rulers.get(house_5_sign)
        
        pairs_to_check = [
            ("AK", "AmK", "Jaimini Raja Yoga (Soul & Career - Highest)"),
            ("AK", "PK",  "Jaimini Raja Yoga (Soul & Power/Intellect)"),
            ("AK", "DK",  "Jaimini Raja Yoga (Soul & Wealth/Spouse)"),
            ("AmK", "PK", "Jaimini Raja Yoga (Career & Power)"),
            ("AmK", "DK", "Jaimini Raja Yoga (Career & Wealth)"),
            ("PK", "DK",  "Jaimini Raja Yoga (Power & Wealth)")
        ]
        
        if lord_5_name:
             pairs_to_check.append(("AK", "5L", "Jaimini Raja Yoga (Soul & Punya/5th Lord)"))
             pairs_to_check.append(("AmK", "5L", "Jaimini Raja Yoga (Career & Punya/5th Lord)"))

        for k1_code, k2_code, yoga_name in pairs_to_check:
            p1_name = karakas.get(k1_code)
            
            if k2_code == "5L":
                p2_name = lord_5_name
            else:
                p2_name = karakas.get(k2_code)
                
            if not p1_name or not p2_name:
                continue
            if p1_name not in planets or p2_name not in planets:
                continue
            
            p1_sign = planets[p1_name].sign
            p2_sign = planets[p2_name].sign
            
            connection = JaiminiDrishtiEngine.check_connection(p1_sign, p2_sign)
            
            if connection:
                yogas.append({
                    "name": yoga_name,
                    "actors": f"{p1_name} ({k1_code}) - {p2_name} ({k2_code})",
                    "type": connection,
                    "signs": f"{p1_sign} - {p2_sign}"
                })
                
        return yogas
