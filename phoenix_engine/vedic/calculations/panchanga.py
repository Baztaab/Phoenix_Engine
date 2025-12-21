
class PanchangaEngine:
    """
    محاسبه ۵ رکن زمان (Panchanga): Vara, Tithi, Nakshatra, Yoga, Karana
    """
    
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    TITHIS = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", 
        "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", 
        "Trayodashi", "Chaturdashi", "Purnima", 
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", 
        "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", 
        "Trayodashi", "Chaturdashi", "Amavasya" 
    ]

    YOGAS = [
        "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", 
        "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", 
        "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", 
        "Brahma", "Indra", "Vaidhriti"
    ]

    @staticmethod
    def calculate_nakshatra(moon_long: float) -> dict:
        idx = int(moon_long / (360/27))
        percent = (moon_long % (360/27)) / (360/27) * 100
        pada = int((moon_long % (360/27)) / (360/27/4)) + 1
        return {
            "index": idx + 1,
            "name": PanchangaEngine.NAKSHATRAS[idx % 27],
            "pada": pada,
            "completion": percent
        }

    @staticmethod
    def calculate_tithi(sun_long: float, moon_long: float) -> dict:
        diff = (moon_long - sun_long) % 360
        tithi_idx = int(diff / 12)
        paksha = "Shukla" if tithi_idx < 15 else "Krishna"
        return {
            "index": tithi_idx + 1,
            "name": PanchangaEngine.TITHIS[tithi_idx],
            "paksha": paksha,
            "degrees_left": 12 - (diff % 12)
        }

    @staticmethod
    def calculate_yoga(sun_long: float, moon_long: float) -> dict:
        total = (moon_long + sun_long) % 360
        idx = int(total / (360/27))
        return {
            "index": idx + 1,
            "name": PanchangaEngine.YOGAS[idx % 27]
        }

    @staticmethod
    def calculate_vara(jd: float) -> dict:
        day_idx = int(jd + 1.5) % 7
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        rulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        return {"day": days[day_idx], "ruler": rulers[day_idx]}
