import os
import time
from dataclasses import dataclass

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    chat_id: str | None
    interval_seconds: int


def get_settings() -> Settings:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required")

    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    interval_seconds = int(os.getenv("NOTIFY_INTERVAL_SECONDS", "0"))

    return Settings(bot_token=bot_token, chat_id=chat_id, interval_seconds=interval_seconds)


def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    resp.raise_for_status()


def main() -> None:
    settings = get_settings()

    # Minimal integration module:
    # - can be extended later into scheduler/worker (Celery/RQ/APS) and connect to DB.
    if not settings.chat_id:
        print("TELEGRAM_CHAT_ID not set; running idle.")
        while True:
            time.sleep(3600)

    if settings.interval_seconds <= 0:
        send_message(settings.bot_token, settings.chat_id, "Fitness Diary: integration service is up.")
        while True:
            time.sleep(3600)

    while True:
        send_message(settings.bot_token, settings.chat_id, "Напоминание: пора сделать тренировку или записать прогресс.")
        time.sleep(settings.interval_seconds)


if __name__ == "__main__":
    main()

