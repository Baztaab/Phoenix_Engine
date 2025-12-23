from typing import List, Dict, Any
from phoenix_engine.vedic.const import SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN


class GocharEngine:
    """
    موتور ترانزیت داده‌محور (Data-Driven Smart Gochar).
    شامل محاسبات لایه‌ای و یوگاهای ترانزیتی.
    """
    
    KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Ascendant"]
    
    HOUSE_TOPICS = {
        1: "Self/Health", 2: "Wealth/Family", 3: "Effort/Courage", 4: "Home/Peace",
        5: "Education/Progeny", 6: "Enemies/Debts", 7: "Spouse/Partnership", 8: "Longevity/Changes",
        9: "Luck/Dharma", 10: "Karma/Career", 11: "Gains/Income", 12: "Loss/Expenses"
    }

    @staticmethod
    def _check_transit_yogas(daily_planets: Dict[str, Dict[str, Any]]) -> List[str]:
        yogas = []
        signs = {p: data['sign'] for p, data in daily_planets.items() if p in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']}
        
        if 'Moon' in signs and 'Jupiter' in signs:
            dist = (signs['Jupiter'] - signs['Moon']) % 12
            if dist in [0, 3, 6, 9]:
                yogas.append("Gaja Kesari (Transit): Reputation & Success")

        if 'Sun' in signs and 'Mercury' in signs and signs['Sun'] == signs['Mercury']:
            yogas.append("Budhaditya (Transit): Intelligence & Communication")
                
        if 'Moon' in signs and 'Mars' in signs and signs['Moon'] == signs['Mars']:
            yogas.append("Chandra Mangala (Transit): Wealth & Earnings")

        if 'Jupiter' in signs and 'Mars' in signs:
            dist = (signs['Mars'] - signs['Jupiter']) % 12
            if dist in [0, 6]:
                yogas.append("Guru Mangala (Transit): High Energy & Leadership")

        return yogas

    @staticmethod
    def analyze_smart_series(
        transit_series: List[Dict], 
        natal_chart: Dict[str, Any], 
        asc_sign: int, 
        sav_data: List[int],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        timeline = []
        active_lords = context.get('active_dasha_lords', [])
        natal_moon_sign = natal_chart["Moon"].sign

        for day_data in transit_series:
            date = day_data["date"]
            active_yogas = GocharEngine._check_transit_yogas(day_data["planets"])
            
            day_snapshot = {
                "date": date,
                "timestamp": day_data.get("timestamp"),
                "global_yogas": active_yogas,
                "planets": {}
            }
            
            for p_name, t_info in day_data["planets"].items():
                if p_name in ["Rahu", "Ketu"]:
                    continue
                
                current_sign = t_info["sign"]
                h_lagna = (current_sign - asc_sign + 12) % 12 + 1
                h_moon = (current_sign - natal_moon_sign + 12) % 12 + 1
                
                sav_score = sav_data[current_sign - 1]
                kakshya_idx = int(t_info["degree"] / 3.75)
                kakshya_lord = GocharEngine.KAKSHYA_LORDS[min(kakshya_idx, 7)]
                
                planet_detail = {
                    "coordinates": {
                        "sign_id": current_sign,
                        "longitude": t_info["longitude"],
                        "degree_in_sign": t_info["degree"],
                        "speed": t_info["speed"],
                        "is_retrograde": t_info["is_retro"]
                    },
                    "nakshatra": t_info["nakshatra"],
                    "houses": {
                        "from_lagna": h_lagna,
                        "topic": GocharEngine.HOUSE_TOPICS.get(h_lagna, "General"),
                        "from_moon": h_moon
                    },
                    "strength": {
                        "sav_points": sav_score,
                        "kakshya_lord": kakshya_lord
                    },
                    "context": {
                        "is_dasha_lord": p_name in active_lords,
                        "functional_nature": "Benefic" if h_lagna in [1,5,9] else "Neutral"
                    }
                }
                
                day_snapshot["planets"][p_name] = planet_detail
            
            timeline.append(day_snapshot)
            
        return {"chronological_timeline": timeline}
