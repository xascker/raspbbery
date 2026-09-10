from skyfield.api import load, Topos
from skyfield import almanac
from datetime import datetime, timezone
from pymongo import MongoClient
from zoneinfo import ZoneInfo
import os
import json

# ---------------- CONFIG ----------------

CONFIG = json.loads(os.environ["APP_CONFIG"])

MONGO_URL = CONFIG["mongo_url"]
LAT = float(CONFIG["lat"])
LNG = float(CONFIG["lng"])

LOCAL_TZ = ZoneInfo(CONFIG["local_tz"])

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

topos = Topos(latitude_degrees=LAT, longitude_degrees=LNG)


# ---------------- HELPERS ----------------

def to_local(dt):
    if dt is None:
        return None
    return dt.astimezone(LOCAL_TZ)


def get_moon_state(t):
    astrometric = (earth + topos).at(t).observe(moon)
    alt, az, dist = astrometric.apparent().altaz()
    return astrometric, alt.degrees, az.degrees, dist.km


def get_phase_angle(t):
    moon_ast = (earth + topos).at(t).observe(moon)
    sun_ast = (earth + topos).at(t).observe(sun)
    return sun_ast.separation_from(moon_ast).degrees


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


# ---------------- RISE / SET ----------------

def find_moon_rise_set():
    now = datetime.now(timezone.utc)

    t0 = ts.utc(now.year, now.month, now.day - 1)
    t1 = ts.utc(now.year, now.month, now.day + 2)

    f = almanac.risings_and_settings(eph, moon, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    rise = None
    set_ = None

    for t, event in zip(times, events):
        dt = t.utc_datetime().replace(tzinfo=timezone.utc)

        if dt.date() == now.date():
            if event == 1 and rise is None:
                rise = dt
            elif event == 0 and set_ is None:
                set_ = dt

    return rise, set_


# ---------------- TRANSIT ----------------

def find_moon_transit():
    now = datetime.now(timezone.utc)

    t0 = ts.utc(now.year, now.month, now.day, 0, 0, 0)
    t1 = ts.utc(now.year, now.month, now.day + 1, 0, 0, 0)

    f = almanac.meridian_transits(eph, moon, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    for t, event in zip(times, events):
        if event == 1:
            astrometric = (earth + topos).at(t).observe(moon)
            alt, _, _ = astrometric.apparent().altaz()

            dt = t.utc_datetime().replace(tzinfo=timezone.utc)
            return dt, alt.degrees

    return None, None


# ---------------- MOON DATA ----------------

def get_moon_data():
    t = ts.now()

    _, alt, az, dist = get_moon_state(t)

    rise, set_ = find_moon_rise_set()
    transit, max_alt = find_moon_transit()

    phase_angle = get_phase_angle(t)
    phase = get_moon_phase(phase_angle)

    return {
        "name": "moon",

        # UTC
        "rise_utc": rise.isoformat() if rise else None,
        "set_utc": set_.isoformat() if set_ else None,
        "transit_utc": transit.isoformat() if transit else None,

        # LOCAL
        "rise_local": to_local(rise).isoformat() if rise else None,
        "set_local": to_local(set_).isoformat() if set_ else None,
        "transit_local": to_local(transit).isoformat() if transit else None,

        # current state
        "altitude_now": float(alt),
        "azimuth_now": float(az),
        "distance_km": float(dist),

        # max altitude
        "max_altitude": float(max_alt) if max_alt else None,

        # phase
        "phase_angle": float(phase_angle),
        "phase": phase
    }


# ---------------- MAIN ----------------

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