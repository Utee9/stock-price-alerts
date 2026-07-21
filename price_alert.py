import os
import json
import requests
from datetime import datetime, timezone

TICKER = os.environ.get("TICKER", "SMH")
THRESHOLD = float(os.environ.get("THRESHOLD", "527"))
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
STATE_FILE = "state.json"


def get_price(ticker: str) -> float:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data["chart"]["result"][0]
    return result["meta"]["regularMarketPrice"]


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()


def main() -> None:
    price = get_price(TICKER)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    state = load_state()

    print(f"{TICKER} price: {price} | threshold: {THRESHOLD}")

    if price >= THRESHOLD:
        if state.get("alerted_date") == today:
            print("Already alerted today, skipping.")
            return
        message = (
            f"🚀 {TICKER} ALERT\n"
            f"Price: ${price:.2f}\n"
            f"Threshold: ${THRESHOLD:.2f}\n"
            f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )
        send_telegram(message)
        state["alerted_date"] = today
        save_state(state)
        print("Alert sent.")
    else:
        # Reset the flag once we're back below threshold on a new day,
        # so a fresh alert fires if it dips and crosses again later.
        if state.get("alerted_date") != today:
            state.pop("alerted_date", None)
            save_state(state)
        print("Below threshold, no alert.")


if __name__ == "__main__":
    main()
