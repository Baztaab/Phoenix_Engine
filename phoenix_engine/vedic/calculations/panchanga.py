import math
from typing import Dict, Any, Tuple
from phoenix_engine.infrastructure.astronomy.swiss import SwissEphemeris
from phoenix_engine.vedic.calculations.vedic_math import VedicMath


class PanchangaEngine:
    
    YOGAS = [
        "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", "Sukarma", "Dhriti", 
        "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", 
        "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", 
        "Brahma", "Indra", "Vaidhriti"
    ]

    KARANAS = [
        "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"
    ]
    
    FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

    WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    @staticmethod
    def calculate_panchanga(jd: float, sun_lon: float, moon_lon: float, sunrise_jd: float) -> Dict[str, Any]:
        """
        محاسبه کامل ۵ عضو زمان: Tithi, Vara, Nakshatra, Yoga, Karana
        به همراه Ishta Kala (Ghatis).
        """
        
        # 1. Tithi (lunar day)
        # Distance between Sun and Moon / 12 degrees
        diff = (moon_lon - sun_lon) % 360
        tithi_float = diff / 12.0
        tithi_index = int(tithi_float) + 1  # 1-30
        
        # Paksha (Fortnight)
        paksha = "Shukla" if tithi_index <= 15 else "Krishna"
        tithi_name = f"{paksha} {tithi_index if tithi_index <= 15 else tithi_index - 15}"
        tithi_left = (1.0 - (tithi_float % 1)) * 100 # Percentage left

        # 2. Nakshatra (Constellation)
        # Moon longitude / 13.3333 degrees
        nak_float = moon_lon / 13.333333
        nak_index = int(nak_float) + 1 # 1-27
        nak_left = (1.0 - (nak_float % 1)) * 100

        # 3. Yoga (Sun + Moon)
        # (Sun + Moon) / 13.3333 degrees
        yoga_sum = (sun_lon + moon_lon) % 360
        yoga_float = yoga_sum / 13.333333
        yoga_index = int(yoga_float) # 0-26
        yoga_name = PanchangaEngine.YOGAS[yoga_index % 27]
        yoga_left = (1.0 - (yoga_float % 1)) * 100

        # 4. Karana (Half-Tithi) - The JHora Logic
        # Each Tithi has 2 Karanas (6 degrees each)
        karana_float = diff / 6.0
        k_index = int(karana_float) + 1 # 1-60
        
        karana_name = ""
        # Logic adapted from JHora/Standard Vedic:
        if k_index == 1:
            karana_name = "Kimstughna"
        elif k_index >= 58:
            if k_index == 58: karana_name = "Shakuni"
            elif k_index == 59: karana_name = "Chatushpada"
            elif k_index == 60: karana_name = "Naga"
        else:
            # Repeating cycle of 7 movable karanas
            # Adjust index to skip Kimstughna (1)
            adjusted_idx = (k_index - 2) % 7
            karana_name = PanchangaEngine.KARANAS[adjusted_idx]
            
        karana_left = (1.0 - (karana_float % 1)) * 100

        # 5. Vara (Weekday)
        # JD + 1.5 % 7 gives weekday (0=Sunday)
        vara_idx = int(jd + 1.5) % 7
        vara_name = PanchangaEngine.WEEKDAYS[vara_idx]

        # 6. Vedic Time (Ghatis) - Ishta Kala
        # Requires Sunrise JD.
        # If sunrise calc failed (0.0), use placeholder
        if sunrise_jd > 0:
            ghatis, ghatis_str = VedicMath.time_diff_to_ghati(jd, sunrise_jd)
        else:
            ghatis, ghatis_str = 0.0, "N/A"

        return {
            "tithi": {
                "index": tithi_index,
                "name": tithi_name,
                "left_percent": round(tithi_left, 2)
            },
            "nakshatra": {
                "index": nak_index,
                "left_percent": round(nak_left, 2)
            },
            "yoga": {
                "name": yoga_name,
                "left_percent": round(yoga_left, 2)
            },
            "karana": {
                "name": karana_name,
                "left_percent": round(karana_left, 2)
            },
            "vara": vara_name,
            "vedic_time": {
                "ghatis": round(ghatis, 4),
                "text": ghatis_str
            }
        }

    # --- Compatibility helpers for existing plugins ---
    @staticmethod
    def calculate_tithi(sun_long: float, moon_long: float) -> Dict[str, Any]:
        diff = (moon_long - sun_long) % 360
        tithi_idx = int(diff / 12)
        paksha = "Shukla" if tithi_idx < 15 else "Krishna"
        return {
            "index": tithi_idx + 1,
            "name": f"{paksha} {tithi_idx + 1 if tithi_idx < 15 else tithi_idx - 14}",
            "paksha": paksha,
            "degrees_left": 12 - (diff % 12)
        }

    @staticmethod
    def calculate_nakshatra(moon_long: float) -> Dict[str, Any]:
        nak_float = moon_long / 13.333333
        idx = int(nak_float)
        completion = (moon_long % (360/27)) / (360/27) * 100
        pada = int((moon_long % (360/27)) / (360/27/4)) + 1
        return {
            "index": idx + 1,
            "completion": completion,
            "pada": pada
        }

    @staticmethod
    def calculate_yoga(sun_long: float, moon_long: float) -> Dict[str, Any]:
        total = (moon_long + sun_long) % 360
        idx = int(total / (360/27))
        return {
            "index": idx + 1,
            "name": PanchangaEngine.YOGAS[idx % 27]
        }

    @staticmethod
    def calculate_vara(jd: float) -> Dict[str, Any]:
        day_idx = int(jd + 1.5) % 7
        rulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        return {"day": PanchangaEngine.WEEKDAYS[day_idx], "ruler": rulers[day_idx]}
