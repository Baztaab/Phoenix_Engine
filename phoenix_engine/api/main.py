
from datetime import datetime
from typing import Dict, Any
import json

from phoenix_engine.engines.birth import BirthChartEngine
from phoenix_engine.core.time_engine import localize_strict

def calculate_chart(
    year: int, month: int, day: int, 
    hour: int, minute: int, second: int, 
    timezone_str: str, 
    lat: float, lon: float
) -> Dict[str, Any]:
    """
    API اصلی برای محاسبه چارت تولد.
    خروجی به صورت دیکشنری (JSON-ready) است.
    """
    # 1. ساخت زمان دقیق
    dt = datetime(year, month, day, hour, minute, second)
    dt_aware = localize_strict(dt, timezone_str)
    
    # 2. ایجاد چارت
    chart = BirthChartEngine(dt_aware, lat, lon)
    result_model = chart.process()
    
    # 3. تبدیل به دیکشنری
    return result_model.model_dump()

if __name__ == "__main__":
    # تست سریع (Demo)
    print("🔮 Phoenix Engine V12.1 Demo...")
    result = calculate_chart(
        1997, 6, 7, 20, 28, 36, 
        "Asia/Tehran", 
        35.6892, 51.3890
    )
    
    # چاپ و ذخیره
    print(json.dumps(result, indent=2, ensure_ascii=False))
    with open("final_chart_v2.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print("\n✅ Generated 'final_chart_v2.json'")
