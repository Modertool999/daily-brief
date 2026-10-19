"""Research a short daily briefing and deliver it through Telegram."""

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from zoneinfo import ZoneInfo

from openai import OpenAI

TIMEZONE = ZoneInfo("America/New_York")


def research() -> str:
    prompt = os.environ["DAILY_BRIEF_PROMPT"].strip()
    if not prompt:
        raise ValueError("DAILY_BRIEF_PROMPT is empty")
    response = OpenAI(timeout=2400, max_retries=0).responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        input=prompt.replace("{DATE}", datetime.now(TIMEZONE).strftime("%A, %B %d, %Y")),
        instructions=(
            "Keep the entire briefing within 1200 characters. Spend most analysis on "
            "the betting section: verify current odds, bookmaker, timestamp and injuries; "
            "compare implied probability with an evidence-based estimate, accounting for "
            "bookmaker margin. Distinguish estimates from facts. Cite sources briefly. "
            "If odds or an edge cannot be verified, say no bet; never invent prices or "
            "probabilities. State that quoted odds must be rechecked before betting."
        ),
        tools=[{"type": "web_search", "search_context_size": "medium"}],
        tool_choice="required",
        reasoning={"effort": "high"},
        text={"verbosity": "low"},
        max_output_tokens=25000,  # Includes reasoning, not just the short final text.
        max_tool_calls=6,
    )
    message = (response.output_text or "").strip()
    if response.status != "completed" or not 0 < len(message) <= 1200:
        raise RuntimeError("Research incomplete, empty or over 1200 characters; no briefing sent")
    return message


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": message}).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=30) as response:
            if not json.load(response).get("ok"):
                raise RuntimeError("Telegram rejected the message")
    except Exception:
        # Request exceptions can contain the bot token in the URL.
        raise RuntimeError("Telegram delivery failed; check bot token and chat ID") from None


def wait_until_delivery_time(briefing_date: date) -> None:
    now = datetime.now(TIMEZONE)
    if now.date() != briefing_date:
        raise RuntimeError("Briefing is from a previous day; no briefing sent")
    seconds = max(0, (now.replace(hour=10, minute=0, second=0, microsecond=0) - now).total_seconds())
    if seconds:
        print(f"Research ready; waiting {int(seconds)} seconds until 10 AM ET.", flush=True)
        time.sleep(seconds)
        if datetime.now(TIMEZONE).date() != briefing_date:
            raise RuntimeError("Briefing is from a previous day; no briefing sent")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("test", "preview", "send"))
    mode = parser.parse_args().mode
    if mode == "test":
        send_telegram("Telegram is connected!")
        return
    briefing_date = datetime.now(TIMEZONE).date()
    message = research()
    if mode == "preview":
        print(message)
        return
    if os.getenv("GITHUB_EVENT_NAME") == "schedule":
        wait_until_delivery_time(briefing_date)
    send_telegram(message)
    print("Daily briefing delivered.")


if __name__ == "__main__":
    main()
