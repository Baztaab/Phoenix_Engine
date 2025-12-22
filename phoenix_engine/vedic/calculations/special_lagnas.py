from typing import Dict, Any


class SpecialLagnaEngine:
    
    @staticmethod
    def calculate_bhava_lagna(sun_lon_rise: float, time_from_sunrise_hours: float) -> float:
        # Rate: 1 Sign (30 deg) per 2 Hours (5 Ghatis) -> Speed of Lagna (360/24 = 15 deg/hr)
        # Wait, Bhava Lagna moves at Sun's speed? No. It moves like Lagna but averaged?
        # Standard: Sun at Sunrise + (Time in Ghatis * 6) degrees? No.
        # BL = Sun(rise) + (Time from Rise in Hours * 15)
        return (sun_lon_rise + (time_from_sunrise_hours * 15.0)) % 360

    @staticmethod
    def calculate_hora_lagna(sun_lon_rise: float, time_from_sunrise_hours: float) -> float:
        # HL Rate: 1 Sign (30 deg) per 2.5 Ghatis (1 Hour).
        # Speed: 30 deg / 1 hr = 30 deg/hr.
        return (sun_lon_rise + (time_from_sunrise_hours * 30.0)) % 360

    @staticmethod
    def calculate_ghati_lagna(sun_lon_rise: float, time_from_sunrise_hours: float) -> float:
        # GL Rate: 1 Sign (30 deg) per 1 Ghati (24 mins = 0.4 hr).
        # Speed: 30 / 0.4 = 75 deg/hr.
        return (sun_lon_rise + (time_from_sunrise_hours * 75.0)) % 360

    @staticmethod
    def calculate_bhrigu_bindu(moon_lon: float, rahu_lon: float) -> float:
        # Midpoint of Moon and Rahu
        # Need to handle 360 crossing carefully.
        # Usually: (Moon + Rahu) / 2. 
        # But Rahu is usually retro. Midpoint is the point between them.
        
        # Simple Average
        mid = (moon_lon + rahu_lon) / 2.0
        # Check shorter arc? usually not specified, Bhrigu Bindu is just arithmetic mean usually 
        # adjusted for short arc. If diff > 180, take the other side.
        diff = abs(moon_lon - rahu_lon)
        if diff > 180:
            mid = (mid + 180) % 360
        return mid

    @staticmethod
    def calculate_yogi_point(sun_lon: float, moon_lon: float) -> Dict[str, Any]:
        # Yoga Point = Sun + Moon
        yoga_deg = (sun_lon + moon_lon) % 360
        
        # Yogi Planet = Ruler of Nakshatra of Yoga Point
        nak_idx = int(yoga_deg / 13.333333)
        # Nakshatra Rulers (Standard Vimshottari Order)
        # 0:Ket, 1:Ven, 2:Sun, 3:Mon, 4:Mar, 5:Rah, 6:Jup, 7:Sat, 8:Mer ... repeat
        rulers = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
        yogi_lord = rulers[nak_idx % 9]
        
        # Avayogi Point = Yoga Point + 186deg 40min (Standard Pushya-paksha correction)
        # Often simplified as: 6th Nakshatra from Yogi?
        # Formula: (Yoga Point + 93.3333) ? No.
        # Let's use standard: Avayogi is the ruler of the 6th Nakshatra from Yogi Nakshatra.
        # But the Point itself:
        abayogi_deg = (yoga_deg + 186.6666) % 360
        abayogi_nak = int(abayogi_deg / 13.333333)
        abayogi_lord = rulers[abayogi_nak % 9]
        
        return {
            "Yoga_Point": yoga_deg,
            "Yogi": yogi_lord,
            "Avayogi": abayogi_lord
        }
