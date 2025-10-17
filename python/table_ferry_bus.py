#!/usr/bin/env python3
import requests
from datetime import datetime, timezone
import json

BASE = "https://v6.db.transport.rest"

# Ferry schedule: every hour at :05, :20, :35, :50
FERRY_MINUTES = [5, 20, 35, 50]

def find_stop_id(name):
    r = requests.get(f"{BASE}/locations", params={"query": name, "results": 1})
    r.raise_for_status()
    return r.json()[0]["id"]

def parse_time(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def get_bus_journeys(from_name, to_name, results=50):
    from_id = find_stop_id(from_name)
    to_id = find_stop_id(to_name)
    now_iso = datetime.now().isoformat(timespec="minutes")
    params = {
        "from": from_id,
        "to": to_id,
        "departure": now_iso,
        "results": results,
        "remarks": True,
        "polylines": False,
        "tickets": False,
        "products": {"bus": True},
    }
    r = requests.get(f"{BASE}/journeys", params=params)
    r.raise_for_status()
    return r.json().get("journeys", [])

def generate_ferry_schedule_for_day(reference_dt):
    ferry_times = []
    for hour in range(24):
        for minute in FERRY_MINUTES:
            ferry_dt = reference_dt.replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=reference_dt.tzinfo)
            ferry_times.append(ferry_dt)
    return ferry_times

def main():
    FROM = "Konstanz Allmannsdorf"
    TO = "Meersburg Kirche"

    journeys = get_bus_journeys(FROM, TO, results=50)
    if not journeys:
        print("No bus journeys found today.")
        return

    reference_dt = parse_time(journeys[0]["legs"][0]["departure"])
    ferry_schedule = generate_ferry_schedule_for_day(reference_dt)

    # Ferry -> list of buses
    ferry_map = {f_dt: [] for f_dt in ferry_schedule}

    for j in journeys:
        first_leg = j["legs"][0]
        last_leg = j["legs"][-1]
        bus_name = first_leg.get("line", {}).get("name") or first_leg.get("mode", "Bus")
        bus_dep = parse_time(first_leg["departure"])
        bus_arr = parse_time(last_leg["arrival"])
        origin_name = first_leg["origin"]["name"]
        dest_name = last_leg["destination"]["name"]
        bus_info = {
            "name": bus_name,
            "dep": bus_dep.strftime("%H:%M"),
            "arr": bus_arr.strftime("%H:%M"),
            "origin": origin_name,
            "destination": dest_name
        }

        for f_dt in ferry_map:
            if f_dt >= bus_dep:
                ferry_map[f_dt].append(bus_info)

    # Build JSON output with most_likely flag
    output = []
    for f_dt, buses in ferry_map.items():
        if buses:
            buses_sorted = sorted(buses, key=lambda b: b["dep"])
            for i, b in enumerate(buses_sorted):
                b["most_likely"] = (i == 0)
        output.append({
            "ferry_dep": f_dt.strftime("%H:%M"),
            "buses": buses_sorted if buses else []
        })

    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
