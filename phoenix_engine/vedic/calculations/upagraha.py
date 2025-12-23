from typing import Dict, Tuple


class UpagrahaEngine:
    """
    Upagraha Calculation Engine (JHora Standard).
    Calculates:
    1. Non-Luminous Points based on Sun (Dhooma, Vyatipata, etc.)
    2. Time-based Points (Gulika, Mandi) - returns JD start times.
    """

    # 0=Sunday ... 6=Saturday
    WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    # Maps Day Lord -> (Day Segment Index, Night Segment Index)
    # Segments are 1-based (1 to 8)
    GULIKA_INDICES = {
        "Sun": (7, 3), "Moon": (6, 2), "Mars": (5, 1), "Mercury": (4, 7),
        "Jupiter": (3, 6), "Venus": (2, 5), "Saturn": (1, 4)
    }

    MANDI_INDICES = {
        "Sun": (4, 8), "Moon": (3, 7), "Mars": (2, 6), "Mercury": (1, 5),
        "Jupiter": (8, 4), "Venus": (7, 3), "Saturn": (6, 2)
    }

    @staticmethod
    def calculate_sun_upagrahas(sun_lon: float) -> Dict[str, float]:
        """Calculates longitude-based Upagrahas derived from Sun."""
        dhooma = (sun_lon + 133.3333) % 360
        vyatipata = (360 - dhooma) % 360
        parivesha = (vyatipata + 180) % 360
        indra_chapa = (360 - parivesha) % 360
        upaketu = (indra_chapa + 16.6666) % 360

        return {
            "Dhooma": dhooma,
            "Vyatipata": vyatipata,
            "Parivesha": parivesha,
            "Indra Chapa": indra_chapa,
            "Upaketu": upaketu
        }

    @staticmethod
    def calculate_kalavela_times(jd: float, sunrise_jd: float, sunset_jd: float, weekday_idx: int) -> Dict[str, float]:
        """
        Calculates the Julian Day (time) when the segment for Gulika/Mandi begins.
        The Longitude of Gulika/Mandi is the Ascendant at this specific time.
        """
        if sunrise_jd == 0.0 or sunset_jd == 0.0:
            return {"Gulika_JD": jd, "Mandi_JD": jd}

        # Day = Sunrise to Sunset. Night = Sunset to next Sunrise.
        is_day_birth = (jd >= sunrise_jd) and (jd < sunset_jd)

        start_jd = 0.0
        part_len = 0.0
        idx_tuple_pos = 0  # 0 for Day, 1 for Night

        if is_day_birth:
            idx_tuple_pos = 0
            start_jd = sunrise_jd
            duration = sunset_jd - sunrise_jd
            part_len = duration / 8.0
        else:
            idx_tuple_pos = 1
            if jd >= sunset_jd:
                start_jd = sunset_jd
                day_len = sunset_jd - sunrise_jd
                night_len = 1.0 - day_len  # approx
                part_len = night_len / 8.0
            else:
                # Before sunrise (belongs to previous Vedic night)
                start_jd = sunset_jd  # assumes caller passes correct sunset (prior)
                part_len = (sunrise_jd - (sunset_jd - 0.5)) / 8.0  # rough fix

        day_lord = UpagrahaEngine.WEEKDAY_LORDS[weekday_idx]

        g_idx = UpagrahaEngine.GULIKA_INDICES[day_lord][idx_tuple_pos]
        gulika_time = start_jd + (g_idx - 1) * part_len

        m_idx = UpagrahaEngine.MANDI_INDICES[day_lord][idx_tuple_pos]
        mandi_time = start_jd + (m_idx - 1) * part_len

        return {"Gulika_JD": gulika_time, "Mandi_JD": mandi_time}
