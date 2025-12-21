import sys
import os
import requests
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo
from types import SimpleNamespace

# افزودن مسیر جاری برای شناسایی موتور
sys.path.append(os.getcwd())

# --- رنگ‌بندی ترمینال ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.HEADER}==========================================")
    print(f"🦅  PHOENIX ENGINE V13 (PRO CLI)")
    print(f"=========================================={Colors.ENDC}")

# --- 1. GEOCODING (جستجوی شهر) ---
def get_location():
    print(f"\n{Colors.CYAN}[1] LOCATION SETUP{Colors.ENDC}")
    while True:
        query = input(f"{Colors.BOLD}   City Name (e.g. Tehran): {Colors.ENDC}").strip()
        if not query: continue
        
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
            res = requests.get(url, timeout=5).json()
            results = res.get("results", [])
            
            if not results:
                print(f"{Colors.WARNING}   ⚠️ No city found. Try again.{Colors.ENDC}")
                continue
                
            print(f"\n   {Colors.BLUE}Select City:{Colors.ENDC}")
            for i, r in enumerate(results):
                print(f"   {i+1}. {r['name']}, {r.get('country')} (TZ: {r.get('timezone')})")
            
            sel = input(f"\n{Colors.BOLD}   Enter Number: {Colors.ENDC}")
            if sel.isdigit() and 1 <= int(sel) <= len(results):
                return results[int(sel)-1]
        except Exception as e:
            print(f"{Colors.FAIL}   Error: {e}{Colors.ENDC}")

# --- 2. DATE & TIME ---
def get_datetime(tz_str):
    print(f"\n{Colors.CYAN}[2] BIRTH DATA{Colors.ENDC}")
    while True:
        d_str = input(f"   Date (YYYY-MM-DD): ").strip()
        t_str = input(f"   Time (HH:MM:SS): ").strip()
        try:
            dt_naive = datetime.strptime(f"{d_str} {t_str}", "%Y-%m-%d %H:%M:%S")
            tz = ZoneInfo(tz_str)
            return dt_naive.replace(tzinfo=tz)
        except ValueError:
            print(f"{Colors.WARNING}   ⚠️ Invalid format. Use 1990-05-21 and 14:30:00{Colors.ENDC}")

# --- 3. ADVANCED CONFIGURATION ---
def get_config():
    print(f"\n{Colors.CYAN}[3] ASTROLOGY SETTINGS{Colors.ENDC}")
    
    # --- AYANAMSA ---
    print(f"\n   {Colors.BOLD}Select Ayanamsa (Zodiac System):{Colors.ENDC}")
    print("   1. Lahiri (Chitra Paksha) [Standard Vedic]")
    print("   2. Raman")
    print("   3. Krishnamurti (KP)")
    print("   4. Tropical (Western/Sayana)")
    print("   5. Fagan-Bradley")
    
    ayan_map = {'1': 1, '2': 3, '3': 5, '4': 0, '5': 0} # 0 is generic/tropical fallback ID for swisseph
    ayan_choice = input(f"   Choice [Default=1]: ").strip() or '1'
    ayanamsa_id = ayan_map.get(ayan_choice, 1)

    # --- HOUSE SYSTEM ---
    print(f"\n   {Colors.BOLD}Select House System:{Colors.ENDC}")
    print("   1. Whole Sign (Rasi as House) [Ancient Vedic]")
    print("   2. Placidus [Modern/Western]")
    print("   3. Equal House")
    print("   4. Porphyry")
    
    house_map = {'1': 'W', '2': 'P', '3': 'E', '4': 'O'}
    house_choice = input(f"   Choice [Default=1]: ").strip() or '1'
    house_sys = house_map.get(house_choice, 'W')

    # --- OUTPUTS (DASHAS & MORE) ---
    print(f"\n   {Colors.BOLD}Output Options (y/n):{Colors.ENDC}")
    inc_dosha = input("   Include Doshas (Manglik/Kalasarpa)? [y]: ").lower() != 'n'
    inc_varga = input("   Include Vargas (D9, D60...)? [y]: ").lower() != 'n'
    inc_shad = input("   Include Shadbala (Strength)? [n]: ").lower() == 'y' # Default No to save time

    # ساخت آبجکت کانفیگ (دقت کن دیکشنری نیست، آبجکت است)
    # --- OUTPUT CONFIGURATION (ALL-INCLUSIVE FIX) ---
    # Defining ALL potential flags to satisfy strict engine checks
    output_conf = SimpleNamespace(
        # User Choices
        include_doshas=inc_dosha,
        include_vargas=inc_varga,
        include_shadbala=inc_shad,
        
        # Sub-Module Safety Flags (Must exist even if False)
        include_avasthas=True,       # Planetary States
        include_bhavabala=True,      # House Strength
        include_phala=True,          # Results/Fruits (The Fix)
        include_ishta_kashta=True,   # Ishta/Kashta Phala
        include_yogas=True,          # Yoga Combinations
        include_ashtakavarga=True,   # 8-Fold Strength
        include_panchanga=True,      # 5-Limbs of Time
        include_dasa=True,           # Dasha Systems
        include_transit=False        # Future proofing
    )
    
    calc_conf = SimpleNamespace(
        ayanamsa_mode=ayanamsa_id,
        house_system=house_sys
    )
    
    # بازگشت کانفیگ نهایی
    return SimpleNamespace(output=output_conf, calculation=calc_conf)

