from datetime import timedelta
from utils.time import parse_dt, to_local, to_utc


def build_planet_events(doc, sun_doc=None):
    events = []

    planets = doc.get("planets", {})

    sun_set = None
    if sun_doc:
        sun_set = parse_dt(sun_doc.get("sun", {}).get("sunset"))

    for name, p in planets.items():

        rise = parse_dt(p.get("rise_utc"))
        set_ = parse_dt(p.get("set_utc"))
        transit = parse_dt(p.get("transit_utc"))

        if not set_:
            continue

        # -------------------------
        # visibility rule
        # -------------------------
        if sun_set and set_ <= sun_set + timedelta(hours=1):
            continue

        event_time = None

        if sun_set:
            event_time = sun_set - timedelta(minutes=20)
        else:
            event_time = set_ - timedelta(minutes=20)

        events.append({
            "event_id": f"{doc['_id']}-{name}-window",
            "type": "planet_window",
            "time": to_utc(event_time),
            "message": (
                f"🪐 {name.title()} window\n\n"
                f"🌅 Rise: {to_local(rise).strftime('%H:%M') if rise else 'N/A'}\n"
                f"🌇 Set: {to_local(set_).strftime('%H:%M')}\n"
                f"⬆️ Transit: {to_local(transit).strftime('%H:%M') if transit else 'N/A'}\n"
                f"📏 Max alt: {round(p.get('max_altitude', 0), 1)}°"
            )
        })

    return events