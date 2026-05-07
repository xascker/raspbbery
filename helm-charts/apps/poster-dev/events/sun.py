from datetime import timedelta
from utils.time import parse_dt, to_local, to_utc


def build_sun_events(doc):
    events = []

    sun = doc.get("sun", {})
    kp = doc.get("kp", {})
    flares = doc.get("flares_probabilities", {})

    sunrise = parse_dt(sun.get("sunrise"))
    sunset = parse_dt(sun.get("sunset"))

    # -------------------------
    # SUNRISE PRE (-45 min)
    # -------------------------
    if sunrise:
        events.append({
            "event_id": f"{doc['_id']}-sunrise-pre",
            "type": "sunrise_pre",
            "time": to_utc(sunrise - timedelta(minutes=45)),
            "message": (
                f"<code>🌄 Sunrise today</code> - {to_local(sunrise).strftime('%H:%M')}\n"
                f"<code>🌇 Sunset</code>: {to_local(sunset).strftime('%H:%M') if sunset else 'N/A'}\n"
                f"<code>🧲 Geomag:</code> "
                    f"Max {kp.get('kp_max_today', 'N/A')}, "
                    f"Avg {kp.get('kp_avg_today', 'N/A')}\n"
                f"<code>📊 Flares:</code> "
                    f"M{flares.get('m_class_1_day', 'N/A')}%, "
                    f"X{flares.get('x_class_1_day', 'N/A')}%"

            )
        })

    # -------------------------
    # SUNSET PRE (-30 min)
    # -------------------------
    if sunset:
        events.append({
            "event_id": f"{doc['_id']}-sunset-pre",
            "type": "sunset_pre",
            "time": to_utc(sunset - timedelta(minutes=30)),
            "message": (
                f"<code>🌇 Sunset event</code> - {to_local(sunset).strftime('%H:%M') if sunset else 'N/A'}"
            )
        })

    return events