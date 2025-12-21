
from datetime import datetime, timedelta
from typing import Dict, List, Any
import copy

class DashaEngine:
    """
    محاسبه پیشرفته ویمشوتاری داشا (تا ۳ سطح: Maha, Antar, Pratyantar)
    """
    
    DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    DASHA_YEARS = {
        "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, 
        "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
    }
    TOTAL_CYCLE = 120

    @staticmethod
    def _get_sub_periods(main_lord: str, start_date: datetime, main_duration: float, level: int) -> List[Dict]:
        """تابع بازگشتی برای تولید زیر-دوره‌ها"""
        if level > 3: 
            return []

        sub_periods = []
        current_date = start_date
        
        start_idx = DashaEngine.DASHA_LORDS.index(main_lord)
        ordered_lords = DashaEngine.DASHA_LORDS[start_idx:] + DashaEngine.DASHA_LORDS[:start_idx]
        
        for sub_lord in ordered_lords:
            sub_duration_years = (main_duration * DashaEngine.DASHA_YEARS[sub_lord]) / 120.0
            days = sub_duration_years * 365.2425
            end_date = current_date + timedelta(days=days)
            
            period_data = {
                "lord": sub_lord,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "duration_years": round(sub_duration_years, 4),
                "level": level,
                "sub_periods": [] 
            }
            
            sub_periods.append(period_data)
            current_date = end_date
            
        return sub_periods

    @staticmethod
    def calculate_vimshottari_nested(moon_longitude: float, birth_date: datetime) -> List[Dict]:
        """محاسبه درخت کامل داشاها (فقط سطح ۲ برای همه)"""
        
        # --- FIX: حذف تایم زون برای مقایسه یکدست ---
        # ما فقط با تاریخ سر و کار داریم، ساعت و منطقه زمانی در مقیاس سالانه داشا مهم نیستند
        birth_naive = birth_date.replace(tzinfo=None)
        # -------------------------------------------

        nak_span = 13.333333333
        nak_index_float = moon_longitude / nak_span
        nak_index = int(nak_index_float)
        passed_fraction = nak_index_float - nak_index
        remaining_fraction = 1.0 - passed_fraction
        
        first_lord_idx = nak_index % 9
        first_lord = DashaEngine.DASHA_LORDS[first_lord_idx]
        
        full_years_first = DashaEngine.DASHA_YEARS[first_lord]
        balance_years = full_years_first * remaining_fraction
        spent_years = full_years_first - balance_years
        
        # استفاده از تاریخ Naive
        theoretical_start = birth_naive - timedelta(days=spent_years * 365.2425)
        
        dashas = []
        current_date_theoretical = theoretical_start
        
        for _ in range(2): 
            for i in range(9):
                curr_lord_idx = (first_lord_idx + i) % 9
                lord = DashaEngine.DASHA_LORDS[curr_lord_idx]
                duration = DashaEngine.DASHA_YEARS[lord]
                
                end_date = current_date_theoretical + timedelta(days=duration * 365.2425)
                
                # مقایسه: Naive با Naive (ایمن شد)
                if end_date > birth_naive:
                    real_start = max(birth_naive, current_date_theoretical)
                    
                    antardashas = DashaEngine._get_sub_periods(lord, current_date_theoretical, duration, 2)
                    
                    # فیلتر کردن و مقایسه ایمن
                    valid_antars = []
                    for ad in antardashas:
                        ad_end = datetime.strptime(ad['end'], "%Y-%m-%d")
                        if ad_end > birth_naive:
                            valid_antars.append(ad)

                    # اصلاح شروع اولین آنترداشای معتبر
                    if valid_antars and valid_antars[0]['start'] < birth_naive.strftime("%Y-%m-%d"):
                         valid_antars[0]['start'] = birth_naive.strftime("%Y-%m-%d")

                    dasha_entry = {
                        "lord": lord,
                        "start": real_start.strftime("%Y-%m-%d"),
                        "end": end_date.strftime("%Y-%m-%d"),
                        "duration_years": duration,
                        "level": 1,
                        "sub_periods": valid_antars
                    }
                    dashas.append(dasha_entry)
                
                current_date_theoretical = end_date
                if len(dashas) >= 15: break
            if len(dashas) >= 15: break

        return dashas

    @staticmethod
    def get_current_chain(all_dashas: List[Dict], target_date: datetime) -> List[Dict]:
        """پیدا کردن زنجیره دقیق زمان حال (Maha > Antar > Pratyantar)"""
        t_str = target_date.strftime("%Y-%m-%d")
        chain = []
        
        # 1. Find Maha Dasha
        maha = None
        for d in all_dashas:
            if d['start'] <= t_str < d['end']:
                maha = d
                break
        
        if not maha: return []
        chain.append({k:v for k,v in maha.items() if k != 'sub_periods'})
        
        # 2. Find Antar Dasha
        antar = None
        if 'sub_periods' in maha and maha['sub_periods']:
            for ad in maha['sub_periods']:
                if ad['start'] <= t_str < ad['end']:
                    antar = ad
                    break
        
        if antar:
            chain.append({k:v for k,v in antar.items() if k != 'sub_periods'})
            
            # 3. Calculate Pratyantar (Level 3) - On-the-fly calculation
            antar_lord = antar['lord']
            antar_duration = antar['duration_years']
            antar_start = datetime.strptime(antar['start'], "%Y-%m-%d")
            
            pratyantars = DashaEngine._get_sub_periods(antar_lord, antar_start, antar_duration, 3)
            
            for pd in pratyantars:
                if pd['start'] <= t_str < pd['end']:
                    chain.append(pd)
                    break
                    
        return chain
