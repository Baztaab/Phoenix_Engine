from typing import List, Dict, Any
from phoenix_engine.vedic.const import SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN


class GocharEngine:
    """
    موتور تحلیل ترانزیت هوشمند (Smart Vedic Transit Engine).
    اطلاعات را در 5 لایه (هویت، قدرت، مکان، اتصال، کیفیت) مپ می‌کند.
    """
    
    KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Ascendant"]
    
    HOUSE_TOPICS = {
        1: "Self/Health", 2: "Wealth/Family", 3: "Effort/Communication", 4: "Home/Mother",
        5: "Creativity/Children", 6: "Service/Enemies", 7: "Marriage/Partners", 8: "Transformation/Crisis",
        9: "Dharma/Luck", 10: "Career/Status", 11: "Gains/Network", 12: "Loss/Spirituality"
    }

    ASPECT_RULES = {
        "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
        "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
        "Rahu": [5, 7, 9], "Ketu": [5, 7, 9]
    }

    @staticmethod
    def _get_kakshya_lord(degree: float) -> str:
        idx = int(degree / 3.75)
        return GocharEngine.KAKSHYA_LORDS[min(idx, 7)]

    @staticmethod
    def _get_functional_nature(planet_name: str, asc_sign: int) -> str:
        rulers = {1:"Mars", 2:"Venus", 3:"Mercury", 4:"Moon", 5:"Sun", 6:"Mercury", 
                  7:"Venus", 8:"Mars", 9:"Jupiter", 10:"Saturn", 11:"Saturn", 12:"Jupiter"}
        
        owned_houses = []
        for h in range(1, 13):
            sign = (asc_sign + h - 2) % 12 + 1
            if rulers.get(sign) == planet_name:
                owned_houses.append(h)
                
        if not owned_houses:
            return "Neutral"
        
        is_trine_lord = any(h in [1, 5, 9] for h in owned_houses)
        is_dusthana_lord = any(h in [6, 8, 12] for h in owned_houses)
        
        if is_trine_lord:
            return "Functional Benefic"
        if is_dusthana_lord and not is_trine_lord:
            return "Functional Malefic"
        return "Neutral/Mixed"

    @staticmethod
    def _calculate_tara_bala(transit_nak: int, moon_nak: int) -> Dict[str, Any]:
        if not moon_nak:
            return {"score": 0, "status": "Unknown"}
        
        dist = (transit_nak - moon_nak)
        if dist < 0:
            dist += 27
        tara_num = (dist % 9) + 1
        
        tara_map = {
            1: "Janma (Birth) - Medium",
            2: "Sampat (Wealth) - Good",
            3: "Vipat (Danger) - Bad",
            4: "Kshema (Well-being) - Good",
            5: "Pratyak (Obstacles) - Bad",
            6: "Sadhana (Achievement) - Very Good",
            7: "Naidhana (Destruction) - Very Bad",
            8: "Mitra (Friend) - Good",
            9: "Parama Mitra (Best Friend) - Excellent"
        }
        
        desc = tara_map.get(tara_num, "Neutral")
        score = 1 if tara_num in [2,4,6,8,9] else -1 if tara_num in [3,5,7] else 0
        
        return {"type": tara_num, "desc": desc, "score": score}

    @staticmethod
    def analyze_smart_series(
        transit_series: List[Dict], 
        natal_chart: Dict[str, Any], 
        asc_sign: int, 
        sav_data: List[int],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        analyzed_timeline = []
        
        karakas = context.get('karakas', {})
        active_lords = context.get('active_dasha_lords', [])
        planet_to_karaka = {v: k for k, v in karakas.items()}
        
        natal_moon = natal_chart.get("Moon")
        moon_nak = int(natal_moon.nakshatra_id) if hasattr(natal_moon, 'nakshatra_id') else 0
        moon_sign = natal_moon.sign

        for day_data in transit_series:
            date = day_data["date"]
            daily_insights = {"date": date, "global_score": 0, "planets": {}}
            daily_total_score = 0
            
            for p_name, t_info in day_data["planets"].items():
                if p_name in ["Rahu", "Ketu"]:
                    continue
                
                func_nature = GocharEngine._get_functional_nature(p_name, asc_sign)
                karaka_role = planet_to_karaka.get(p_name, "")
                is_dasha_lord = p_name in active_lords
                
                sign_idx = t_info["sign"] - 1
                sav = sav_data[sign_idx]
                kakshya_lord = GocharEngine._get_kakshya_lord(t_info["degree"])
                
                h_from_lagna = (t_info["sign"] - asc_sign + 12) % 12 + 1 if asc_sign else 0
                h_from_moon = (t_info["sign"] - moon_sign + 12) % 12 + 1
                
                t_nak = t_info["nakshatra"]["id"]
                tara_info = GocharEngine._calculate_tara_bala(t_nak, moon_nak)
                
                aspects_to_houses = []
                if p_name in GocharEngine.ASPECT_RULES:
                    for aspect_dist in GocharEngine.ASPECT_RULES[p_name]:
                        target_h = (h_from_lagna + aspect_dist - 1) % 12 + 1
                        topic = GocharEngine.HOUSE_TOPICS.get(target_h, "")
                        aspects_to_houses.append(f"H{target_h} ({topic})")
                
                base_score = 0
                if sav >= 30:
                    base_score += 2
                elif sav < 20:
                    base_score -= 1
                
                if tara_info["score"] > 0:
                    base_score += 1
                elif tara_info["score"] < 0:
                    base_score -= 1
                
                final_score = base_score
                if is_dasha_lord:
                    final_score *= 1.5
                
                status_text = "Neutral"
                if final_score >= 3:
                    status_text = "Excellent"
                elif final_score >= 1:
                    status_text = "Good"
                elif final_score < 0:
                    status_text = "Challenging"
                
                planet_obj = {
                    "position": {
                        "sign": t_info["sign"],
                        "house_lagna": h_from_lagna,
                        "house_moon": h_from_moon,
                        "nakshatra": t_nak,
                        "is_retro": t_info["is_retro"]
                    },
                    "identity": {
                        "functional": func_nature,
                        "chara_karaka": karaka_role,
                        "is_dasha_lord": is_dasha_lord
                    },
                    "strength": {
                        "sav_points": sav,
                        "kakshya_lord": kakshya_lord
                    },
                    "quality": {
                        "tara_bala": tara_info.get("desc", "Unknown"),
                        "status_score": round(final_score, 1)
                    },
                    "network": {
                        "current_domain": GocharEngine.HOUSE_TOPICS.get(h_from_lagna, ""),
                        "aspects_hitting": aspects_to_houses
                    },
                    "summary": f"{p_name} ({func_nature}) in {GocharEngine.HOUSE_TOPICS.get(h_from_lagna,'')} aspecting {aspects_to_houses}"
                }
                
                daily_insights["planets"][p_name] = planet_obj
                daily_total_score += final_score
            
            daily_insights["global_score"] = round(daily_total_score, 1)
            analyzed_timeline.append(daily_insights)
            
        return {"daily_timeline": analyzed_timeline}
