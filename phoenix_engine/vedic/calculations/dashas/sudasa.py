from typing import Dict, List, Any
from datetime import timedelta
from phoenix_engine.vedic.const import ODD_SIGNS, EVEN_SIGNS
from phoenix_engine.vedic.calculations.dashas.chara import CharaDashaEngine


class SudasaDashaEngine:
    
    @staticmethod
    def calculate_sree_lagna(asc_lon: float, moon_lon: float) -> float:
        # Formula: Add (Moon's travel in Nakshatra * 360) to Ascendant
        nak_span = 13.333333333
        moon_nak_passed_deg = moon_lon % nak_span
        moon_fraction = moon_nak_passed_deg / nak_span
        sree_lagna_deg = (asc_lon + (moon_fraction * 360.0)) % 360.0
        return sree_lagna_deg

    @staticmethod
    def calculate(asc_lon: float, planets: Dict[str, Any], birth_date: Any) -> List[Dict]:
        moon_lon = planets['Moon'].longitude
        sl_deg = SudasaDashaEngine.calculate_sree_lagna(asc_lon, moon_lon)
        sl_sign = int(sl_deg / 30) + 1
        
        # Balance fraction of SL sign remaining
        sl_sign_rem_deg = 30.0 - (sl_deg % 30)
        balance_factor = sl_sign_rem_deg / 30.0
        
        direction = 1 if (sl_sign-1) in ODD_SIGNS else -1
        
        sat_sign = planets['Saturn'].sign
        ketu_sign = planets['Ketu'].sign
        if sat_sign == sl_sign:
            direction = 1
        elif ketu_sign == sl_sign:
            direction = -1
        
        # Sequence: Kendras, Panaparas, Apoklimas from SL
        kendra_offsets = [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11]
        
        dashas = []
        curr_date = birth_date
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

        for i, offset in enumerate(kendra_offsets):
            shift = offset * direction
            curr_sign = (sl_sign + shift)
            while curr_sign > 12:
                curr_sign -= 12
            while curr_sign < 1:
                curr_sign += 12
            
            dur = CharaDashaEngine.calculate_duration(curr_sign, planets)
            
            if i == 0:
                real_dur = dur * balance_factor
            else:
                real_dur = dur
                
            end_date = curr_date + timedelta(days=real_dur * 365.256363)
            
            dashas.append({
                "sign_name": sign_names[curr_sign-1],
                "duration": round(real_dur, 2),
                "full_duration": dur,
                "end_date": end_date.strftime("%Y-%m-%d")
            })
            curr_date = end_date
            
        return dashas
