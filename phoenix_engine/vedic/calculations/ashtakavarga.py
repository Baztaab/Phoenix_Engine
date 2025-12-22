from typing import Dict, List, Any


class AshtakavargaEngine:
    """
    موتور محاسبه Ashtakavarga طبق استانداردهای JHora.
    شامل: BAV, SAV, Trikona Sodhana, Ekadhipatya Sodhana, Shodhya Pinda.
    """
    
    POINTS_DATA = {
        "Sun": [
            [1,2,4,7,8,9,10,11], [3,6,10,11], [1,2,4,7,8,9,10,11], [3,5,6,9,10,11,12],
            [5,6,9,11], [6,7,12], [1,2,4,7,8,9,10,11], [3,4,6,10,11,12]
        ],
        "Moon": [
            [3,6,7,8,10,11], [1,3,6,7,9,10,11], [2,3,5,6,10,11], [1,3,4,5,7,8,10,11],
            [1,2,4,7,8,10,11], [3,4,5,7,9,10,11], [3,5,6,11], [3,6,10,11]
        ],
        "Mars": [
            [3,5,6,10,11], [3,6,11], [1,2,4,7,8,10,11], [3,5,6,11],
            [6,10,11,12], [6,8,11,12], [1,4,7,8,9,10,11], [1,3,6,10,11]
        ],
        "Mercury": [
            [5,6,9,11,12], [2,4,6,8,10,11], [1,2,4,7,8,9,10,11], [1,3,5,6,9,10,11,12],
            [6,8,11,12], [1,2,3,4,5,8,9,11], [1,2,4,7,8,9,10,11], [1,2,4,6,8,10,11]
        ],
        "Jupiter": [
            [1,2,3,4,7,8,9,10,11], [2,5,7,9,11], [1,2,4,7,8,10,11], [1,2,4,5,6,9,10,11],
            [1,2,3,4,7,8,10,11], [2,5,6,9,10,11], [3,5,6,12], [1,2,4,5,6,7,9,10,11]
        ],
        "Venus": [
            [8,11,12], [1,2,3,4,5,8,9,11,12], [3,4,6,9,11,12], [3,5,6,9,11],
            [5,8,9,10,11], [1,2,3,4,5,8,9,10,11], [3,4,5,8,9,10,11], [1,2,3,4,5,8,9,11]
        ],
        "Saturn": [
            [1,2,4,7,8,10,11], [3,6,11], [3,5,6,10,11,12], [6,8,9,10,11,12],
            [5,6,11,12], [6,11,12], [3,5,6,11], [1,3,4,6,10,11]
        ]
    }

    PLANETS_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    RASI_MULTIPLIERS = [7, 10, 8, 4, 10, 6, 7, 8, 9, 5, 11, 12]
    GRAHA_MULTIPLIERS = [5, 5, 8, 5, 10, 7, 5]

    @staticmethod
    def calculate_bav(planets: Dict[str, Any], asc_sign: int) -> Dict[str, List[int]]:
        bav_results = {}
        positions = []
        refs = AshtakavargaEngine.PLANETS_ORDER + ["Ascendant"]
        
        for p in refs:
            if p == "Ascendant":
                positions.append(asc_sign)
            else:
                positions.append(planets[p].sign)

        for p_name in AshtakavargaEngine.PLANETS_ORDER:
            points = [0] * 12
            rules = AshtakavargaEngine.POINTS_DATA[p_name]
            for ref_idx, houses in enumerate(rules):
                ref_sign = positions[ref_idx]
                for h_offset in houses:
                    target_sign_idx = (ref_sign + h_offset - 2) % 12
                    points[target_sign_idx] += 1
            bav_results[p_name] = points
            
        return bav_results

    @staticmethod
    def calculate_sav(bav: Dict[str, List[int]]) -> List[int]:
        sav = [0] * 12
        for p_name in AshtakavargaEngine.PLANETS_ORDER:
            p_bav = bav[p_name]
            for i in range(12):
                sav[i] += p_bav[i]
        return sav

    @staticmethod
    def _trikona_sodhana(bav_list: List[int]) -> List[int]:
        reduced = list(bav_list)
        groups = [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
        
        for group in groups:
            vals = [reduced[i] for i in group]
            m = min(vals)
            if vals[0] == vals[1] == vals[2]:
                for i in group:
                    reduced[i] = 0
            elif m > 0:
                for i in group:
                    reduced[i] -= m
                 
        return reduced

    @staticmethod
    def _ekadhipatya_sodhana(bav_list: List[int], planets_in_signs: Dict[int, List[str]]) -> List[int]:
        reduced = list(bav_list)
        pairs = [(0, 7), (1, 6), (2, 5), (8, 11), (9, 10)]
        
        for r1, r2 in pairs:
            val1 = reduced[r1]
            val2 = reduced[r2]
            if val1 == 0 and val2 == 0:
                continue
            occ1 = len(planets_in_signs.get(r1 + 1, [])) > 0
            occ2 = len(planets_in_signs.get(r2 + 1, [])) > 0
            
            if not occ1 and not occ2:
                if val1 == val2:
                    reduced[r1] = 0
                    reduced[r2] = 0
                else:
                    m = min(val1, val2)
                    reduced[r1] = m
                    reduced[r2] = m
            elif occ1 and not occ2:
                if val2 < val1:
                    reduced[r2] = 0
                else:
                    reduced[r2] = val1
            elif not occ1 and occ2:
                if val1 < val2:
                    reduced[r1] = 0
                else:
                    reduced[r1] = val2
        return reduced

    @staticmethod
    def calculate_sodhita_and_pinda(bav_raw: Dict[str, List[int]], planets: Dict[str, Any]) -> Dict[str, Any]:
        planets_in_signs = {}
        for p_name, p_data in planets.items():
            if p_name in ["Rahu", "Ketu"]:
                continue
            s = p_data.sign
            planets_in_signs.setdefault(s, []).append(p_name)
            
        results = {}
        
        for p_name, vals in bav_raw.items():
            after_trikona = AshtakavargaEngine._trikona_sodhana(vals)
            after_ekadhipatya = AshtakavargaEngine._ekadhipatya_sodhana(after_trikona, planets_in_signs)
            
            rasi_pinda = 0
            for i in range(12):
                rasi_pinda += after_ekadhipatya[i] * AshtakavargaEngine.RASI_MULTIPLIERS[i]
                
            graha_pinda = 0
            for g_idx, g_name in enumerate(AshtakavargaEngine.PLANETS_ORDER):
                g_sign = planets[g_name].sign
                points_at_sign = after_ekadhipatya[g_sign - 1]
                mult = AshtakavargaEngine.GRAHA_MULTIPLIERS[g_idx]
                graha_pinda += points_at_sign * mult
                
            shodhya_pinda = rasi_pinda + graha_pinda
            
            results[p_name] = {
                "sodhita": after_ekadhipatya,
                "rasi_pinda": rasi_pinda,
                "graha_pinda": graha_pinda,
                "shodhya_pinda": shodhya_pinda
            }
            
        return results
