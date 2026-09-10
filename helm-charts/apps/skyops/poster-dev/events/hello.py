from datetime import datetime, timedelta

_last_run = None


def get_hello_events():
    global _last_run

    now = datetime.utcnow()

    if _last_run and (now - _last_run).seconds < 60:
        return []

    _last_run = now

    return [
        {
            "type": "hello",
            "message": "👋 Hello from poster engine!",
            "timestamp": now.isoformat()
        }
    ]