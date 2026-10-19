# Daily AI Brief

A short daily briefing researched with OpenAI web search and delivered through Telegram using GitHub Actions.

## Setup

1. Create a Telegram bot with [@BotFather](https://t.me/BotFather) and get its token and your chat ID.
2. Add these repository secrets under **Settings > Secrets and variables > Actions**:
   - `OPENAI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `DAILY_BRIEF_PROMPT`: Research instructions; `{DATE}` becomes today's Eastern date.
3. Keep the workflow on the default branch. Edit the schedule and model in [daily.yml](.github/workflows/daily.yml).

## Schedule and settings

Scheduled daily at **4:07 AM Eastern**, adjusting for daylight saving time. The briefing sends as soon as research finishes. GitHub may delay or skip scheduled runs; there is no late-morning cutoff.

Uses **GPT-5.6 Luna with high reasoning**, medium search context, and no search-call cap. The budget is **25,000 generated tokens**, including reasoning; the final message is limited to **1,200 characters**. Costs vary with token and search usage; see [OpenAI pricing](https://developers.openai.com/api/docs/pricing).

Betting analysis checks odds and injuries and can recommend “no bet.” Recheck quoted odds before betting.

## Manual runs

Open **Actions > Daily AI Brief > Run workflow**:

- `test`: Test Telegram.
- `preview`: Research without sending.
- `send`: Research and send immediately. Reruns can send another briefing.

Run local checks:

```sh
python3 -m unittest discover -s tests -v
```

*AI disclosure: Code generated with assistance from GPT-6.1-Sol.*
