
from typing import Dict, List, Any

class YogaEngine:
    """
    موتور پیشرفته تشخیص یوگاها (Advanced Yoga Detection System)
    شامل: Pancha Mahapurusha, Parivartana, Vipareeta, etc.
    """
    
    # ارباب نشان‌ها
    RULERS = {
        1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 
        5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars", 
        9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
    }
    
    # نشان‌های شرف (Exaltation Signs)
    EXALTATION_SIGNS = {
        "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
        "Jupiter": 4, "Venus": 12, "Saturn": 7
    }
    
    # نشان‌های هبوط (Debilitation Signs)
    DEBILITATION_SIGNS = {
        "Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12,
        "Jupiter": 10, "Venus": 6, "Saturn": 1
    }
    
    # نشان‌های خودی (Own Signs)
    OWN_SIGNS = {
        "Sun": [5], "Moon": [4], "Mars": [1, 8], "Mercury": [3, 6],
        "Jupiter": [9, 12], "Venus": [2, 7], "Saturn": [10, 11]
    }

    @staticmethod
    def get_house_lord(sign_num: int) -> str:
        return YogaEngine.RULERS.get(sign_num, "Unknown")

    @staticmethod
    def check_yogas(planets: Dict[str, Any], ascendant_long: float) -> List[Dict[str, str]]:
        detected_yogas = []
        
        # Pre-process Data
        p_data = {}
        asc_sign = int(ascendant_long / 30) + 1
        
        for name, data in planets.items():
            sign = int(data.longitude / 30) + 1
            # House relative to Ascendant
            house = (sign - asc_sign) % 12 + 1
            if house <= 0: house += 12
            
            p_data[name] = {
                "sign": sign,
                "house": house,
                "lord": YogaEngine.get_house_lord(sign),
                "obj": data
            }

        # --- 1. PANCHA MAHAPURUSHA YOGAS (The 5 Great Men) ---
        # Rule: Mars/Merc/Jup/Ven/Sat in Own or Exalted sign AND in Kendra (1,4,7,10) from Asc.
        
        # A. Ruchaka (Mars)
        if "Mars" in p_data:
            m = p_data["Mars"]
            if m["house"] in [1, 4, 7, 10]:
                if m["sign"] in [1, 8] or m["sign"] == 10: # Own or Exalted
                    detected_yogas.append({"name": "Ruchaka Yoga", "description": "Mars in strength in Kendra. Courageous, strong, born leader."})

        # B. Bhadra (Mercury)
        if "Mercury" in p_data:
            m = p_data["Mercury"]
            if m["house"] in [1, 4, 7, 10]:
                if m["sign"] in [3, 6]: # Own/Exalted (Virgo is both)
                    detected_yogas.append({"name": "Bhadra Yoga", "description": "Mercury in strength in Kendra. Intelligent, good speaker, long life."})

        # C. Hamsa (Jupiter)
        if "Jupiter" in p_data:
            j = p_data["Jupiter"]
            if j["house"] in [1, 4, 7, 10]:
                if j["sign"] in [9, 12] or j["sign"] == 4:
                    detected_yogas.append({"name": "Hamsa Yoga", "description": "Jupiter in strength in Kendra. Wisdom, virtue, spiritual nature."})

        # D. Malavya (Venus)
        if "Venus" in p_data:
            v = p_data["Venus"]
            if v["house"] in [1, 4, 7, 10]:
                if v["sign"] in [2, 7] or v["sign"] == 12:
                    detected_yogas.append({"name": "Malavya Yoga", "description": "Venus in strength in Kendra. Wealth, luxury, artistic talent, happiness."})

        # E. Sasa (Saturn)
        if "Saturn" in p_data:
            s = p_data["Saturn"]
            if s["house"] in [1, 4, 7, 10]:
                if s["sign"] in [10, 11] or s["sign"] == 7:
                    detected_yogas.append({"name": "Sasa Yoga", "description": "Saturn in strength in Kendra. Authority, discipline, leadership over masses."})

        # --- 2. COMMON YOGAS ---
        
        # Gaja Kesari (Jupiter in Kendra from Moon)
        if "Moon" in p_data and "Jupiter" in p_data:
            moon_sign = p_data["Moon"]["sign"]
            jup_sign = p_data["Jupiter"]["sign"]
            dist = (jup_sign - moon_sign) % 12
            if dist in [0, 3, 6, 9]: # 1, 4, 7, 10
                detected_yogas.append({"name": "Gaja Kesari Yoga", "description": "Jupiter in Kendra from Moon. Fame, virtue, intelligence."})

        # Budhaditya (Sun + Mercury)
        if p_data["Sun"]["sign"] == p_data["Mercury"]["sign"]:
             detected_yogas.append({"name": "Budhaditya Yoga", "description": "Sun and Mercury conjunction. Intelligence and skill in work."})

        # Chandra Mangala (Moon + Mars)
        if p_data["Moon"]["sign"] == p_data["Mars"]["sign"]:
             detected_yogas.append({"name": "Chandra Mangala Yoga", "description": "Moon and Mars conjunction. Financial success but potential aggression."})

        # --- 3. PARIVARTANA YOGA (Exchange of Signs) ---
        # Check every pair
        planets_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        checked_pairs = []
        
        for p1 in planets_list:
            for p2 in planets_list:
                if p1 == p2 or {p1, p2} in checked_pairs: continue
                
                # Logic: P1 is in P2's sign AND P2 is in P1's sign
                p1_sign = p_data[p1]["sign"]
                p2_sign = p_data[p2]["sign"]
                
                p1_lord = YogaEngine.get_house_lord(p1_sign)
                p2_lord = YogaEngine.get_house_lord(p2_sign)
                
                if p1_lord == p2 and p2_lord == p1:
                    # Determine type (Maha, Khala, Dainya) based on houses
                    h1 = p_data[p1]["house"]
                    h2 = p_data[p2]["house"]
                    
                    is_dusthana = (h1 in [6, 8, 12]) or (h2 in [6, 8, 12])
                    
                    yoga_name = "Maha Parivartana Yoga"
                    desc = "Exchange of lords of good houses. Great success."
                    
                    if is_dusthana:
                        # If both are dusthana lords (e.g. 6th and 8th exchange) -> Vipareeta (Good)
                        if (h1 in [6,8,12]) and (h2 in [6,8,12]):
                             yoga_name = "Vipareeta Parivartana"
                             desc = "Exchange between bad houses. Success after struggle."
                        else:
                             yoga_name = "Dainya/Khala Parivartana"
                             desc = "Exchange involving a bad house (6,8,12). Mixed results, fluctuations."
                             
                    detected_yogas.append({"name": f"{yoga_name} ({p1}-{p2})", "description": desc})
                    checked_pairs.append({p1, p2})

        # --- 4. VIPAREETA RAJA YOGA (VRY) ---
        # Lords of 6, 8, 12 placed in 6, 8, 12 (and not conjunct other lords preferably, simplified here)
        dusthana_lords = []
        for h in [6, 8, 12]:
            sign_on_h = (asc_sign + h - 2) % 12 + 1
            lord = YogaEngine.get_house_lord(sign_on_h)
            dusthana_lords.append(lord)
            
        # Check if 6th lord is in 6, 8, 12
        lord_6 = dusthana_lords[0]
        if p_data[lord_6]["house"] in [6, 8, 12]:
             detected_yogas.append({"name": "Harsha Vipareeta Raja Yoga", "description": "6th Lord in 6/8/12. Health, fame, winning over enemies."})
             
        lord_8 = dusthana_lords[1]
        if p_data[lord_8]["house"] in [6, 8, 12]:
             detected_yogas.append({"name": "Sarala Vipareeta Raja Yoga", "description": "8th Lord in 6/8/12. Longevity, fearlessness, wealth."})
             
        lord_12 = dusthana_lords[2]
        if p_data[lord_12]["house"] in [6, 8, 12]:
             detected_yogas.append({"name": "Vimala Vipareeta Raja Yoga", "description": "12th Lord in 6/8/12. Savings, good conduct, happiness."})

        # --- 5. KEMADRUMA YOGA ---
        # No planets in 2nd and 12th from Moon (excluding Sun, Rahu, Ketu)
        moon_sign = p_data["Moon"]["sign"]
        prev_sign = (moon_sign - 2) % 12 + 1 # 12th from Moon
        next_sign = (moon_sign) % 12 + 1     # 2nd from Moon
        
        has_planet_prev = False
        has_planet_next = False
        
        for p in planets_list:
            if p == "Moon" or p == "Sun": continue
            s = p_data[p]["sign"]
            if s == prev_sign: has_planet_prev = True
            if s == next_sign: has_planet_next = True
            
        if not has_planet_prev and not has_planet_next:
            # Cancel check: If Moon in Kendra from Asc or Planets in Kendra from Moon (Simplified: Just declare it exists)
            detected_yogas.append({"name": "Kemadruma Yoga", "description": "No planets 2nd/12th from Moon. Mental unrest or loneliness (check cancellations)."})

        return detected_yogas
