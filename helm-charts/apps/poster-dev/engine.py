from storage import db
from events.sun import build_sun_events
from events.moon import build_moon_events
from events.planets import build_planet_events
from utils.time import utc_day_start_from_local, utc_day_end_from_local, ensure_aware
from datetime import timezone

UTC = timezone.utc


def get_events():
    doc = db.solar.find_one(sort=[("createdAt", -1)])

    if not doc:
        return []

    start = utc_day_start_from_local()
    end = utc_day_end_from_local()

    doc_time = ensure_aware(doc.get("createdAt"))

    if not doc_time:
        return []

    doc_time = doc_time.astimezone(UTC)

    if not (start <= doc_time <= end):
        return []

    events = []

    # SUN
    events.extend(build_sun_events(doc))

    # MOON
    moon_doc = db.moon.find_one(sort=[("createdAt", -1)])
    if moon_doc:
        events.extend(build_moon_events(moon_doc))

    # PLANETS
    planet_doc = db.planets.find_one(sort=[("createdAt", -1)])
    sun_doc = db.solar.find_one(sort=[("createdAt", -1)])
    if planet_doc:
        events.extend(
            build_planet_events(planet_doc, sun_doc)
        )

    return events