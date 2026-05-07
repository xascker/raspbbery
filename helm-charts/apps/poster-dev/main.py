import os
import json
import asyncio
import logging

from telegram import Bot

from engine import get_events
from storage import already_sent, save_event, cleanup_old
from utils.time import now_local

# ----------------------------
# CONFIG
# ----------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

APP_CONFIG_RAW = os.getenv("APP_CONFIG", "{}")

try:
    APP_CONFIG = json.loads(APP_CONFIG_RAW)
except json.JSONDecodeError:
    APP_CONFIG = {}

CHANNEL_ID = APP_CONFIG.get("channel_id")

# ----------------------------
# LOGGING CONFIG
# ----------------------------

log_level_str = APP_CONFIG.get("log_level", "WARNING")
log_level = getattr(logging, log_level_str.upper(), logging.WARNING)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logging.warning(f"Log level set to {log_level_str.upper()}")

# ----------------------------
# BOT
# ----------------------------

bot = Bot(token=BOT_TOKEN)


async def send(event):
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=event["message"],
        parse_mode="HTML"
    )


async def main():
    logging.warning("poster started")

    while True:
        try:
            logging.debug("=== TICK ===")
            logging.debug(f"LOCAL TIME: {now_local()}")

            events = get_events()
            logging.debug(f"EVENTS COUNT: {len(events)}")

            cleanup_old()

            for event in events:
                eid = event["event_id"]

                if already_sent(eid):
                    continue

                await send(event)
                save_event(event)

        except Exception as e:
            logging.exception(e)

        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())