# --- MAIN EXECUTION ---
def main():
    print_header()
    
    # 1. Inputs
    city = get_location()
    dt = get_datetime(city['timezone'])
    config = get_config()
    
    print(f"\n{Colors.GREEN}🚀 Initializing Phoenix Engine...{Colors.ENDC}")
    
    try:
        from phoenix_engine.engines.birth import BirthChartEngine
        
        # Engine Call
        # ما کانفیگ را به موتور پاس می‌دهیم. اگر موتور تو هنوز کانفیگ 'calculation' را
        # پشتیبانی نمی‌کند، ممکن است نیاز باشد آن را در فایل موتور هم هندل کنی.
        # فعلاً فرض می‌کنیم موتور پارامتر config را کامل می‌گیرد.
        
        engine = BirthChartEngine(
            dt, 
            city['latitude'], 
            city['longitude'], 
            config=config
        )
        
        result = engine.process()
        data = result.dict()
        
        # --- REPORT ---
        print_header()
        print(f"{Colors.HEADER}🔮 REPORT FOR: {city['name'].upper()}{Colors.ENDC}")
        print(f"   Time: {dt}")
        print(f"   Ayanamsa ID: {config.calculation.ayanamsa_mode} | House: {config.calculation.house_system}")
        print("-" * 40)
        
        # Ascendant
        print(f"{Colors.BOLD}➤ Ascendant (Lagna):{Colors.ENDC} {data['ascendant']:.2f}°")
        
        # Planets Table
        print(f"\n{Colors.BOLD}{'PLANET':<10} {'LON':<10} {'SIGN':<10} {'HOUSE':<5} {'RETRO'}{Colors.ENDC}")
        print("-" * 50)
        for p, d in data['grahas'].items():
            retro = "Rx" if d['is_retrograde'] else ""
            print(f"{p:<10} {d['lon']:.2f}{'':<4} {d['sign']:<10} {d['house']:<5} {retro}")
            
        # Doshas
        if config.output.include_doshas:
            manglik = data.get('dosha', {}).get('manglik', {}).get('is_present')
            color = Colors.FAIL if manglik else Colors.GREEN
            print(f"\n{Colors.BOLD}🔥 Manglik Dosha:{Colors.ENDC} {color}{manglik}{Colors.ENDC}")
            
        # Save JSON
        filename = f"chart_{dt.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n{Colors.BLUE}💾 Full JSON saved to: {filename}{Colors.ENDC}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n{Colors.FAIL}❌ CRITICAL ERROR: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
