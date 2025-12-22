from typing import Dict, List, Any
from phoenix_engine.vedic.calculations.dashas.chara import CharaDashaEngine


class NarayanaDashaEngine:
    """
    موتور محاسبه Narayana Dasha (General).
    منطق:
    1. شروع از قوی‌ترین بین Lagna و خانه 7.
    2. حرکت بر اساس ماهیت نشان (Chara/Sthira/Dwiswabhava).
    3. مدت زمان مشابه Chara Dasha (Lord position).
    """

    MOVABLE = [1, 4, 7, 10]      # Chara Rashi
    FIXED = [2, 5, 8, 11]        # Sthira Rashi
    DUAL = [3, 6, 9, 12]         # Dwiswabhava Rashi

    @staticmethod
    def get_planet_count_in_sign(sign_id: int, planets: Dict[str, Any]) -> int:
        count = 0
        for p_name, p_data in planets.items():
            if p_name in ["Rahu", "Ketu"]:
                continue
            if p_data.sign == sign_id:
                count += 1
        return count

    @staticmethod
    def get_stronger_sign(sign_a: int, sign_b: int, planets: Dict[str, Any]) -> int:
        """
        مقایسه قدرت دو نشان برای تعیین شروع داشا.
        قوانین (ساده شده):
        1. تعداد سیارات بیشتر.
        2. اگر مساوی بود، فعلاً A را برمی‌گردانیم (می‌توان توسعه داد).
        """
        count_a = NarayanaDashaEngine.get_planet_count_in_sign(sign_a, planets)
        count_b = NarayanaDashaEngine.get_planet_count_in_sign(sign_b, planets)
        
        if count_a > count_b:
            return sign_a
        if count_b > count_a:
            return sign_b
        return sign_a

    @staticmethod
    def get_progression_sequence(start_sign: int) -> List[int]:
        """
        تولید توالی 12 نشان بر اساس Padakrama ساده‌شده.
        """
        sequence = []
        current = start_sign
        
        is_movable = start_sign in NarayanaDashaEngine.MOVABLE
        is_fixed = start_sign in NarayanaDashaEngine.FIXED
        is_dual = start_sign in NarayanaDashaEngine.DUAL
        
        jump = 1
        if is_movable:
            jump = 1
        elif is_fixed:
            jump = 5
        elif is_dual:
            jump = 4
        
        direction = 1
        if start_sign % 2 == 0:
            direction = -1
        
        for _ in range(12):
            sequence.append(current)
            next_step = current + (jump * direction)
            while next_step > 12:
                next_step -= 12
            while next_step < 1:
                next_step += 12
            current = next_step
            
        return sequence

    @staticmethod
    def calculate(ascendant_sign: int, planets: Dict[str, Any], birth_date: Any) -> List[Dict]:
        dashas = []
        
        # 1. پیدا کردن نقطه شروع (Arambha)
        sign_1 = ascendant_sign
        sign_7 = ascendant_sign + 6
        if sign_7 > 12:
            sign_7 -= 12
        
        start_sign = NarayanaDashaEngine.get_stronger_sign(sign_1, sign_7, planets)
        
        # 2. تولید توالی نشان‌ها
        signs_seq = NarayanaDashaEngine.get_progression_sequence(start_sign)
        
        # 3. محاسبه داشاها
        current_date = birth_date
        sign_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                      "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for sign_id in signs_seq:
            lord_pos = CharaDashaEngine.get_stronger_lord(sign_id, planets)
            
            dist = (lord_pos - sign_id)
            if dist <= 0:
                dist += 12
            
            duration = dist - 1
            if duration == 0:
                duration = 12
            
            try:
                end_date = current_date.replace(year=current_date.year + duration)
            except ValueError:
                safe_date = current_date.replace(month=2, day=28)
                end_date = safe_date.replace(year=current_date.year + duration)
            
            dashas.append({
                "sign_id": sign_id,
                "sign_name": sign_names[sign_id - 1],
                "ruler_pos": lord_pos,
                "duration_years": duration,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            })
            
            current_date = end_date
            
        return dashas
