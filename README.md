# Daily AI Brief

OpenAI web research delivered through Telegram. GitHub Actions starts daily at **4:07 AM Eastern** and sends when ready; scheduling delays are possible.

Add repository **Actions secrets**: `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and `DAILY_BRIEF_PROMPT` (`{DATE}` inserts today's Eastern date).

Configure the schedule and model in [daily.yml](.github/workflows/daily.yml). Uses **GPT-5.6 Luna**, high reasoning, and uncapped search calls.

For manual runs: choose `test` (Telegram), `preview` (research only), or `send` (research and deliver).

*AI disclosure: Code generated with assistance from GPT-6.1-Sol.*
