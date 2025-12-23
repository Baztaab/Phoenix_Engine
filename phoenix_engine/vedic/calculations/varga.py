from typing import Dict, List, Union


class VargaEngine:
    """
    Advanced Shodashavarga Engine.
    Refactored by Kai to support JHora-standard variations (e.g., Kashinatha Hora).
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

    # --- D2: Hora (Wealth & Resources) ---
    @staticmethod
    def calculate_d2_parashara(longitude: float) -> int:
        """
        Standard Parashara Hora (Sun/Moon).
        Used primarily for planetary strength (Shadbala).
        Odd Signs: Sun (5), Moon (4)
        Even Signs: Moon (4), Sun (5)
        """
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        is_odd = (sign % 2 != 0)
        first_half = (degree < 15)

        if is_odd:
            return 5 if first_half else 4  # Sun then Moon
        else:
            return 4 if first_half else 5  # Moon then Sun

    @staticmethod
    def calculate_d2_kashinatha(longitude: float) -> int:
        """
        Kashinatha Hora.
        Used specifically for Wealth/Finance analysis in JHora.
        Odd Signs: 1st Half -> Sign itself; 2nd Half -> 12th from Sign.
        Even Signs: 1st Half -> 12th from Sign; 2nd Half -> Sign itself.
        """
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        is_odd = (sign % 2 != 0)
        first_half = (degree < 15)

        sign_12th = VargaEngine.normalize_sign(sign - 1)

        if is_odd:
            return sign if first_half else sign_12th
        else:
            return sign_12th if first_half else sign

    # --- D3: Drekkana (Siblings) ---
    @staticmethod
    def calculate_d3_drekkana(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 10)  # 0, 1, 2
        return VargaEngine.normalize_sign(sign + (part * 4))

    # --- D4: Chaturthamsa (Destiny/Assets) ---
    @staticmethod
    def calculate_d4_chaturthamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 7.5)  # 30/4 = 7.5
        return VargaEngine.normalize_sign(sign + (part * 3))

    # --- D7: Saptamsa (Progeny) ---
    @staticmethod
    def calculate_d7_saptamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30 / 7))
        start = sign if (sign % 2 != 0) else (sign + 6)
        return VargaEngine.normalize_sign(start + part)

    # --- D9: Navamsa (Marriage/Dharma) ---
    @staticmethod
    def calculate_d9_navamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30 / 9))

        remainder = sign % 4
        start = 1
        if remainder == 2:
            start = 10
        elif remainder == 3:
            start = 7
        elif remainder == 0:
            start = 4

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
        part = int(degree / (30 / 16))
        rem = sign % 3
        start = 1
        if rem == 2:
            start = 5
        elif rem == 0:
            start = 9
        return VargaEngine.normalize_sign(start + part)

    # --- D20: Vimsamsa (Spirituality) ---
    @staticmethod
    def calculate_d20_vimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 1.5)  # 30/20 = 1.5
        rem = sign % 3
        start = 1
        if rem == 2:
            start = 9
        elif rem == 0:
            start = 5
        return VargaEngine.normalize_sign(start + part)

    # --- D24: Chaturvimsamsa (Education) ---
    @staticmethod
    def calculate_d24_chaturvimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 1.25)  # 30/24
        start = 5 if (sign % 2 != 0) else 4
        return VargaEngine.normalize_sign(start + part)

    # --- D27: Saptavimsamsa (Strengths) ---
    @staticmethod
    def calculate_d27_saptavimsamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30 / 27))
        rem = sign % 4
        start = 1
        if rem == 2:
            start = 4
        elif rem == 3:
            start = 7
        elif rem == 0:
            start = 10
        return VargaEngine.normalize_sign(start + part)

    # --- D30: Trimsamsa (Misfortunes) ---
    @staticmethod
    def calculate_d30_trimsamsa(longitude: float) -> int:
        """
        Parashara Trimsamsa.
        Degrees are unequal and depend on Odd/Even signs.
        Lords: Mars, Saturn, Jupiter, Mercury, Venus.
        """
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        is_odd = (sign % 2 != 0)

        if is_odd:
            if degree <= 5:
                return 1
            elif degree <= 10:
                return 11
            elif degree <= 18:
                return 9
            elif degree <= 25:
                return 3
            else:
                return 7
        else:
            if degree <= 5:
                return 2
            elif degree <= 12:
                return 6
            elif degree <= 20:
                return 12
            elif degree <= 25:
                return 10
            else:
                return 8

    # --- D40: Khavedamsa ---
    @staticmethod
    def calculate_d40_khavedamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 0.75)  # 30/40
        start = 1 if (sign % 2 != 0) else 7
        return VargaEngine.normalize_sign(start + part)

    # --- D45: Akshavedamsa ---
    @staticmethod
    def calculate_d45_akshavedamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / (30 / 45))
        rem = sign % 3
        start = 1
        if rem == 2:
            start = 5
        elif rem == 0:
            start = 9
        return VargaEngine.normalize_sign(start + part)

    # --- D60: Shashtyamsa ---
    @staticmethod
    def calculate_d60_shashtyamsa(longitude: float) -> int:
        sign = VargaEngine.get_sign(longitude)
        degree = longitude % 30
        part = int(degree / 0.5)
        return VargaEngine.normalize_sign(sign + part)

    @staticmethod
    def compute_vargas(longitudes: Dict[str, float]) -> Dict[str, Dict[str, int]]:
        """
        Computes all Divisional Charts.
        Includes both Parashara D2 and Kashinatha D2.
        """
        result = {}
        for body, lng in longitudes.items():
            result[body] = {
                "D1": VargaEngine.calculate_d1(lng),
                "D2": VargaEngine.calculate_d2_parashara(lng),
                "D2_K": VargaEngine.calculate_d2_kashinatha(lng),
                "D3": VargaEngine.calculate_d3_drekkana(lng),
                "D4": VargaEngine.calculate_d4_chaturthamsa(lng),
                "D7": VargaEngine.calculate_d7_saptamsa(lng),
                "D9": VargaEngine.calculate_d9_navamsa(lng),
                "D10": VargaEngine.calculate_d10_dasamsa(lng),
                "D12": VargaEngine.calculate_d12_dwadasamsa(lng),
                "D16": VargaEngine.calculate_d16_shodasamsa(lng),
                "D20": VargaEngine.calculate_d20_vimsamsa(lng),
                "D24": VargaEngine.calculate_d24_chaturvimsamsa(lng),
                "D27": VargaEngine.calculate_d27_saptavimsamsa(lng),
                "D30": VargaEngine.calculate_d30_trimsamsa(lng),
                "D40": VargaEngine.calculate_d40_khavedamsa(lng),
                "D45": VargaEngine.calculate_d45_akshavedamsa(lng),
                "D60": VargaEngine.calculate_d60_shashtyamsa(lng),
            }
        return result
