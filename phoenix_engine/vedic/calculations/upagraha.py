from typing import Dict, Any


class UpagrahaEngine:
    WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    GULIKA_INDICES = {"Sun": (7, 3), "Moon": (6, 2), "Mars": (5, 1), "Mercury": (4, 7), "Jupiter": (3, 6), "Venus": (2, 5), "Saturn": (1, 4)}
    MANDI_INDICES = {"Sun": (4, 8), "Moon": (3, 7), "Mars": (2, 6), "Mercury": (1, 5), "Jupiter": (8, 4), "Venus": (7, 3), "Saturn": (6, 2)}

    @staticmethod
    def calculate_sun_upagrahas(sun_lon: float) -> Dict[str, float]:
        dhooma = (sun_lon + 133.3333) % 360
        vyatipata = (360 - dhooma) % 360
        parivesha = (vyatipata + 180) % 360
        indra_chapa = (360 - parivesha) % 360
        upaketu = (indra_chapa + 16.6666) % 360
        return {"Dhooma": dhooma, "Vyatipata": vyatipata, "Parivesha": parivesha, "Indra Chapa": indra_chapa, "Upaketu": upaketu}

    @staticmethod
    def calculate_kalavela(jd: float, sunrise_jd: float, sunset_jd: float, weekday_idx: int) -> Dict[str, float]:
        # FIX: Prevents UnboundLocalError by initializing defaults
        start_jd = jd
        part_len = 0.0
        idx_tuple_idx = 0 
        
        if sunrise_jd == 0.0 or sunset_jd == 0.0:
            return {"Gulika_JD": jd, "Mandi_JD": jd}

        current_weekday = weekday_idx
        
        if jd < sunrise_jd:
            # Before Sunrise -> Belongs to Previous Vedic Night
            idx_tuple_idx = 1 # Night index
            current_weekday = (weekday_idx - 1) % 7
            start_jd = sunset_jd - 1.0 # Yesterday Sunset
            duration = sunrise_jd - start_jd
            part_len = duration / 8.0
        elif jd >= sunset_jd:
            # After Sunset -> Current Night
            idx_tuple_idx = 1
            start_jd = sunset_jd
            duration = (sunrise_jd + 1.0) - sunset_jd
            part_len = duration / 8.0
        else:
            # Day Time
            idx_tuple_idx = 0
            start_jd = sunrise_jd
            duration = sunset_jd - sunrise_jd
            part_len = duration / 8.0

        day_lord = UpagrahaEngine.WEEKDAY_LORDS[current_weekday]
        g_idx = UpagrahaEngine.GULIKA_INDICES[day_lord][idx_tuple_idx]
        gulika_start_time = start_jd + (g_idx - 1) * part_len
        
        m_idx = UpagrahaEngine.MANDI_INDICES[day_lord][idx_tuple_idx]
        mandi_start_time = start_jd + (m_idx - 1) * part_len
        
        return {"Gulika_JD": gulika_start_time, "Mandi_JD": mandi_start_time}
