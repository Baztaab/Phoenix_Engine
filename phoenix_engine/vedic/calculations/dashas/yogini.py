from typing import Dict, List, Any
from datetime import timedelta


class YoginiDashaEngine:
    YOGINIS = [
        {"name": "Mangala",  "duration": 1, "ruler": "Moon"},
        {"name": "Pingala",  "duration": 2, "ruler": "Sun"},
        {"name": "Dhanya",   "duration": 3, "ruler": "Jupiter"},
        {"name": "Bhramari", "duration": 4, "ruler": "Mars"},
        {"name": "Bhadrika", "duration": 5, "ruler": "Mercury"},
        {"name": "Ulka",     "duration": 6, "ruler": "Saturn"},
        {"name": "Siddha",   "duration": 7, "ruler": "Venus"},
        {"name": "Sankata",  "duration": 8, "ruler": "Rahu"}
    ]

    @staticmethod
    def calculate(moon_lon: float, birth_date: Any) -> List[Dict]:
        nak_raw = moon_lon / 13.333333333
        nak_index = int(nak_raw) + 1
        passed_percent = nak_raw % 1
        remaining_percent = 1.0 - passed_percent
        
        # JHora Logic: (Nak Index + 3) % 8. If 0 -> 8.
        start_idx_raw = (nak_index + 3) % 8
        start_idx = 8 if start_idx_raw == 0 else start_idx_raw
        list_idx = start_idx - 1
        
        start_yogini = YoginiDashaEngine.YOGINIS[list_idx]
        balance_years = start_yogini["duration"] * remaining_percent
        
        dashas = []
        current_date = birth_date
        
        # First Dasha
        days_balance = int(balance_years * 365.256363)  # Sidereal year
        end_date = current_date + timedelta(days=days_balance)
        
        dashas.append({
            "lord": start_yogini["name"],
            "ruler": start_yogini["ruler"],
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(balance_years, 2)
        })
        current_date = end_date
        
        # Next cycles (Full life ~100 years)
        for i in range(1, 12):
            next_idx = (list_idx + i) % 8
            y = YoginiDashaEngine.YOGINIS[next_idx]
            dur = y["duration"]
            days = int(dur * 365.256363)
            end_date = current_date + timedelta(days=days)
            
            dashas.append({
                "lord": y["name"],
                "ruler": y["ruler"],
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "duration_years": dur
            })
            current_date = end_date
            
        return dashas
