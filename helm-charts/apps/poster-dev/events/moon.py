from datetime import timedelta
from utils.time import parse_dt, to_local, to_utc


def build_moon_events(doc):
    events = []

    moon = doc.get("moon", {})

    rise = parse_dt(moon.get("rise_utc"))
    set_ = parse_dt(moon.get("set_utc"))
    transit = parse_dt(moon.get("transit_utc"))

    distance = moon.get("distance_km", "N/A")
    phase = moon.get("phase", "N/A")

    # -------------------------
    # MOON RISE (-5 min)
    # -------------------------
    if rise:
        events.append({
            "event_id": f"{doc['_id']}-moon-rise-pre",
            "type": "moon_rise_pre",
            "time": to_utc(rise - timedelta(minutes=5)),
            "message": (
                f"<code>🌙 Moon rise today</code> - {to_local(rise).strftime('%H:%M')}\n"
                f"<code>🌇 Set:</code> {to_local(set_).strftime('%H:%M') if set_ else 'N/A'}\n"
                f"<code>⬆️ Transit:</code> {to_local(transit).strftime('%H:%M') if transit else 'N/A'}\n"
                f"<code>🌕 Phase:</code> {phase}\n"
                f"<code>📏 Distance:</code> {int(distance) if distance != 'N/A' else 'N/A'} km"
            )
        })

    # -------------------------
    # MOON TRANSIT (-30 min)
    # -------------------------
    if transit:
        events.append({
            "event_id": f"{doc['_id']}-moon-transit-pre",
            "type": "moon_transit_pre",
            "time": to_utc(transit - timedelta(minutes=30)),
            "message": (
                f"<code>🌕 Moon transit event</code> - {to_local(transit).strftime('%H:%M') if transit else 'N/A'}"
            )
        })

    return events