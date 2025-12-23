import json
from datetime import datetime

import pytz

from phoenix_engine.core.config import ChartConfig
from phoenix_engine.core.orchestrator import ChartOrchestrator
from phoenix_engine.utils.geolocation import resolve_city_wrapper


def save_output(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nOutput saved to: {filename}")


def main():
    print("Phoenix Engine - Professional CLI v2 (High Precision)")

    print("\n--- Phoenix Engine Input ---")
    name = input("Name: ") or "User"

    # City resolution
    while True:
        city_name = (input("City (Anywhere in the world): ") or "Tehran").strip()
        city_data = resolve_city_wrapper(city_name)
        if city_data:
            display_name = city_data.get("address", city_name.title())
            short_name = display_name.split(",")[0]
            print(f"   📍 Found: {short_name} | Lat: {city_data['lat']:.4f}, Lon: {city_data['lon']:.4f}")
            print(f"   🌐 Zone:  {city_data['tz']}")
            break
        print(f"   ❌ Could not locate '{city_name}'. Check spelling or internet connection.")

    date_str = input("Date (YYYY-MM-DD): ") or "1985-06-15"

    # Time with seconds support
    while True:
        time_input = input("Time (HH:MM:SS or HH:MM): ") or "12:00:00"
        parts = time_input.strip().split(":")
        if len(parts) == 2:
            time_str = f"{time_input}:00"
            break
        if len(parts) == 3:
            time_str = time_input
            break
        print("   Invalid format. Please use HH:MM or HH:MM:SS")

    tz = pytz.timezone(city_data["tz"])
    dt_str = f"{date_str} {time_str}"
    try:
        local_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        aware_dt = tz.localize(local_dt)
    except ValueError as e:
        print(f"   Date/Time Error: {e}")
        return

    print(f"   Local Time: {aware_dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f"   UTC Time:   {aware_dt.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")

    config = ChartConfig(ayanamsa="LAHIRI")
    orchestrator = ChartOrchestrator(config)

    print("\nSelect Output Mode:")
    print("1) Natal Intelligence JSON (Static Soul Map)")
    print("2) Smart Transit Timeline JSON (Dynamic Forecast + Yogas)")
    print("3) Varshaphal (Annual Solar Return Chart)")
    choice = input("Choice (1/2/3): ")

    if choice == "1":
        print("\nGenerating Natal Chart...")
        report = orchestrator.run_birth_chart(
            name,
            aware_dt.year,
            aware_dt.month,
            aware_dt.day,
            aware_dt.hour,
            aware_dt.minute,
            aware_dt.second,
            city_data["lat"],
            city_data["lon"],
            city_data["tz"],
        )
        report.pop("transits", None)
        save_output(f"{name}_natal.json", report)

    elif choice == "2":
        print("\nGenerating Smart Transit Timeline...")
        full_report = orchestrator.run_birth_chart(
            name,
            aware_dt.year,
            aware_dt.month,
            aware_dt.day,
            aware_dt.hour,
            aware_dt.minute,
            aware_dt.second,
            city_data["lat"],
            city_data["lon"],
            city_data["tz"],
        )

        transits = full_report.get("transits", {}) or {}
        transit_payload = {
            "meta": {
                "subject": name,
                "birth_time_used": aware_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "location": f"{city_data['lat']}, {city_data['lon']}",
                "timezone": str(aware_dt.tzinfo),
                "forecast_start": datetime.now().strftime("%Y-%m-%d"),
                "active_dasha": transits.get("meta", {}).get("active_dasha", []),
            },
            "events": transits.get("events", []),
            "timeline": transits.get("forecast", {}).get("chronological_timeline", []),
        }

        save_output(f"{name}_transit.json", transit_payload)
    elif choice == "3":
        target_year_str = input(f"Enter Target Year (Default {datetime.now().year}): ")
        target_year = int(target_year_str) if target_year_str else datetime.now().year

        print(f"\nGenerating Varshaphal for {target_year}...")
        annual_report = orchestrator.run_annual_forecast(
            name,
            aware_dt.year,
            aware_dt.month,
            aware_dt.day,
            aware_dt.hour,
            aware_dt.minute,
            aware_dt.second,
            city_data["lat"],
            city_data["lon"],
            target_year,
            city_data["tz"],
        )

        varsha_payload = annual_report.get("varshaphal", annual_report)
        save_output(f"{name}_varshaphal_{target_year}.json", varsha_payload)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
