#!/usr/bin/env python3
import requests
from datetime import datetime

BASE = "https://v6.db.transport.rest"

def find_stop_id(name):
    """Find stop ID by name (returns first match)."""
    r = requests.get(f"{BASE}/locations", params={"query": name, "results": 1})
    r.raise_for_status()
    data = r.json()
    if not data or not isinstance(data, list):
        raise ValueError(f"Unexpected response format for {name}")
    return data[0]["id"]

def parse_time(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def fmt_duration(dep, arr):
    delta = arr - dep
    mins = int(delta.total_seconds() // 60)
    h, m = divmod(mins, 60)
    return f"{h}h {m:02d}m"

def get_bus_journeys(from_name, to_name, results=5):
    """Fetch only bus journeys."""
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
        "products": {"bus": True},  # only allow bus journeys
    }

    r = requests.get(f"{BASE}/journeys", params=params)
    r.raise_for_status()
    data = r.json()
    if not data or "journeys" not in data:
        raise ValueError("No journeys found or unexpected response")
    return data["journeys"]

def print_journeys(journeys):
    for j in journeys:
        first_leg = j["legs"][0]
        last_leg = j["legs"][-1]
        dep = parse_time(first_leg["departure"])
        arr = parse_time(last_leg["arrival"])
        duration = fmt_duration(dep, arr)
        print(f"\n=== Bus Journey ===")
        print(f"Departure: {dep.strftime('%H:%M')}  Arrival: {arr.strftime('%H:%M')}  Duration: {duration}")
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
    print("Fetching live *bus* journeys Konstanz → Meersburg...")
    try:
        journeys = get_bus_journeys("Konstanz", "Meersburg (Bodensee)")
        print_journeys(journeys)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
