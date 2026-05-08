import os
import json

APP_CONFIG = json.loads(os.getenv("APP_CONFIG", "{}"))
DEBUG = APP_CONFIG.get("debug", False)


def trace_engine(events):
    if DEBUG:
        print("\n[ENGINE]")
        print("events:", len(events))


def trace_skip(event_id, reason):
    if DEBUG:
        print(f"[SKIP] {event_id} | {reason}")


def trace_send(event_id):
    if DEBUG:
        print(f"[SEND] {event_id}")


def trace_saved(event_id):
    if DEBUG:
        print(f"[SAVE] {event_id}")


def trace_planet(name, sun_set, set_, event_time=None, skipped=False):
    if DEBUG:
        state = "SKIP" if skipped else "EVENT"

        print(
            f"[PLANET {state}] "
            f"{name} | "
            f"sunset={sun_set} tz={sun_set.tzinfo if sun_set else None} | "
            f"planet_set={set_} tz={set_.tzinfo if set_ else None} | "
            f"event={event_time} tz={event_time.tzinfo if event_time else None}"
        )