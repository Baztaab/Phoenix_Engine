from typing import Dict, List, Any
from datetime import timedelta
from phoenix_engine.vedic.const import ODD_FOOTED_SIGNS, EVEN_FOOTED_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS


class CharaDashaEngine:
    
    @staticmethod
    def get_stronger_lord(sign_id: int, planets: Dict[str, Any]) -> int:
        # Simple logic for now: Mars vs Ketu (Sc), Sat vs Rahu (Aq)
        if sign_id == 8:  # Scorpio
            return planets.get("Mars", planets.get("Ketu", planets["Mars"])).sign if "Mars" in planets else sign_id
        if sign_id == 11:  # Aquarius
            return planets.get("Saturn", planets.get("Rahu", planets["Saturn"])).sign if "Saturn" in planets else sign_id
        
        rulers = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                  7: "Venus", 9: "Jupiter", 10: "Saturn", 12: "Jupiter"}
        p_name = rulers.get(sign_id)
        if p_name and p_name in planets:
            return planets[p_name].sign
        return sign_id

    @staticmethod
    def calculate_duration(sign_id: int, planets: Dict[str, Any]) -> int:
        lord_pos = CharaDashaEngine.get_stronger_lord(sign_id, planets)
        
        sign_idx_0 = sign_id - 1
        is_even_footed = sign_idx_0 in EVEN_FOOTED_SIGNS
        
        if is_even_footed:
            count = (sign_id - lord_pos)
            if count <= 0:
                count += 12
        else:
            count = (lord_pos - sign_id)
            if count <= 0:
                count += 12
            
        duration = count - 1
        if duration == 0:
            duration = 12
        
        # Placeholder for exaltation/debilitation adjustment if needed:
        # Could add/subtract 1 year based on lord's dignity using EXALTATION_SIGNS/DEBILITATION_SIGNS.
        return duration

    @staticmethod
    def calculate(asc_sign: int, planets: Dict[str, Any], birth_date: Any) -> List[Dict]:
        dashas = []
        curr_date = birth_date
        
        ninth_house = asc_sign + 8
        if ninth_house > 12:
            ninth_house -= 12
        ninth_idx = ninth_house - 1
        
        direction = -1 if ninth_idx in EVEN_FOOTED_SIGNS else 1
            
        curr_sign = asc_sign
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for _ in range(12):
            dur = CharaDashaEngine.calculate_duration(curr_sign, planets)
            end_date = curr_date + timedelta(days=dur * 365.256363)
            
            dashas.append({
                "sign_name": sign_names[curr_sign-1],
                "duration": dur,
                "end_date": end_date.strftime("%Y-%m-%d")
            })
            curr_date = end_date
            
            curr_sign += direction
            if curr_sign > 12:
                curr_sign = 1
            elif curr_sign < 1:
                curr_sign = 12
            
        return dashas
