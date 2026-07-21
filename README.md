# SMH Price Alert → Telegram

Checks SMH's price every 30 minutes during US market hours and sends you a
Telegram message once it crosses your threshold ($527 by default). Runs
entirely on GitHub's free servers — nothing on your phone or laptop needs to
stay open.

## 1. Create your Telegram bot (2 minutes)

1. Open Telegram, message **@BotFather**.
2. Send `/newbot`, give it a name and username (e.g. `smh_alert_bot`).
3. BotFather replies with a **token** like `123456789:AAExampleToken`. Save it.
4. Send your new bot any message (e.g. "hi") so it knows who you are.
5. In a browser, open:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   Find `"chat":{"id":123456789,...}` in the response — that number is your
   **chat_id**. Save it.

## 2. Create a GitHub repo

1. Go to github.com → New repository (can be private).
2. Upload everything in this folder (`price_alert.py`, `README.md`, and the
   `.github/workflows/price-alert.yml` file — keep the `.github` folder
   structure intact) to the **root** of the repo.

## 3. Add your secrets

In the repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add two:

- `TELEGRAM_BOT_TOKEN` → the token from step 1
- `TELEGRAM_CHAT_ID` → the chat_id from step 1

## 4. Enable Actions

Go to the **Actions** tab in your repo and enable workflows if prompted.
That's it — it'll now run automatically every 30 minutes, Mon-Fri, 13:00-22:00
UTC (covers 9:30am-4pm ET regardless of daylight saving).

## 5. Test it immediately (don't wait for the schedule)

Actions tab → "SMH Price Alert" workflow → **Run workflow** button. Check the
logs to confirm it printed the price correctly, and check Telegram if the
price is already above threshold.

## Changing the ticker or price

Edit the `env:` block in `.github/workflows/price-alert.yml`:

```yaml
TICKER: SMH
THRESHOLD: "527"
```

Commit the change and it takes effect on the next run.

## Notes

- The script won't spam you — once it alerts, it won't alert again until the
  price drops back below threshold and crosses again (tracked via
  `state.json`, which the workflow commits back to the repo automatically).
- The price feed uses Yahoo Finance's public chart endpoint — free, no API
  key needed, but unofficial, so treat it as a heads-up rather than an
  execution-critical feed.
- GitHub's free tier gives 2,000 Action minutes/month for private repos,
  unlimited for public repos — this job takes seconds per run, so you're
  nowhere close to any limit.
