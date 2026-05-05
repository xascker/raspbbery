import requests
from datetime import datetime, timezone
from pymongo import MongoClient
import os
import json

# MONGO_URL = os.getenv(
#     "MONGO_URL",
#     "mongodb://root:admin@192.168.1.151:30017/admin"
# )

CONFIG = json.loads(os.environ["APP_CONFIG"])

MONGO_URL = CONFIG["mongo_url"]

LAT = CONFIG["lat"]
LNG = CONFIG["lng"]

SUN_URL = CONFIG["sun_url"]
SOLAR_FL_URL = CONFIG["solar_fl_url"]
KP_URL = CONFIG["kp_url"]

client = MongoClient(MONGO_URL)

db = client.space
col = db.solar


def get_sun():
    r = requests.get(
        SUN_URL,
        params={
            "lat": LAT,
            "lng": LNG,
            "formatted": 0
        },
        timeout=10
    )
    r.raise_for_status()
    return r.json()["results"]


def get_solar_flares_probabilities():
    r = requests.get(SOLAR_FL_URL, timeout=10)
    r.raise_for_status()
    data = r.json()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for row in data:
        if row["date"].startswith(today):
            return row

    return None


def get_kp_forecast():
    r = requests.get(KP_URL, timeout=10)
    r.raise_for_status()

    lines = r.text.splitlines()

    forecast = []
    capture = False

    for line in lines:
        line = line.strip()

        if "NOAA Kp index forecast" in line:
            capture = True
            continue

        if not capture:
            continue

        if "NOAA Geomagnetic Activity Probabilities" in line:
            break

        if "UT" not in line:
            continue

        parts = line.split()

        if len(parts) < 4:
            continue

        try:
            forecast.append({
                "time_slot": parts[0],
                "kp_today": float(parts[1]),  # first column for today
                "kp_tomorrow": float(parts[2]),
                "kp_day3": float(parts[3])
            })
        except:
            continue

    if not forecast:
        return None

    kp_today_values = [x["kp_today"] for x in forecast]

    return {
        "forecast": forecast,
        "kp_max_today": max(kp_today_values),
        "kp_avg_today": round(sum(kp_today_values) / len(kp_today_values), 2)
    }


def main():
    print("collecting solar data...")

    data = {
        "createdAt": datetime.now(timezone.utc),
        "sun": get_sun(),
        "flares_probabilities": get_solar_flares_probabilities(),
        "kp": get_kp_forecast()
    }

    result = col.insert_one(data)
    #print(data)

    print("inserted:", result.inserted_id)


if __name__ == "__main__":
    main()