import swisseph as swe
from datetime import datetime, timedelta
from typing import List, Dict, Any
from phoenix_engine.vedic.const import SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU


class TransitCalculator:
    """
    ماشین حساب ترانزیت (Gochar) با استاندارد JHora.
    خروجی‌ها شامل:
    - Longitude/Sign/Degree: برای محاسبات Ashtakavarga و Kakshya.
    - Nakshatra: برای تحلیل Tara Bala.
    - Speed: برای تشخیص حرکت بازگشتی (Retrograde).
    """
    
    PLANET_IDS = {
        "Sun": SUN, "Moon": MOON, "Mars": MARS, "Mercury": MERCURY,
        "Jupiter": JUPITER, "Venus": VENUS, "Saturn": SATURN,
        "Rahu": RAHU, "Ketu": KETU
    }

    @staticmethod
    def get_nakshatra(lon: float) -> Dict[str, Any]:
        """محاسبه ناکشاترا برای منطق تارا بالا (Tara Bala)"""
        nak_len = 13.333333333
        idx = int(lon / nak_len)  # 0 to 26
        rem_deg = lon % nak_len
        pada_len = 3.333333333
        pada = int(rem_deg / pada_len) + 1
        
        return {
            "id": idx + 1,
            "pada": pada,
            "percent": (rem_deg / nak_len) * 100
        }

    @staticmethod
    def get_daily_transits(start_date: datetime, days_count: int = 30) -> List[Dict[str, Any]]:
        """
        تولید داده‌های سری زمانی (Time Series) برای آنالیز Gochar.
        """
        results = []
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        current_date = start_date
        
        for _ in range(days_count):
            jd = swe.julday(current_date.year, current_date.month, current_date.day, 12.0)
            
            daily_snapshot = {
                "date": current_date.strftime("%Y-%m-%d"),
                "timestamp": current_date.timestamp(),
                "planets": {}
            }
            
            for p_name, p_id in TransitCalculator.PLANET_IDS.items():
                flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
                
                if p_name == "Ketu":
                    rahu_res = swe.calc_ut(jd, RAHU, flags)
                    lon = (rahu_res[0][0] + 180.0) % 360.0
                    speed = rahu_res[0][3]
                else:
                    res = swe.calc_ut(jd, p_id, flags)
                    lon = res[0][0]
                    speed = res[0][3]
                
                sign_id = int(lon / 30.0) + 1
                degree_in_sign = lon % 30.0
                nak_info = TransitCalculator.get_nakshatra(lon)
                
                daily_snapshot["planets"][p_name] = {
                    "longitude": round(lon, 6),
                    "sign": sign_id,
                    "degree": round(degree_in_sign, 6),
                    "nakshatra": nak_info,
                    "speed": speed,
                    "is_retro": speed < 0
                }
            
            results.append(daily_snapshot)
            current_date += timedelta(days=1)
            
        return results

    @staticmethod
    def detect_ingress(daily_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        شناسایی تغییر نشان (Ingress) برای تحلیل‌های مورتی (Murti).
        """
        events = []
        if len(daily_data) < 2:
            return events
        
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

        prev_day = daily_data[0]
        
        for i in range(1, len(daily_data)):
            curr_day = daily_data[i]
            
            for p_name in TransitCalculator.PLANET_IDS.keys():
                if p_name == "Moon":
                    continue 
                
                prev_sign = prev_day["planets"][p_name]["sign"]
                curr_sign = curr_day["planets"][p_name]["sign"]
                
                if prev_sign != curr_sign:
                    events.append({
                        "date": curr_day["date"],
                        "planet": p_name,
                        "type": "Ingress",
                        "from": sign_names[prev_sign - 1],
                        "to": sign_names[curr_sign - 1],
                        "sign_id": curr_sign
                    })
            
            prev_day = curr_day
            
        return events
