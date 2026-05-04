import requests
from datetime import datetime, timezone
from pymongo import MongoClient
import os

# MONGO_URL = os.getenv(
#     "MONGO_URL",
#     "mongodb://root:admin@192.168.1.151:30017/admin"
# )

MONGO_URL = os.environ["MONGO_URL"]

client = MongoClient(MONGO_URL)

db = client.space
col = db.solar


def get_sun():
    url = "https://api.sunrise-sunset.org/json?lat=53.5461&lng=-113.4938&formatted=0"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()["results"]


def get_solar_flares_probabilities():
    url = "https://services.swpc.noaa.gov/json/solar_probabilities.json"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for row in data:
        if row["date"].startswith(today):
            return row

    return None


def get_kp_forecast():
    url = "https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt"
    r = requests.get(url, timeout=10)
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