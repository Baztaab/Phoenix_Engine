from typing import Dict, Any


class ArudhaEngine:
    """
    محاسبه Arudha Padas با قوانین استثنای JHora.
    """

    @staticmethod
    def get_lord_of_sign(sign_id: int, planets: Dict[str, Any]) -> int:
        """
        پیدا کردن حاکم نشان (با رعایت قوانین Sc و Aq).
        """
        rulers = {1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 5: "Sun", 6: "Mercury",
                  7: "Venus", 9: "Jupiter", 10: "Saturn", 12: "Jupiter"}
        
        if sign_id == 8:
            return planets["Mars"].sign if "Mars" in planets else sign_id
        if sign_id == 11:
            return planets["Saturn"].sign if "Saturn" in planets else sign_id
            
        p_name = rulers.get(sign_id)
        if p_name and p_name in planets:
            return planets[p_name].sign
        return sign_id

    @staticmethod
    def calculate_arudhas(asc_sign: int, planets: Dict[str, Any]) -> Dict[str, int]:
        arudhas = {}
        
        for house_num in range(1, 13):
            house_sign = asc_sign + house_num - 1
            if house_sign > 12:
                house_sign -= 12
            
            lord_sign = ArudhaEngine.get_lord_of_sign(house_sign, planets)
            
            dist = lord_sign - house_sign
            if dist < 0:
                dist += 12
            
            arudha_raw = lord_sign + dist
            while arudha_raw > 12:
                arudha_raw -= 12
            
            steps_from_house = arudha_raw - house_sign
            if steps_from_house < 0:
                steps_from_house += 12
            
            final_arudha = arudha_raw
            
            if steps_from_house == 0:
                final_arudha = arudha_raw + 9
            elif steps_from_house == 6:
                final_arudha = arudha_raw + 9
            
            while final_arudha > 12:
                final_arudha -= 12
            
            key = f"A{house_num}"
            if house_num == 1:
                key = "AL"
            if house_num == 12:
                key = "UL"
            
            arudhas[key] = final_arudha
            
            if house_num == 1:
                arudhas["A1"] = final_arudha
            if house_num == 12:
                arudhas["A12"] = final_arudha
            
        return arudhas
