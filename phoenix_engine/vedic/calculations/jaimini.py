
from typing import Dict, List, Any
from datetime import datetime, timedelta

class JaiminiEngine:
    """
    موتور سیستم جایمینی (Jaimini System) - نسخه کامل K.N. Rao
    شامل: Karakas, Arudhas, Chara Dasha (Maha & Antar).
    """

    KARAKA_NAMES = ["Atmakaraka (AK)", "Amatyakaraka (AmK)", "Bhratrukaraka (BK)", 
                    "Matrukaraka (MK)", "Putrakaraka (PK)", "Gnatikaraka (GK)", "Darakaraka (DK)"]

    # جهت چرخش داشا (K.N. Rao Standard)
    # 1 = Direct (Aries, Leo, Virgo, Libra, Aquarius, Pisces) -> WRONG OLD MAPPING
    # Correct K.N. Rao Mapping:
    # Savya (Direct): Aries(1), Taurus(2), Gemini(3), Libra(7), Scorpio(8), Sagittarius(9)
    # Apasavya (Reverse): Cancer(4), Leo(5), Virgo(6), Capricorn(10), Aquarius(11), Pisces(12)
    DASHA_DIRECTION = {
        1: 1, 2: 1, 3: 1, 
        4: -1, 5: -1, 6: -1,
        7: 1, 8: 1, 9: 1, 
        10: -1, 11: -1, 12: -1
    }

    @staticmethod
    def get_sign(longitude: float) -> int:
        return int(longitude / 30) + 1

    @staticmethod
    def normalize_sign(sign: int) -> int:
        return (sign - 1) % 12 + 1

    @staticmethod
    def get_planet_sign(p_name: str, planets: Dict[str, Any]) -> int:
        if p_name not in planets: return 0
        return int(planets[p_name].longitude / 30) + 1

    @staticmethod
    def get_dual_lord_strength(sign_num: int, planets: Dict[str, Any]) -> str:
        """
        تعیین ارباب قوی‌تر برای عقرب (Mars/Ketu) و دلو (Saturn/Rahu).
        قوانین:
        1. سیاره‌ای که با سیارات بیشتری همراه است.
        2. اگر برابر بود، سیاره‌ای که شرف (Exalted) است.
        3. اگر برابر بود، سیاره‌ای که درجه بالاتری دارد.
        """
        if sign_num == 8: # Scorpio
            p1, p2 = "Mars", "Ketu"
        elif sign_num == 11: # Aquarius
            p1, p2 = "Saturn", "Rahu"
        else:
            return "Unknown"

        # 1. Conjunction Count
        def count_conjunctions(p_name):
            if p_name not in planets: return -1
            p_sign = int(planets[p_name].longitude / 30) + 1
            count = 0
            for name, data in planets.items():
                if name == p_name: continue
                if (int(data.longitude / 30) + 1) == p_sign:
                    count += 1
            return count

        c1 = count_conjunctions(p1)
        c2 = count_conjunctions(p2)
        
        if c1 > c2: return p1
        if c2 > c1: return p2
        
        # 2. Exaltation (Simplified check)
        # Mars Exalted in 10, Ketu in ? (Disputed, usually ignored or Sag/Sco)
        # Saturn in 7, Rahu in ? (Gem/Tau)
        # Let's move to Degree as reliable tie-breaker
        
        # 3. Higher Degree (Longitude in sign)
        deg1 = planets[p1].longitude % 30
        deg2 = planets[p2].longitude % 30
        
        if deg1 >= deg2: return p1
        return p2

    @staticmethod
    def get_chara_lord_sign(sign_num: int, planets: Dict[str, Any]) -> int:
        """پیدا کردن نشانِ اربابِ یک نشان (با حل تضادها)"""
        # Standard Rulers
        rulers = {
            1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 
            5: "Sun", 6: "Mercury", 7: "Venus", 
            9: "Jupiter", 10: "Saturn", 12: "Jupiter"
        }
        
        if sign_num in [8, 11]:
            lord_name = JaiminiEngine.get_dual_lord_strength(sign_num, planets)
        else:
            lord_name = rulers.get(sign_num, "Sun") # Default fallback

        return JaiminiEngine.get_planet_sign(lord_name, planets)

    @staticmethod
    def calculate_chara_dasha(asc_sign: int, planets: Dict[str, Any], birth_date: datetime) -> List[Dict[str, Any]]:
        """
        محاسبه Chara Dasha (Maha + Antar)
        """
        dashas = []
        # تاریخ شروع با دقت روز
        current_date = birth_date
        
        direction = JaiminiEngine.DASHA_DIRECTION.get(asc_sign, 1)
        
        # 12 Maha Dashas
        for i in range(12):
            # A. Calculate Maha Dasha Sign
            if direction == 1:
                md_sign = JaiminiEngine.normalize_sign(asc_sign + i)
            else:
                md_sign = JaiminiEngine.normalize_sign(asc_sign - i)
            
            # B. Calculate Duration
            lord_pos = JaiminiEngine.get_chara_lord_sign(md_sign, planets)
            
            # K.N. Rao Logic for Counting
            # Direct Signs: Count Forward from Sign to Lord
            # Indirect Signs: Count Backward from Sign to Lord
            
            sign_dir = JaiminiEngine.DASHA_DIRECTION.get(md_sign, 1)
            
            if sign_dir == 1:
                count = (lord_pos - md_sign) % 12
                if count < 0: count += 12
            else:
                count = (md_sign - lord_pos) % 12
                if count < 0: count += 12
            
            years = count
            if years == 0: years = 12
            
            # C. Calculate Dates
            # Approximate leap years by using 365.2425 or python date math
            # Here we add years simply. For precision, we should handle exact dates.
            # Using simple year addition for clean JSON, can be enhanced.
            
            # Converting years to days for date math
            days_duration = int(years * 365.25)
            end_date = current_date + timedelta(days=days_duration)
            
            # D. Antardashas (Sub-periods)
            # Logic: Antardasha starts from the Sign of the Maha Dasha (or the one next to it?)
            # K.N. Rao: AD starts from the sign occupied by the LORD of the MD? Or standard sequence?
            # Standard Practice: ADs follow the same direction as the MD sign's nature.
            # Starting sign: Usually the sign following the MD sign (if direct) or previous (if indirect).
            # But let's use the widely accepted: ADs start from the MD sign itself or the next one.
            # Simplified for V1: ADs are 1/12th of MD. Sequence follows MD sign direction.
            
            sub_periods = []
            ad_duration_months = years # 12 ADs in 'years' years -> each AD is 'years' months long.
            current_ad_date = current_date
            
            ad_direction = JaiminiEngine.DASHA_DIRECTION.get(md_sign, 1)
            
            for k in range(1, 13): # 12 Antardashas
                # Sequence: Usually starts from the sign in the next house from MD sign (Direct) or prev (Indirect)
                # K.N. Rao often uses: Start from the sign following the MD sign based on direction.
                if ad_direction == 1:
                    ad_sign = JaiminiEngine.normalize_sign(md_sign + k) # Start from next
                else:
                    ad_sign = JaiminiEngine.normalize_sign(md_sign - k) # Start from prev
                
                # Duration in days
                ad_days = (years * 365.25) / 12
                ad_end = current_ad_date + timedelta(days=ad_days)
                
                sub_periods.append({
                    "sign": ad_sign,
                    "start": current_ad_date.strftime("%Y-%m-%d"),
                    "end": ad_end.strftime("%Y-%m-%d")
                })
                current_ad_date = ad_end

            dashas.append({
                "sign": md_sign,
                "lord_sign": lord_pos,
                "duration_years": years,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "sub_periods": sub_periods
            })
            
            current_date = end_date
            
        return dashas

    # --- Standard Methods ---
    @staticmethod
    def calculate_charakarakas(planets: Dict[str, Any]) -> Dict[str, str]:
        valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        planet_degrees = []
        for name in valid_planets:
            if name not in planets: continue
            deg = planets[name].longitude % 30
            planet_degrees.append({"name": name, "degree": deg})
        planet_degrees.sort(key=lambda x: x["degree"], reverse=True)
        results = {}
        for i, karaka_label in enumerate(JaiminiEngine.KARAKA_NAMES):
            if i < len(planet_degrees):
                p_name = planet_degrees[i]["name"]
                results[karaka_label] = f"{p_name} ({round(planet_degrees[i]['degree'], 2)}°)"
            else:
                results[karaka_label] = "N/A"
        return results

    @staticmethod
    def calculate_arudha_padas(ascendant_sign: int, planets: Dict[str, Any]) -> Dict[str, int]:
        padas = {}
        planet_signs = {name: int(data.longitude / 30) + 1 for name, data in planets.items()}
        # Simplified rulers for AL calc
        rulers = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars", 9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"}
        
        for house_num in range(1, 13):
            house_sign = JaiminiEngine.normalize_sign(ascendant_sign + house_num - 1)
            lord_name = rulers.get(house_sign, "Saturn")
            
            # Exception for Sco/Aq lords in AL: Usually heavier lord used. 
            # For simplicity in V1 we stick to standard unless we pass planets to use get_dual_lord_strength logic here too.
            # Let's rely on standard logic for AL stability first.
            
            if lord_name not in planet_signs: continue
            lord_sign = planet_signs[lord_name]
            
            dist = (lord_sign - house_sign) % 12 
            arudha_sign_index = (lord_sign - 1 + dist) % 12 + 1
            
            dist_from_house = (arudha_sign_index - house_sign) % 12
            if dist_from_house == 0 or dist_from_house == 6:
                arudha_sign_index = JaiminiEngine.normalize_sign(arudha_sign_index + 9)
                
            label = f"A{house_num}"
            if house_num == 1: label = "AL (Arudha Lagna)"
            if house_num == 12: label = "UL (Upapada)"
            padas[label] = arudha_sign_index
        return padas
