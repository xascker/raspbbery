from datetime import datetime, timezone, timedelta

from utils.time import parse_dt, to_local, format_astro
from utils.trace import trace_planet

import logging


PLANET_ICONS = {
    "venus": "⚪️",
    "mars": "🔴️",
    "jupiter": "🟠",
    "saturn": "🪐",
    "mercury": "☿",
    "uranus": "⛢",
    "neptune": "♆",
}


def build_planet_events(doc, sun_doc=None):
    events = []
    now_local = to_local(datetime.now(timezone.utc))
    planets = doc.get("planets", {})

    sun_set = None
    if sun_doc:
        raw_sunset = sun_doc.get("sun", {}).get("sunset")
        sun_set = parse_dt(raw_sunset) if raw_sunset else None

    now = datetime.now(timezone.utc)

    # # -------------------------
    # # DEBUG BLOCK
    # # -------------------------
    # logging.debug("===== PLANET DEBUG =====")
    # logging.debug(f"NOW: {now}")
    # logging.debug(f"SUN_DOC: {sun_doc}")
    # logging.debug(f"SUNSET: {sun_set} {getattr(sun_set, 'tzinfo', None)}")
    # logging.debug(f"PLANETS COUNT: {len(planets)}")
    # logging.debug("========================")

    for name, p in planets.items():

        rise = parse_dt(p.get("rise_utc"))
        set_ = parse_dt(p.get("set_utc"))
        transit = parse_dt(p.get("transit_utc"))

# #----
#         logging.debug(f"[{name}] SET: {set_}")
#         logging.debug(f"[{name}] SUN: {sun_set}")
#         if set_ and sun_set:
#             diff_hours = (set_ - sun_set).total_seconds() / 3600
#             logging.debug(f"[{name}] DIFF HOURS: {diff_hours}")
#         else:
#             logging.debug(f"[{name}] DIFF HOURS: None (missing data)")
# #----

        if not set_:
            continue

        # visibility rule
        if sun_set:
            if set_ <= sun_set + timedelta(hours=1):
                trace_planet(
                    name=name,
                    sun_set=sun_set,
                    set_=set_,
                    skipped=True
                )
                continue
            event_time = sun_set - timedelta(minutes=20)
        else:
            event_time = set_ - timedelta(minutes=20)

        # scheduler gate
        if event_time > now:
            trace_planet(
                name=name,
                sun_set=sun_set,
                set_=set_,
                event_time=event_time,
                skipped=True
            )
            continue

        trace_planet(
            name=name,
            sun_set=sun_set,
            set_=set_,
            event_time=event_time
        )

        icon = PLANET_ICONS.get(name.lower(), "🪐")

        events.append({
            "event_id": f"{doc['_id']}-{name}-window",
            "type": "planet_window",
            "time": event_time,
            "message": (
                f"<pre>{icon} {name.title()} window</pre>\n"
                f"🌅 Rise: {format_astro(rise, now_local)}\n"
                f"🌇 Set: {format_astro(set_, now_local)}\n"
                f"⬆️ Transit: {format_astro(transit, now_local)}\n"
                f"📏 Max alt: {round(p.get('max_altitude', 0), 1)}°"
            )
        })

    print("FINAL EVENTS:", len(events))

    return events