import os
import json
from pymongo import MongoClient

APP_CONFIG = json.loads(os.getenv("APP_CONFIG", "{}"))

client = MongoClient(APP_CONFIG["mongo_url"])
db = client.get_database()


def already_sent(event_id: str) -> bool:
    return db.events.find_one({"event_id": event_id}) is not None


def save_event(event: dict):
    db.events.update_one(
        {"event_id": event["event_id"]},
        {"$set": event},
        upsert=True
    )


def cleanup_old():
    pass