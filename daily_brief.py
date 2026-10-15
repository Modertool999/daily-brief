"""Daily world/markets + sports research, delivered through Telegram."""

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, time as clock_time, timedelta
from zoneinfo import ZoneInfo

from openai import OpenAI

TIMEZONE = ZoneInfo("America/New_York")
DEFAULT_MODEL = "gpt-5.4-mini"
RESEARCH_TIMEOUT_SECONDS = 40 * 60
POLL_INTERVAL_SECONDS = 10
MAX_BRIEF_CHARACTERS = 1200
DELIVERY_TIME = clock_time(11, 0)
DELIVERY_GRACE_PERIOD = timedelta(hours=1)


def build_prompt() -> str:
    """Load the private prompt and substitute today's date in Eastern time."""
    prompt = os.getenv("DAILY_BRIEF_PROMPT", "")
    if not prompt.strip():
        raise ValueError("DAILY_BRIEF_PROMPT is missing or empty; set the repository secret")

    today = datetime.now(TIMEZONE).strftime("%A, %B %d, %Y")
    return prompt.replace("{DATE}", today)


def research() -> str:
    """Research the briefing and wait for a complete, validated result."""
    prompt = build_prompt()
    client = OpenAI()  # Uses the OPENAI_API_KEY environment variable.
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        input=prompt,
        tools=[{"type": "web_search", "search_context_size": "high"}],
        tool_choice="required",
        reasoning={"effort": "medium"},
        background=True,
    )

    deadline = time.monotonic() + RESEARCH_TIMEOUT_SECONDS
    while response.status in ("queued", "in_progress"):
        if time.monotonic() >= deadline:
            raise TimeoutError("Research exceeded 40 minutes; no briefing sent")
        time.sleep(POLL_INTERVAL_SECONDS)
        response = client.responses.retrieve(response.id)

    if response.status != "completed":
        # Log only the error category, never the API message or response contents.
        error_code = response.error.code if response.error else "unknown"
        raise RuntimeError(
            f"Research ended with status {response.status} "
            f"(error code: {error_code}); no briefing sent"
        )

    message = (response.output_text or "").strip()
    if not message or len(message) > MAX_BRIEF_CHARACTERS:
        raise ValueError(
            f"Briefing is empty or longer than {MAX_BRIEF_CHARACTERS} characters; "
            "no briefing sent"
        )
    return message


def send_telegram(message: str) -> None:
    """Send a message without exposing the bot token in error logs."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        with urllib.request.urlopen(url, data=data, timeout=30) as response:
            result = json.load(response)
    except Exception:
        # Don't expose the request URL, which contains the bot token, in logs.
        raise RuntimeError("Telegram delivery failed; check bot token and chat ID") from None

    if not result.get("ok"):
        raise RuntimeError("Telegram did not confirm message delivery")


def wait_until_delivery_time() -> None:
    """Wait for 11 AM Eastern, rejecting deliveries more than an hour late."""
    now = datetime.now(TIMEZONE)
    target = datetime.combine(now.date(), DELIVERY_TIME, tzinfo=TIMEZONE)
    if now > target + DELIVERY_GRACE_PERIOD:
        raise RuntimeError("Too late to deliver today's briefing")

    wait_seconds = (target - now).total_seconds()
    if wait_seconds > 0:
        print(
            f"Research complete; waiting {int(wait_seconds)} seconds until 11 AM ET.",
            flush=True,
        )
        time.sleep(wait_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily AI briefing to Telegram")
    parser.add_argument(
        "mode",
        choices=("test", "preview", "send"),
        help="test Telegram, preview the briefing, or research and send it",
    )
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
        wait_until_delivery_time()
    send_telegram(message)
    print("Daily briefing delivered via Telegram.")


if __name__ == "__main__":
    main()
