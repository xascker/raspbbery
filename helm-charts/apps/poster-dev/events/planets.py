from datetime import datetime, timezone, timedelta

from utils.time import parse_dt, to_local
from utils.trace import trace_planet

import logging


def build_planet_events(doc, sun_doc=None):
    events = []

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
            if set_ < sun_set or set_ > sun_set + timedelta(hours=1):
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

        events.append({
            "event_id": f"{doc['_id']}-{name}-window",
            "type": "planet_window",
            "time": event_time,
            "message": (
                f"🪐 {name.title()} window\n\n"
                f"🌅 Rise: {to_local(rise).strftime('%H:%M') if rise else 'N/A'}\n"
                f"🌇 Set: {to_local(set_).strftime('%H:%M')}\n"
                f"⬆️ Transit: {to_local(transit).strftime('%H:%M') if transit else 'N/A'}\n"
                f"📏 Max alt: {round(p.get('max_altitude', 0), 1)}°"
            )
        })

    print("FINAL EVENTS:", len(events))

    return events