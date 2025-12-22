import sys
import os
import requests
import urllib3
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo
from types import SimpleNamespace

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # Silence SSL warnings

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
    print(f"🦅  PHOENIX ENGINE V13 (LITE CLI)")
    print(f"=========================================={Colors.ENDC}")

# --- 1. GEOCODING ---
def get_location():
    print(f"\n{Colors.CYAN}[1] LOCATION SETUP{Colors.ENDC}")
    while True:
        query = input(f"{Colors.BOLD}   City Name (e.g. Tehran): {Colors.ENDC}").strip()
        if not query: continue
        
        try:
            # FIX: Added User-Agent and verify=False to bypass VPN/Proxy SSL issues
            headers = {'User-Agent': 'Mozilla/5.0 (PhoenixEngine V13)'}
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"
            
            # Increased timeout to 10s
            res = requests.get(url, headers=headers, timeout=10, verify=False).json()
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

# --- 2. BIRTH DATA ---
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

# --- 3. CONFIGURATION (SIMPLIFIED) ---
def get_config():
    print(f"\n{Colors.CYAN}[3] ASTROLOGY SETTINGS{Colors.ENDC}")
    
    # 3.1 AYANAMSA
    print(f"\n   {Colors.BOLD}Select Ayanamsa:{Colors.ENDC}")
    print("   1. Lahiri (Chitra Paksha) [Default]")
    print("   2. Raman")
    print("   3. KP (Krishnamurti)")
    print("   4. Tropical (Western)")
    
    ayan_choice = input(f"   Choice [1]: ").strip() or '1'
    ayan_map = {'1': "LAHIRI", '2': "RAMAN", '3': "KP", '4': "TROPICAL"}
    selected_ayanamsa = ayan_map.get(ayan_choice, "LAHIRI")

    # 3.2 HOUSE SYSTEM
    print(f"\n   {Colors.BOLD}Select House System:{Colors.ENDC}")
    print("   1. Placidus [Default]")
    print("   2. Whole Sign (Vedic Traditional)")
    print("   3. Equal House")
    print("   4. Porphyry")
    
    house_choice = input(f"   Choice [1]: ").strip() or '1'
    house_map = {'1': "PLACIDUS", '2': "WHOLE_SIGN", '3': "EQUAL", '4': "PORPHYRY"}
    selected_house = house_map.get(house_choice, "PLACIDUS")

    # 3.3 DASHA SYSTEM
    print(f"\n   {Colors.BOLD}Select Dasha System:{Colors.ENDC}")
    print("   1. Vimshottari [Default]")
    print("   2. Chara (K.N. Rao)")
    
    dasha_choice = input(f"   Choice [1]: ").strip() or '1'
    dasha_map = {'1': ["VIMSHOTTARI"], '2': ["CHARA_KNR"]}
    selected_dashas = dasha_map.get(dasha_choice, ["VIMSHOTTARI"])

    # 3.4 AUTOMATIC FULL OUTPUT
    output_conf = SimpleNamespace(
        include_doshas=True,
        include_vargas=True,
        include_shadbala=True,
        include_yogas=True,
        include_ashtakavarga=True,
        include_panchanga=True,
        include_dasa=True,
        include_jaimini=True,
        include_maitri=True,
        include_aspects=True,
        include_avasthas=True,
        include_bhavabala=True,
        include_phala=True,
        include_ishta_kashta=True,
        include_semantics=False,
        include_transit=False
    )
    
    return SimpleNamespace(
        ayanamsa=selected_ayanamsa,
        house_system=selected_house,
        dashas=selected_dashas,
        output=output_conf,
        calculation=SimpleNamespace(
            ayanamsa_mode=selected_ayanamsa,
            house_system=selected_house
        )
    )

# --- MAIN EXECUTION ---
def main():
    print_header()
    
    # Inputs
    city = get_location()
    dt = get_datetime(city['timezone'])
    config = get_config()
    
    print(f"\n{Colors.GREEN}🚀 Initializing Phoenix Engine...{Colors.ENDC}")
    
    try:
        from phoenix_engine.engines.birth import BirthChartEngine
        
        engine = BirthChartEngine(
            dt, 
            city['latitude'], 
            city['longitude'], 
            config=config
        )
        
        result = engine.process()
        data = result.dict()
        
        # --- REPORT SUMMARY ---
        print_header()
        print(f"{Colors.HEADER}🔮 CHART SUMMARY: {city['name'].upper()}{Colors.ENDC}")
        print(f"   Time: {dt}")
        print(f"   Settings: {config.ayanamsa} | {config.house_system} | {config.dashas[0]}")
        print("-" * 50)
        
        # 1. Ascendant
        print(f"{Colors.BOLD}➤ Ascendant:{Colors.ENDC} {data['ascendant']:.2f}°")
        
        # 2. Planets
        # FIX: Changed 'grahas' to 'planets' and 'lon' to 'longitude'
        print(f"\n{Colors.BOLD}{'PLANET':<10} {'LON':<8} {'SIGN':<10} {'HOUSE':<5} {'R'}{Colors.ENDC}")
        for p, d in data['planets'].items():
            retro = "Rx" if d['is_retrograde'] else ""
            print(f"{p:<10} {d['longitude']:.2f}{'':<4} {d['sign']:<10} {d['house']:<5} {retro}")

        # 3. Save
        filename = f"chart_{dt.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
        print(f"\n{Colors.BLUE}💾 Full calculations saved to:{Colors.ENDC}")
        print(f"   {Colors.BOLD}./{filename}{Colors.ENDC}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n{Colors.FAIL}❌ ENGINE ERROR: {e}{Colors.ENDC}")

if __name__ == "__main__":
    main()
