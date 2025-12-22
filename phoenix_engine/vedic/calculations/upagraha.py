from typing import Dict, Any
import math


class UpagrahaEngine:
    """
    محاسبه اجرام سایه‌ای (Upagrahas): Mandi, Gulika, etc.
    """
    
    # ترتیب اربابان روز (شروع از یکشنبه)
    WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    # قطعه مربوط به گولیکا (Gulika) و ماندی (Mandi) در روز/شب (8 قسمت)
    # فرمت: {Weekday_Lord: (Day_Index, Night_Index)} - 1-based index out of 8
    # Saturn's portion is Gulika. 
    # Gulika ruling start indices:
    # Sun: Day=7, Night=3 | Mon: Day=6, Night=2 ...
    # This is standard chart logic.
    GULIKA_INDICES = {
        "Sun": (7, 3), "Moon": (6, 2), "Mars": (5, 1), "Mercury": (4, 7),
        "Jupiter": (3, 6), "Venus": (2, 5), "Saturn": (1, 4)
    }
    
    # Mandi is usually slightly different or same depending on tradition.
    # JHora: Mandi rises at the MIDDLE of the Saturn portion? Or specific portion?
    # Standard: Mandi starts at: Sun: Day=4, Night=... 
    # Let's use Parashara Standard for Mandi:
    # Sun: D4, N8 | Mon: D3, N7 | Mar: D2, N6 | Mer: D1, N5 | Jup: D8, N4 | Ven: D7, N3 | Sat: D6, N2
    MANDI_INDICES = {
        "Sun": (4, 8), "Moon": (3, 7), "Mars": (2, 6), "Mercury": (1, 5),
        "Jupiter": (8, 4), "Venus": (7, 3), "Saturn": (6, 2)
    }

    @staticmethod
    def calculate_sun_upagrahas(sun_lon: float) -> Dict[str, float]:
        """
        Dhooma, Vyatipata, Parivesha, Indra Chapa, Upaketu
        """
        dhooma = (sun_lon + 133.3333) % 360 # +133 deg 20 min
        vyatipata = (360 - dhooma) % 360
        parivesha = (vyatipata + 180) % 360
        indra_chapa = (360 - parivesha) % 360
        upaketu = (indra_chapa + 16.6666) % 360 # +16 deg 40 min
        
        return {
            "Dhooma": dhooma,
            "Vyatipata": vyatipata,
            "Parivesha": parivesha,
            "Indra Chapa": indra_chapa,
            "Upaketu": upaketu
        }

    @staticmethod
    def calculate_kalavela(jd: float, sunrise_jd: float, sunset_jd: float, weekday_idx: int) -> Dict[str, float]:
        """
        محاسبه دقیق Mandi و Gulika بر اساس طول روز/شب
        """
        is_day = (sunrise_jd <= jd < sunset_jd)
        
        if is_day:
            start_jd = sunrise_jd
            duration = sunset_jd - sunrise_jd
            part_len = duration / 8.0
            idx_tuple_idx = 0 # Day index
        else:
            # Night logic: Sunset to Next Sunrise (Approx)
            # Simplified: Use sunset to sunrise (assuming 24h - day_len)
            # If jd is before sunrise (early morning), we are in previous night technically
            # This requires complex next-sunrise logic. 
            # Simplified V1: Assume constant night length for now or approx 12h
            # For high precision, we need next sunrise. Let's use Day Logic for robustness first.
            # Assume 30 ghatis approx if data missing, else calculated.
            duration = 0.5 # Default half day fallback
            if jd > sunset_jd: duration = (sunrise_jd + 1.0) - sunset_jd
            else: duration = sunrise_jd - (sunset_jd - 1.0)
            
            part_len = duration / 8.0
            idx_tuple_idx = 1 # Night index

        day_lord = UpagrahaEngine.WEEKDAY_LORDS[weekday_idx]
        
        # Gulika
        g_idx = UpagrahaEngine.GULIKA_INDICES[day_lord][idx_tuple_idx]
        # Gulika rises at the START of the segment (or end? Standard: Start)
        # JHora uses Start of segment + duration/2 (Middle)? No, usually Segment Start.
        # Let's use Segment Start time.
        gulika_start_time = start_jd + (g_idx - 1) * part_len
        
        # Mandi
        m_idx = UpagrahaEngine.MANDI_INDICES[day_lord][idx_tuple_idx]
        mandi_start_time = start_jd + (m_idx - 1) * part_len
        
        # Convert Time JD back to Ascendant Longitude
        # To get Longitude of Gulika, we calculate the Ascendant at Gulika's rising time.
        # We need to return the JD times, and the caller (Plugin) will calc Ascendant for these JDs.
        
        return {
            "Gulika_JD": gulika_start_time,
            "Mandi_JD": mandi_start_time
        }
