import os
import json
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from handlers.test import test_command
from handlers.start import start_command

# ----------------------------
# CONFIG
# ----------------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")

APP_CONFIG_RAW = os.getenv("APP_CONFIG", "{}")

try:
    APP_CONFIG = json.loads(APP_CONFIG_RAW)
except json.JSONDecodeError:
    APP_CONFIG = {}

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
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

# ----------------------------
# BOT APP
# ----------------------------

app = ApplicationBuilder().token(BOT_TOKEN).build()

# commands
app.add_handler(CommandHandler("start", start_command))
app.add_handler(CommandHandler("test", test_command))

# ----------------------------
# RUN
# ----------------------------

if __name__ == "__main__":
    logging.info("Bot starting...")
    app.run_polling()