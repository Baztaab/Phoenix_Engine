
from typing import Dict, List, Union

class VargaEngine:
    """
    موتور محاسبات کامل ۱۶ چارت پاراشارا (Shodashavarga)
    """

    @staticmethod
    def get_sign(longitude: float) -> int:
        return int(longitude / 30) + 1

    @staticmethod
    def normalize_sign(sign: int) -> int:
        return (sign - 1) % 12 + 1

    # --- D1: Rasi (Body) ---
    @staticmethod
    def calculate_d1(longitude: float) -> int:
        return VargaEngine.get_sign(longitude)

    # --- D2: Hora (Wealth) ---
    @staticmethod
    def calculate_d2_hora(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        is_odd = (sign % 2 != 0)
        first_half = (degree < 15)
        # Parashara Hora: Odd->Sun(5),Moon(4); Even->Moon(4),Sun(5)
        if is_odd: return 5 if first_half else 4
        else: return 4 if first_half else 5

    # --- D3: Drekkana (Siblings) ---
    @staticmethod
    def calculate_d3_drekkana(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 10) # 0,1,2
        return VargaEngine.normalize_sign(sign + (part * 4))

    # --- D4: Chaturthamsa (Destiny/Assets) ---
    @staticmethod
    def calculate_d4_chaturthamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/4)) # 0,1,2,3
        # Starts from sign itself, then 4th, 7th, 10th (Kendra logic)
        return VargaEngine.normalize_sign(sign + (part * 3))

    # --- D7: Saptamsa (Progeny) ---
    @staticmethod
    def calculate_d7_saptamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/7))
        start = sign if (sign % 2 != 0) else (sign + 6)
        return VargaEngine.normalize_sign(start + part)

    # --- D9: Navamsa (Marriage/Dharma) ---
    @staticmethod
    def calculate_d9_navamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/9))
        remainder = sign % 4
        start = 1 # Fire
        if remainder == 2: start = 10 # Earth
        elif remainder == 3: start = 7 # Air
        elif remainder == 0: start = 4 # Water
        return VargaEngine.normalize_sign(start + part)

    # --- D10: Dasamsa (Career) ---
    @staticmethod
    def calculate_d10_dasamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 3)
        start = sign if (sign % 2 != 0) else (sign + 8)
        return VargaEngine.normalize_sign(start + part)

    # --- D12: Dwadasamsa (Parents) ---
    @staticmethod
    def calculate_d12_dwadasamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 2.5)
        return VargaEngine.normalize_sign(sign + part)

    # --- D16: Shodasamsa (Vehicles/Happiness) ---
    @staticmethod
    def calculate_d16_shodasamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/16))
        # Moveable(1,4,7,10)->Aries(1); Fixed(2,5,8,11)->Leo(5); Dual(3,6,9,12)->Sag(9)
        rem = sign % 3
        start = 1
        if rem == 2: start = 5  # Fixed
        elif rem == 0: start = 9 # Dual
        return VargaEngine.normalize_sign(start + part)

    # --- D20: Vimsamsa (Spirituality) ---
    @staticmethod
    def calculate_d20_vimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/20))
        # Moveable->Aries(1); Fixed->Sag(9); Dual->Leo(5) (Note: Fixed/Dual swap compared to D16)
        rem = sign % 3
        start = 1
        if rem == 2: start = 9  # Fixed starts from Sagittarius
        elif rem == 0: start = 5 # Dual starts from Leo
        return VargaEngine.normalize_sign(start + part)

    # --- D24: Chaturvimsamsa (Education) ---
    @staticmethod
    def calculate_d24_chaturvimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/24))
        # Odd->Leo(5); Even->Cancer(4)
        start = 5 if (sign % 2 != 0) else 4
        return VargaEngine.normalize_sign(start + part)

    # --- D27: Saptavimsamsa (Strengths) ---
    @staticmethod
    def calculate_d27_saptavimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/27))
        # Fire->Aries(1); Earth->Cancer(4); Air->Libra(7); Water->Cap(10)
        rem = sign % 4
        start = 1
        if rem == 2: start = 4
        elif rem == 3: start = 7
        elif rem == 0: start = 10
        return VargaEngine.normalize_sign(start + part)

    # --- D30: Trimsamsa (Misfortunes) ---
    @staticmethod
    def calculate_d30_trimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        is_odd = (sign % 2 != 0)
        
        # Parashara Logic (Based on degrees, not equal parts)
        if is_odd:
            if degree <= 5: return 1   # Mars
            elif degree <= 10: return 11 # Saturn
            elif degree <= 18: return 9  # Jupiter
            elif degree <= 25: return 3  # Mercury
            else: return 7             # Venus
        else:
            if degree <= 5: return 2   # Venus
            elif degree <= 12: return 6  # Mercury
            elif degree <= 20: return 12 # Jupiter
            elif degree <= 25: return 10 # Saturn
            else: return 8             # Mars

    # --- D40: Khavedamsa (Auspicousness) ---
    @staticmethod
    def calculate_d40_khavedamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/40))
        # Odd->Aries(1); Even->Libra(7)
        start = 1 if (sign % 2 != 0) else 7
        return VargaEngine.normalize_sign(start + part)

    # --- D45: Akshavedamsa (Character) ---
    @staticmethod
    def calculate_d45_akshavedamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30/45))
        # Moveable->Aries(1); Fixed->Leo(5); Dual->Sag(9)
        rem = sign % 3
        start = 1
        if rem == 2: start = 5
        elif rem == 0: start = 9
        return VargaEngine.normalize_sign(start + part)

    # --- D60: Shashtyamsa (Past Karma) ---
    @staticmethod
    def calculate_d60_shashtyamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 0.5)
        return VargaEngine.normalize_sign(sign + part)

    @staticmethod
    def compute_vargas(longitudes: Dict[str, float]) -> Dict[str, Dict[str, int]]:
        result = {}
        for body, lng in longitudes.items():
            result[body] = {
                "D1": VargaEngine.calculate_d1(lng),
                "D2": VargaEngine.calculate_d2_hora(lng),
                "D3": VargaEngine.calculate_d3_drekkana(lng),
                "D4": VargaEngine.calculate_d4_chaturthamsa(lng),   # New
                "D7": VargaEngine.calculate_d7_saptamsa(lng),
                "D9": VargaEngine.calculate_d9_navamsa(lng),
                "D10": VargaEngine.calculate_d10_dasamsa(lng),
                "D12": VargaEngine.calculate_d12_dwadasamsa(lng),
                "D16": VargaEngine.calculate_d16_shodasamsa(lng),   # New
                "D20": VargaEngine.calculate_d20_vimsamsa(lng),     # New
                "D24": VargaEngine.calculate_d24_chaturvimsamsa(lng), # New
                "D27": VargaEngine.calculate_d27_saptavimsamsa(lng),  # New
                "D30": VargaEngine.calculate_d30_trimsamsa(lng),
                "D40": VargaEngine.calculate_d40_khavedamsa(lng),     # New
                "D45": VargaEngine.calculate_d45_akshavedamsa(lng),   # New
                "D60": VargaEngine.calculate_d60_shashtyamsa(lng)
            }
        return result
