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
3. Configure the model and schedule in `.github/workflows/daily.yml` and the delivery time in `daily_brief.py`.

Once configured, the briefing runs automatically each day.

The first research trigger is at 6:07 AM Eastern, with automatic retry opportunities
hourly through 11:07 AM. Minute 7 avoids GitHub's busiest top-of-hour window.
Scheduled runs wait until 11 AM to deliver and refuse
delivery after noon. Runs execute one at a time; after a successful send, a
daily GitHub Actions cache record lets later runs skip that day's briefing.
Manual `send` runs also respect that record and deliver immediately when it
is absent. Test and preview runs do not mark the briefing as delivered.
The job allows up to six hours so early runs can wait for delivery. Research
happens when the run starts, so early briefings may miss later morning news.

GitHub can delay or drop scheduled triggers, so 11 AM delivery remains best
effort. Duplicate protection depends on the delivery record being saved and
retained; a failure after Telegram accepts the message but before the record
is saved can still cause a duplicate.

*AI disclosure: Code generated with assistance from GPT-6.1-Sol.*
