"""Daily world/markets + sports research, delivered through Telegram."""

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, time as clock_time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import OpenAI

TZ = ZoneInfo("America/New_York")


def research() -> str:
    today = datetime.now(TZ).strftime("%A, %B %d, %Y")
    prompt = Path(__file__).with_name("prompt.txt").read_text(encoding="utf-8")

    client = OpenAI()  # Uses the OPENAI_API_KEY environment variable.
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        input=prompt.replace("{DATE}", today),
        tools=[{"type": "web_search", "search_context_size": "high"}],
        tool_choice="required",
        reasoning={"effort": "high"},
        background=True,
    )

    deadline = time.monotonic() + 40 * 60
    while response.status in ("queued", "in_progress"):
        if time.monotonic() >= deadline:
            raise TimeoutError("Research exceeded 40 minutes; no briefing sent")
        time.sleep(10)
        response = client.responses.retrieve(response.id)

    if response.status != "completed":
        raise RuntimeError(f"Research ended with status {response.status}; no briefing sent")

    message = (response.output_text or "").strip()
    if not message or len(message) > 1200:
        raise ValueError("Briefing is empty or longer than 1200 characters; no briefing sent")
    return message


def send_telegram(message: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        with urllib.request.urlopen(url, data=data, timeout=30) as response:
            result = json.load(response)
    except Exception as error:
        # Don't expose the request URL, which contains the bot token, in logs.
        raise RuntimeError("Telegram delivery failed; check bot token and chat ID") from None

    if not result.get("ok"):
        raise RuntimeError("Telegram did not confirm message delivery")


def wait_until_11am() -> None:
    now = datetime.now(TZ)
    target = datetime.combine(now.date(), clock_time(11, 0), tzinfo=TZ)
    if now > target + timedelta(hours=1):
        raise RuntimeError("Too late to deliver today's briefing")
    wait_seconds = (target - now).total_seconds()
    if wait_seconds > 0:
        print(f"Research complete; waiting {int(wait_seconds)} seconds until 11 AM ET.", flush=True)
        time.sleep(wait_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily AI briefing to Telegram")
    parser.add_argument("mode", choices=("test", "preview", "send"))
    args = parser.parse_args()

    if args.mode == "test":
        send_telegram("Telegram is connected! Your daily AI brief is ready for scheduling.")
        print("Telegram test delivered.")
        return

    message = research()
    if args.mode == "preview":
        print("PREVIEW — not sent to Telegram:\n" + message)
        return

    # Only the scheduled workflow waits for the requested 11 AM delivery time.
    if os.getenv("GITHUB_EVENT_NAME") == "schedule":
        wait_until_11am()
    send_telegram(message)
    print("Daily briefing delivered via Telegram.")


if __name__ == "__main__":
    main()
