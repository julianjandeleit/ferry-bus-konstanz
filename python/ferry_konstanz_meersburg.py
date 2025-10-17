#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

BASE = "https://v6.db.transport.rest"

# Example ferry departures for the day (hour:minute)
# You can adjust as needed
FERRY_SCHEDULE = [
    (5, 20), (5, 50), (6, 20), (6, 50), (7, 20), (7, 50),
    (8, 20), (8, 50), (9, 20), (9, 50), (10, 20), (10, 50),
    (11, 20), (11, 50), (12, 20), (12, 50), (13, 20), (13, 50),
    (14, 20), (14, 50), (15, 20), (15, 50), (16, 20), (16, 50),
    (17, 20), (17, 50), (18, 20), (18, 50), (19, 20), (19, 50)
]

def find_stop_id(name):
    r = requests.get(f"{BASE}/locations", params={"query": name, "results": 1})
    r.raise_for_status()
    data = r.json()
    return data[0]["id"]

def parse_time(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def fmt_duration(dep, arr):
    delta = arr - dep
    mins = int(delta.total_seconds() // 60)
    h, m = divmod(mins, 60)
    return f"{h}h {m:02d}m"

def get_bus_journeys(from_name, to_name, results=5):
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
        "products": {"bus": True},  # only bus
    }

    r = requests.get(f"{BASE}/journeys", params=params)
    r.raise_for_status()
    data = r.json()
    return data["journeys"]

def get_ferry_candidates(bus_start_dt):
    """Return all ferries >= bus start time; mark the first one."""
    ferry_times = []
    first_after = None
    for h, m in FERRY_SCHEDULE:
        ferry_dt = bus_start_dt.replace(hour=h, minute=m, second=0, microsecond=0)
        # if ferry already passed, skip or move to next day
        if ferry_dt < bus_start_dt:
            continue
        ferry_times.append(ferry_dt)
        if not first_after:
            first_after = ferry_dt
    return ferry_times, first_after

def print_journeys_with_ferry(journeys):
    for j in journeys:
        first_leg = j["legs"][0]
        last_leg = j["legs"][-1]
        dep = parse_time(first_leg["departure"])
        arr = parse_time(last_leg["arrival"])
        duration = fmt_duration(dep, arr)

        ferry_candidates, first_ferry = get_ferry_candidates(dep)

        print(f"\n=== Bus Journey ===")
        print(f"Departure: {dep.strftime('%H:%M')}  Arrival: {arr.strftime('%H:%M')}  Duration: {duration}")
        print("Ferry departures after bus start:")
        for f in ferry_candidates:
            marker = " <-- most likely" if f == first_ferry else ""
            print(f"  {f.strftime('%H:%M')}{marker}")

        for leg in j["legs"]:
            mode = leg.get("line", {}).get("productName") or leg.get("mode", "Walk")
            origin = leg["origin"]["name"]
            dest = leg["destination"]["name"]
            dep_t = leg["departure"][11:16]
            arr_t = leg["arrival"][11:16]
            print(f"  {mode}: {origin} ({dep_t}) → {dest} ({arr_t})")
        for rmk in j.get("remarks", []):
            if "text" in rmk:
                print(f"  ⚠ {rmk['text']}")

def main():
    FROM = "Konstanz Allmannsdorf"
    TO = "Meersburg Kirche"
    print(f"Fetching live bus journeys {FROM} → {TO}...")
    try:
        journeys = get_bus_journeys(FROM, TO)
        if journeys:
            print_journeys_with_ferry(journeys)
        else:
            print("No bus journeys found.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
