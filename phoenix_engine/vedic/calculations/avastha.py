
from typing import Dict, Any

class AvasthaEngine:
    "موتور محاسبه حالات سیارات (Avasthas)"
    
    @staticmethod
    def calculate_baladi_avastha(planet_name: str, degree: float, sign: int) -> str:
        # Baladi Avastha (Age): Infant, Young, Adult, Old, Dead
        # Odd Signs: 0-6 Infant, 6-12 Young, 12-18 Adult, 18-24 Old, 24-30 Dead
        # Even Signs: Reverse order
        
        state = ""
        is_odd = (sign % 2 != 0)
        
        if 0 <= degree < 6:
            state = "Bala (Infant)" if is_odd else "Mrit (Dead)"
        elif 6 <= degree < 12:
            state = "Kumara (Young)" if is_odd else "Vriddha (Old)"
        elif 12 <= degree < 18:
            state = "Yuva (Adult)" # Best state
        elif 18 <= degree < 24:
            state = "Vriddha (Old)" if is_odd else "Kumara (Young)"
        elif 24 <= degree <= 30:
            state = "Mrit (Dead)" if is_odd else "Bala (Infant)"
            
        return state

    @staticmethod
    def calculate_jagradadi_avastha(planet_name: str, is_retrograde: bool, is_exalted: bool, is_debilitated: bool, house_type: str) -> str:
        # Jagradadi (Consciousness): Jagrat (Awake), Swapna (Dreaming), Sushupti (Deep Sleep)
        if is_exalted or house_type == "Own":
            return "Jagrat (Awake)" # Fully effective
        elif is_debilitated or is_retrograde: 
            # Note: Retrogression logic varies, often considered strong (Chesta) but unpredictable
            return "Sushupti (Deep Sleep)" # Or specialized state
        else:
            return "Swapna (Dreaming)" # Average

    @staticmethod
    def calculate_all(planets: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        results = {}
        for name, p in planets.items():
            if name in ["Rahu", "Ketu", "Ascendant"]: continue
            
            # Baladi
            baladi = AvasthaEngine.calculate_baladi_avastha(name, p.degree, p.sign)
            
            # Jagradadi (Simplified)
            # Needs Maitri/Sign knowledge. For now, basic based on degree/speed
            # Will be enriched in Semantic Layer
            
            results[name] = {
                "baladi": baladi,
                "jagradadi": "Pending Maitri Check" 
            }
        return results
