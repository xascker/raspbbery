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