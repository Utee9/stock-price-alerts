import os
import json
import requests
from datetime import datetime, timezone

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
CONFIG_FILE = "tickers.json"
STATE_FILE = "state.json"


def load_config() -> list:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_price(ticker: str) -> float:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data["chart"]["result"][0]
    return result["meta"]["regularMarketPrice"]


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_notification": False,
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()


def check_ticker(entry: dict, state: dict, today: str, price_cache: dict) -> None:
    ticker = entry["ticker"]
    threshold = float(entry["threshold"])
    direction = entry.get("direction", "above").lower()
    label = entry.get("label")  # optional custom note, e.g. "sell target"

    # unique key so multiple alerts on the same ticker don't overwrite each other
    alert_key = entry.get("id") or f"{ticker}_{threshold}_{direction}"

    if ticker not in price_cache:
        price_cache[ticker] = get_price(ticker)
    price = price_cache[ticker]

    print(f"[{alert_key}] {ticker} price: {price} | threshold: {threshold} | direction: {direction}")

    condition_met = price >= threshold if direction == "above" else price <= threshold
    alert_state = state.get(alert_key, {})

    if condition_met:
        if alert_state.get("alerted_date") == today:
            print(f"[{alert_key}]: already alerted today, skipping.")
            return
        arrow = "🚀" if direction == "above" else "🔻"
        extra = f"\nNote: {label}" if label else ""
        message = (
            f"{arrow} *{ticker} ALERT*\n"
            f"Price: ${price:.2f}\n"
            f"Threshold ({direction}): ${threshold:.2f}"
            f"{extra}\n"
            f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
        send_telegram(message)
        alert_state["alerted_date"] = today
        state[alert_key] = alert_state
        print(f"[{alert_key}]: alert sent.")
    else:
        if alert_state.get("alerted_date") != today:
            alert_state.pop("alerted_date", None)
            state[alert_key] = alert_state
        print(f"[{alert_key}]: condition not met, no alert.")


def main() -> None:
    config = load_config()
    state = load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    price_cache = {}

    for entry in config:
        try:
            check_ticker(entry, state, today, price_cache)
        except Exception as e:
            print(f"Error checking {entry.get('ticker')}: {e}")

    save_state(state)


if __name__ == "__main__":
    main()
