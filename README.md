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
3. Configure the model in `.github/workflows/daily.yml` and the delivery time in `daily_brief.py`.
4. Push these changes to the repository's default branch before configuring the external scheduler.

## Daily scheduling with cron-job.org

The primary trigger starts research at **10 AM America/New_York** every day.
The script waits until **11 AM Eastern** to send. GitHub's own schedule provides
backup triggers at **11:07 AM and 12:07 PM Eastern**. No Railway or continuously
running computer is needed.

1. Sign in to [cron-job.org](https://console.cron-job.org/).
2. Create a [fine-grained GitHub personal access token](https://github.com/settings/personal-access-tokens/new)
   restricted to **Modertool999/daily-brief**, with repository permission
   **Actions: Read and write**. Set an expiration and replace the scheduler's
   token before it expires. Keep the token out of the repository and logs.
3. Create a cron job with these settings:

   | Setting | Value |
   | --- | --- |
   | Title | Daily AI Brief |
   | URL | `https://api.github.com/repos/Modertool999/daily-brief/actions/workflows/daily.yml/dispatches` |
   | Time zone | `America/New_York` |
   | Schedule | Every day at 10:00 AM (`0 10 * * *`) |
   | Request method | `POST` |
   | Save response | Disabled |

   Add these custom headers:

   ```text
   Accept: application/vnd.github+json
   Authorization: Bearer YOUR_FINE_GRAINED_TOKEN
   Content-Type: application/json
   X-GitHub-Api-Version: 2026-03-10
   ```

   Use this request body, replacing `main` if the default branch has another name:

   ```json
   {"ref":"main","inputs":{"mode":"send","wait_until_delivery":"true"}}
   ```

4. Enable the job. Optionally create a second job with the same URL, headers,
   and body at **10:45 AM Eastern** (`45 10 * * *`) as an external retry.
   Both jobs must use the `America/New_York` time zone so daylight saving time
   adjusts automatically.
5. To verify credentials without sending a briefing, temporarily use
   `{"ref":"main","inputs":{"mode":"preview","wait_until_delivery":"true"}}`
   and use the scheduler's test-run feature. Check that GitHub Actions creates
   a successful preview run, then restore the `send` body before enabling the job.
   A successful scheduler request only confirms that GitHub accepted the trigger;
   check GitHub Actions for research and Telegram failures.

The external scheduler uses GitHub's [workflow dispatch API](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event).
[cron-job.org supports POST requests and custom headers](https://cron-job.org/en/faq/).
Both the scheduler and GitHub runners can experience delays, so 11 AM delivery
remains best effort.

## Delivery and manual runs

If scheduling or research runs late, the script delivers as soon as research
finishes that day, including after noon. Research from a previous Eastern
calendar day is rejected for automated delivery.

Runs execute one at a time. After a successful send, a daily GitHub Actions
cache record lets later runs skip that day's briefing. Manual `send` runs also
respect that record and deliver immediately when it is absent. Select
**Wait until 11 AM Eastern** in the manual workflow form to opt into waiting.
Test and preview runs do not mark the briefing as delivered.

The job allows up to two hours for research and waiting. Duplicate protection
depends on the delivery record being saved and retained; a failure after
Telegram accepts the message but before the record is saved can still cause
a duplicate.

Run the local timing and command tests without API credentials:

```sh
python3 -m unittest discover -s tests -v
```

*AI disclosure: Code generated with assistance from GPT-6.1-Sol.*
