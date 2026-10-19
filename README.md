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
   and model in `.github/workflows/daily.yml`.

## Schedule

One GitHub Actions workflow is scheduled daily at **4:07 AM America/New_York**.
It researches the briefing and **sends immediately when ready**, with no wait for
a specific delivery time and no late-morning cutoff. If GitHub starts the run on
time, it can arrive shortly after 4 AM; if GitHub delays it, it arrives later.
Daylight saving time adjusts automatically. GitHub can delay or drop scheduled
runs, so morning delivery remains best effort. Research that crosses into the
next Eastern calendar day is rejected.

Everything runs on GitHub Actions with a one-hour job timeout. No external
scheduler, scheduler token, automatic retries, or delivery cache is required.
Runs execute one at a time.

## Research settings and cost

The script keeps **GPT-5.6 Luna**, raises reasoning from medium to **high**, and
uses medium search context with low output verbosity. One request handles the
whole brief; no background polling or second model pass is needed. The request
has a 40-minute timeout and automatic API retries are disabled.

There is **no explicit search-call cap**: the model can search as needed within
the request timeout and **25,000 output-token** budget (including internal reasoning). The final briefing must still fit within
**1,200 characters**. Incomplete or oversized output is rejected rather than sent.

The betting instructions prioritize verified odds, bookmaker and timestamp,
injuries, implied probability and an evidence-based estimated edge. They allow
“no bet” when prices or an edge cannot be verified and require rechecking odds
before betting. Research happens early, so prices and injury news may change
before delivery. More reasoning does not establish that the estimates are accurate.

At [published OpenAI prices](https://developers.openai.com/api/docs/pricing),
Luna costs $0.20/million input tokens and $1.20/million output tokens; web search
costs $0.01/call plus search-content input tokens. The generated-token budget
costs at most $0.03 per request at that model's standard output rate; search
and input tokens are additional and vary with usage. The previous approximately
$3/month example assumed six calls per day and is not an estimate for uncapped
search. More searching can improve coverage but does not guarantee better picks.

[Model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna)

## Manual runs

Use **Actions > Daily AI Brief > Run workflow** and select a mode:

- `test`: Send a Telegram connection test.
- `preview`: Research and print the briefing without sending it.
- `send`: Research and send immediately.

Each `send` run sends a message; manually rerunning it can send another briefing
on the same day.

Run the research and command checks without API credentials:

```sh
python3 -m unittest discover -s tests -v
```

*AI disclosure: Code generated with assistance from GPT-6.1-Sol.*
