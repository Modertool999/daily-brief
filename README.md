# Daily AI Brief

An automated daily research briefing powered by OpenAI, scheduled with GitHub Actions, and delivered through Telegram.

The bot uses web search to research topics specified in a customizable prompt and sends a concise summary each morning. Everything runs through GitHub Actions, so no local setup or continuously running computer is required.

## Setup

1. Create a Telegram bot using [@BotFather](https://t.me/BotFather) and obtain your bot token and chat ID.
2. Add the following repository secrets under GitHub's **Settings > Secrets and variables > Actions**:
   - `DAILY_BRIEF_PROMPT`: Instructions for the AI research.
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
   - `TELEGRAM_CHAT_ID`: The destination chat ID.
3. Push the workflow to the repository's default branch. Configure the schedule
   and model in `.github/workflows/daily.yml`, and delivery time in `daily_brief.py`.

## Schedule

One GitHub Actions workflow is scheduled daily at **4:07 AM America/New_York**.
It researches the briefing, then waits until **10 AM Eastern** to send it.
Daylight saving time adjusts automatically. Starting early leaves room for
GitHub scheduling delays. The job has a six-hour timeout, enough for the
4:07 AM start to wait until 10 AM.

If a run starts or finishes research after 10 AM, it sends immediately that day,
including after noon. There is no late-morning cutoff. Research from a previous
Eastern calendar day is rejected. GitHub can delay or drop scheduled runs, so
morning delivery remains best effort. Early research may miss later morning news.

Everything runs on GitHub Actions. No external scheduler, scheduler token,
automatic retries, or delivery cache is required. Runs execute one at a time.
Waiting uses runner minutes, including paid or included minutes for private
repositories.

## Manual runs

Use **Actions > Daily AI Brief > Run workflow** and select a mode:

- `test`: Send a Telegram connection test.
- `preview`: Research and print the briefing without sending it.
- `send`: Research and send immediately, without waiting for 10 AM.

Each `send` run sends a message; manually rerunning it can send another briefing
on the same day.

Run the timing and command checks without API credentials:

```sh
python3 -m unittest discover -s tests -v
```

*AI disclosure: Code generated with assistance from GPT-6.1-Sol.*
