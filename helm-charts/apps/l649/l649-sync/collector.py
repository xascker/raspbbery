import json
import os
from datetime import date, timedelta, datetime, timezone

import requests
from pymongo import MongoClient

CONFIG = json.loads(os.environ["APP_CONFIG"])

MONGO_URL = CONFIG["mongo_url"]
OLG_CLIENT_ID = CONFIG["olg_client_id"]
OLG_USER_AGENT = CONFIG["olg_user_agent"]
OLG_URL = CONFIG["olg_url"]

def get_draws():
    today = date.today()
    start_date = today - timedelta(days=2)

    params = {
        "game": "lotto649",
        "startDate": start_date.isoformat(),
        "endDate": today.isoformat(),
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "X-Client-Id": OLG_CLIENT_ID,
        "User-Agent": OLG_USER_AGENT,
        "Origin": "https://www.olg.ca",
        "Referer": "https://www.olg.ca/",
    }

    response = requests.get(
        OLG_URL,
        params=params,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    draws = data["response"]["winnings"]["lotto649"]["draw"]

    if isinstance(draws, dict):
        draws = [draws]

    return draws


def build_document(draw):
    main = draw["main"]

    # Winning numbers
    numbers = [
        int(number)
        for number in main["regular"].split(",")
    ]

    # Prize information
    prizes = {}

    for prize in main.get("prizeShares", {}).get("prize", []):
        match = prize["match"]

        item = {
            "winningTickets": int(prize.get("winningTickets", 0)),
            "amount": None,
        }

        amount = prize.get("amount")

        if amount == "FREE PLAY":
            item["amount"] = None
            item["freePlay"] = True

        elif amount:
            item["amount"] = float(
                amount.replace("$", "").replace(",", "")
            )

        prizes[match] = item

    # Gold Ball
    gold_ball = draw.get("goldBallDraw", {})

    gold_ball_data = None

    if gold_ball:
        gold_ball_data = {
            "number": gold_ball.get("number"),
            "isDraw": gold_ball.get("isGoldBallDraw") == "YES",
            "prize": None,
        }

        prize = gold_ball.get("prize")

        if prize and prize != "FREE PLAY":
            gold_ball_data["prize"] = float(
                prize.replace("$", "").replace(",", "")
            )

    document = {
        "date": draw["date"],
        "day": draw["day"],
        "numbers": numbers,
        "bonus": int(main["bonus"]),
        "jackpot": prizes.get("6/6", {}).get("amount"),
        "goldBall": gold_ball_data,
        "encore": draw.get("encore", {}).get("number"),
        "prizes": prizes,
        "createdAt": datetime.now(timezone.utc),
    }

    return document


def save_to_mongo(draws):
    client = MongoClient(MONGO_URL)

    db = client["lotto"]
    collection = db["l649"]

    for draw in draws:
        document = build_document(draw)

        collection.update_one(
            {"date": document["date"]},
            {"$set": document},
            upsert=True,
        )

    client.close()


def main():
    draws = get_draws()

    print(f"Found {len(draws)} draw(s)")

    save_to_mongo(draws)

    print("Done")


if __name__ == "__main__":
    main()
