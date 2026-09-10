from skyfield.api import load, Topos
from skyfield import almanac
from datetime import datetime, timezone
from pymongo import MongoClient
import os
import json
from zoneinfo import ZoneInfo

# ---------------- CONFIG ----------------

# DEFAULT_CONFIG = {
#     "mongo_url": "mongodb://root:admin@192.168.1.151:30017/admin",
#     "lat": 53.5461,
#     "lng": -113.4938,
#     "local_tz": "America/Edmonton"
# }
#CONFIG = json.loads(os.getenv("APP_CONFIG", "null")) or DEFAULT_CONFIG

CONFIG = json.loads(os.environ["APP_CONFIG"])

MONGO_URL = CONFIG["mongo_url"]
LAT = float(CONFIG["lat"])
LNG = float(CONFIG["lng"])

LOCAL_TZ = ZoneInfo(CONFIG["local_tz"])

# ---------------- DB ----------------

client = MongoClient(MONGO_URL)
db = client.space
col = db.planets

# ---------------- SKYFIELD ----------------

ts = load.timescale()
eph = load("de421.bsp")

earth = eph["earth"]

venus = eph["venus"]
mars = eph["mars"]
jupiter = eph["jupiter barycenter"]
saturn = eph["saturn barycenter"]

topos = Topos(latitude_degrees=LAT, longitude_degrees=LNG)


# ---------------- HELPERS ----------------

def to_local(dt):
    if dt is None:
        return None
    return dt.astimezone(LOCAL_TZ)


def get_body_state(body, t):
    astrometric = (earth + topos).at(t).observe(body)
    alt, az, dist = astrometric.apparent().altaz()
    return alt.degrees, az.degrees, dist.km


# ---------------- RISE / SET ----------------

def find_rise_set(body):
    now = datetime.now(timezone.utc)

    t0 = ts.utc(now.year, now.month, now.day - 1)
    t1 = ts.utc(now.year, now.month, now.day + 3)

    f = almanac.risings_and_settings(eph, body, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    rise = None
    set_ = None

    for t, event in zip(times, events):
        dt = t.utc_datetime().replace(tzinfo=timezone.utc)

        # first rise after now
        if event == 1 and dt > now and rise is None:
            rise = dt

        # first set after rise
        elif event == 0 and rise and dt > rise:
            set_ = dt
            break

    return rise, set_


# ---------------- TRANSIT ----------------

def find_transit(body):
    now = datetime.now(timezone.utc)

    t0 = ts.utc(now.year, now.month, now.day, 0, 0, 0)
    t1 = ts.utc(now.year, now.month, now.day + 1, 0, 0, 0)

    f = almanac.meridian_transits(eph, body, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    for t, event in zip(times, events):
        if event == 1:
            alt, _, _ = get_body_state(body, t)
            dt = t.utc_datetime().replace(tzinfo=timezone.utc)
            return dt, alt

    return None, None


# ---------------- PLANET DATA ----------------

def get_planet_data(name, body):
    t = ts.now()

    alt, az, dist = get_body_state(body, t)
    rise, set_ = find_rise_set(body)
    transit, max_alt = find_transit(body)

    return {
        "name": name,

        "rise_utc": rise.isoformat() if rise else None,
        "set_utc": set_.isoformat() if set_ else None,
        "transit_utc": transit.isoformat() if transit else None,

        "rise_local": to_local(rise).isoformat() if rise else None,
        "set_local": to_local(set_).isoformat() if set_ else None,
        "transit_local": to_local(transit).isoformat() if transit else None,

        "altitude_now": float(alt),
        "azimuth_now": float(az),
        "distance_km": float(dist),

        "max_altitude": float(max_alt) if max_alt else None
    }


# ---------------- MAIN ----------------

def main():
    print("collecting planet data (UTC Skyfield)...")

    planets = {
        "venus": venus,
        "mars": mars,
        "jupiter": jupiter,
        "saturn": saturn
    }

    planet_data = {}

    for name, body in planets.items():
        planet_data[name] = get_planet_data(name, body)

    data = {
        "createdAt": datetime.now(timezone.utc),
        "planets": planet_data
    }

    result = col.insert_one(data)

    print("inserted:", result.inserted_id)


if __name__ == "__main__":
    main()