
from typing import Dict, Any

class PhalaEngine:
    "موتور محاسبه ایشتا و کاشتا فالا (Ishta & Kashta Phala)"
    
    @staticmethod
    def calculate(planets: Dict[str, Any], shadbala: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        results = {}
        
        for name, p in planets.items():
            if name in ["Rahu", "Ketu", "Ascendant"]: continue
            
            # فرمول‌های تقریبی بر اساس قدرت شادبالا و موقعیت (Ochcha Bala / Chesta Bala)
            # Ishta Phala ~ Uchcha Bala * Chesta Bala (Rooted)
            
            uchcha = 0.0
            chesta = 0.0
            
            if shadbala and name in shadbala:
                sb = shadbala[name]
                # استخراج از بریک‌داون شادبالا (اگر در دسترس باشد)
                # در مدل فعلی ما breakdown را داریم.
                uchcha = sb.breakdown['sthana'] * 60 # Approx mapping
                chesta = sb.breakdown['chesta'] * 60
            
            # فرمول استاندارد (Simplified):
            ishta = (uchcha + chesta) / 2.0
            kashta = 60.0 - ishta
            
            if ishta > 60: ishta = 60
            if kashta < 0: kashta = 0
            
            results[name] = {
                "ishta": round(ishta / 60.0 * 100, 1), # Percentage
                "kashta": round(kashta / 60.0 * 100, 1)
            }
            
        return results
