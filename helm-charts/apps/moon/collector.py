from skyfield.api import load, Topos
from datetime import datetime, timezone
from pymongo import MongoClient
import os
import json

# ---------------- CONFIG ----------------

# DEFAULT_CONFIG = {
#     "mongo_url": "mongodb://root:admin@192.168.1.151:30017/admin",
#     "lat": 53.5461,
#     "lng": -113.4938
# }
#CONFIG = json.loads(os.getenv("APP_CONFIG", "null")) or DEFAULT_CONFIG

CONFIG = json.loads(os.environ["APP_CONFIG"])

MONGO_URL = CONFIG["mongo_url"]
LAT = float(CONFIG["lat"])
LNG = float(CONFIG["lng"])

# ---------------- DB ----------------

client = MongoClient(MONGO_URL)
db = client.space
col = db.moon

# ---------------- SKYFIELD ----------------

ts = load.timescale()
eph = load("de421.bsp")

earth = eph["earth"]
moon = eph["moon"]
sun = eph["sun"]

observer = earth + Topos(latitude_degrees=LAT, longitude_degrees=LNG)


# ---------------- PHASE ----------------

def get_moon_phase(angle_deg):
    if angle_deg < 10:
        return "New Moon"
    elif angle_deg < 80:
        return "Waxing Crescent"
    elif angle_deg < 100:
        return "First Quarter"
    elif angle_deg < 160:
        return "Waxing Gibbous"
    elif angle_deg < 200:
        return "Full Moon"
    elif angle_deg < 260:
        return "Waning Gibbous"
    elif angle_deg < 280:
        return "Last Quarter"
    else:
        return "Waning Crescent"


# ---------------- ALT / AZ / DIST ----------------

def get_state(t):
    astrometric = observer.at(t).observe(moon)
    alt, az, dist = astrometric.apparent().altaz()
    return alt.degrees, az.degrees, dist.km


# ---------------- RISE / SET ----------------

def find_rise_set():
    now = datetime.now(timezone.utc)

    start = ts.utc(now.year, now.month, now.day, 0, 0, 0)
    end = ts.utc(now.year, now.month, now.day, 23, 59, 59)

    step_minutes = 10
    step_days = step_minutes / (60 * 24)

    times = []
    alts = []

    t = start
    while t.tt < end.tt:
        alt, _, _ = get_state(t)
        times.append(t)
        alts.append(alt)
        t = ts.tt_jd(t.tt + step_days)

    moonrise = None
    moonset = None

    for i in range(1, len(alts)):
        if alts[i - 1] < 0 and alts[i] >= 0 and moonrise is None:
            moonrise = times[i].utc_datetime().replace(tzinfo=timezone.utc)

        if alts[i - 1] >= 0 and alts[i] < 0 and moonset is None:
            moonset = times[i].utc_datetime().replace(tzinfo=timezone.utc)

    return moonrise, moonset


# ---------------- MAIN DATA ----------------

def get_moon_data():
    t = ts.now()

    astrometric = observer.at(t).observe(moon)
    alt, az, dist = astrometric.apparent().altaz()

    sun_ast = observer.at(t).observe(sun)
    sun_moon_angle = sun_ast.separation_from(astrometric).degrees

    moonrise, moonset = find_rise_set()

    return {
        "moonrise": moonrise.isoformat() if moonrise else None,
        "moonset": moonset.isoformat() if moonset else None,
        "altitude": float(alt.degrees),
        "azimuth": float(az.degrees),
        "distance_km": float(dist.km),
        "phase": get_moon_phase(sun_moon_angle)
    }


# ---------------- RUN ----------------

def main():
    print("collecting moon data (UTC Skyfield)...")

    data = {
        "createdAt": datetime.now(timezone.utc),
        "moon": get_moon_data()
    }

    result = col.insert_one(data)

    print("inserted:", result.inserted_id)


if __name__ == "__main__":
    main()