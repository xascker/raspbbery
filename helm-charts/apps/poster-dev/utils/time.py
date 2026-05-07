from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os
import json

APP_CONFIG = json.loads(os.getenv("APP_CONFIG", "{}"))

LOCAL_TZ = ZoneInfo(APP_CONFIG["local_tz"])


def now_local():
    return datetime.now(LOCAL_TZ)


def utc_now():
    return datetime.now(timezone.utc)


def parse_dt(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    return dt


def ensure_aware(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = parse_dt(dt)

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


def to_local(dt):
    dt = parse_dt(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(LOCAL_TZ)


def to_utc(dt):
    dt = parse_dt(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(timezone.utc)


def utc_day_start_from_local():
    local = now_local().replace(hour=0, minute=0, second=0, microsecond=0)
    return local.astimezone(timezone.utc)


def utc_day_end_from_local():
    local = now_local().replace(hour=23, minute=59, second=59, microsecond=999999)
    return local.astimezone(timezone.utc)