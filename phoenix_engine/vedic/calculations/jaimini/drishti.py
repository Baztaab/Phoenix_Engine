from typing import List, Dict, Any


class JaiminiDrishtiEngine:
    """
    موتور محاسبه نظرات راشی (Rashi Drishti) طبق قوانین JHora.
    """
    
    # نقشه نظرات (Source Sign ID -> List of Aspected Sign IDs)
    # 1-Based Indexing
    ASPECT_MAP = {
        # Movable (Chara)
        1: [5, 8, 11],   # Aries -> Leo, Scorpio, Aquarius (Not Taurus)
        4: [2, 8, 11],   # Cancer -> Taurus, Scorpio, Aquarius (Not Leo)
        7: [2, 5, 11],   # Libra -> Taurus, Leo, Aquarius (Not Scorpio)
        10: [2, 5, 8],   # Capricorn -> Taurus, Leo, Scorpio (Not Aquarius)
        
        # Fixed (Sthira)
        2: [4, 7, 10],   # Taurus -> Cancer, Libra, Capricorn (Not Aries)
        5: [1, 7, 10],   # Leo -> Aries, Libra, Capricorn (Not Cancer)
        8: [1, 4, 10],   # Scorpio -> Aries, Cancer, Capricorn (Not Libra)
        11: [1, 4, 7],   # Aquarius -> Aries, Cancer, Libra (Not Capricorn)
        
        # Dual (Dwiswabhava)
        3: [6, 9, 12],   # Gemini -> Virgo, Sag, Pisces
        6: [3, 9, 12],   # Virgo -> Gemini, Sag, Pisces
        9: [3, 6, 12],   # Sagittarius -> Gemini, Virgo, Pisces
        12: [3, 6, 9]    # Pisces -> Gemini, Virgo, Sagittarius
    }

    @staticmethod
    def get_aspected_signs(sign_id: int) -> List[int]:
        """لیست نشان‌هایی که توسط sign_id دیده می‌شوند."""
        return JaiminiDrishtiEngine.ASPECT_MAP.get(sign_id, [])

    @staticmethod
    def check_aspect(sign_a: int, sign_b: int) -> bool:
        """آیا نشان A به نشان B نظر دارد؟"""
        aspects = JaiminiDrishtiEngine.get_aspected_signs(sign_a)
        return sign_b in aspects

    @staticmethod
    def check_connection(p1_sign: int, p2_sign: int) -> str:
        """
        بررسی ارتباط بین دو نشان برای یوگا (Jaimini Sambandha).
        خروجی: "Conjunction" (قران), "Aspect" (نظر), یا None.
        """
        if p1_sign == p2_sign:
            return "Conjunction"
        
        if JaiminiDrishtiEngine.check_aspect(p1_sign, p2_sign):
            return "Aspect"
            
        return None
