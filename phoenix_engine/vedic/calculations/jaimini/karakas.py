from typing import Dict, List, Any


class KarakaEngine:
    """
    محاسبه Chara Karakas (شاخص‌های متغیر) با منطق JHora.
    """
    
    # 7 Karaka Scheme (K.N. Rao - Default in JHora)
    # Order: Atma, Amatya, Bhratru, Matru, Putra, Gnati, Dara
    KARAKA_NAMES_7 = ["Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka", 
                      "Putrakaraka", "Gnatikaraka", "Darakaraka"]
    
    # 8 Karaka Scheme (Parashara)
    # Order: Atma, Amatya, Bhratru, Matru, Pitri, Putra, Gnati, Dara
    KARAKA_NAMES_8 = ["Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka", 
                      "Pitrikaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"]

    @staticmethod
    def calculate_chara_karakas(planets: Dict[str, Any], use_8_karakas: bool = False) -> Dict[str, str]:
        candidates = []
        
        planet_list = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        if use_8_karakas:
            planet_list.append("Rahu")
            
        for p_name in planet_list:
            if p_name in planets:
                p_data = planets[p_name]
                deg = p_data.degree
                
                # Rahu advancement: count from 30 downwards
                if p_name == "Rahu":
                    deg = 30.0 - deg
                    
                candidates.append({"name": p_name, "degree": deg})
        
        candidates.sort(key=lambda x: x["degree"], reverse=True)
        
        karaka_map = {}
        names = KarakaEngine.KARAKA_NAMES_8 if use_8_karakas else KarakaEngine.KARAKA_NAMES_7
        
        count = min(len(candidates), len(names))
        for i in range(count):
            role = names[i]
            p_name = candidates[i]["name"]
            karaka_map[role] = p_name
            
            short_code = ""
            if role == "Atmakaraka": short_code = "AK"
            elif role == "Amatyakaraka": short_code = "AmK"
            elif role == "Bhratrukaraka": short_code = "BK"
            elif role == "Matrukaraka": short_code = "MK"
            elif role == "Pitrikaraka": short_code = "PiK"
            elif role == "Putrakaraka": short_code = "PK"
            elif role == "Gnatikaraka": short_code = "GK"
            elif role == "Darakaraka": short_code = "DK"
            
            if short_code:
                karaka_map[short_code] = p_name
            
        return karaka_map
