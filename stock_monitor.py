import json
import os
import requests
import yfinance as yf


# =========================
# 設定
# =========================

TARGETS = {
    "3635": 1700,
    "5032": 3200
}

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
STATE_FILE = "state.json"


# =========================
# Discord Webhook確認
# =========================

if not WEBHOOK_URL:
    raise ValueError("Discord Webhook URLが設定されていません")


# =========================
# 状態を読み込む
# =========================

with open(STATE_FILE, "r", encoding="utf-8") as f:
    state = json.load(f)


# =========================
# Discord通知
# =========================

def send_discord(message):
    data = {
        "content": message
    }

    response = requests.post(
        WEBHOOK_URL,
        json=data,
        timeout=10
    )

    response.raise_for_status()


# =========================
# 株価チェック
# =========================

for code, target_price in TARGETS.items():

    ticker = yf.Ticker(f"{code}.T")

    price = ticker.fast_info["last_price"]
    price = float(price)

    print(f"{code} 現在価格：{price:.2f}円")
    print(f"{code} 設定価格：{target_price}円")

    # 設定価格以下
    if price <= target_price:

        # まだ通知していない場合
        if not state[code]["notified"]:

            message = (
                f"🚨🚨 株価アラート 🚨🚨\n\n"
                f"{code} が設定価格以下になりました！\n\n"
                f"現在価格：{price:.2f}円\n"
                f"設定価格：{target_price}円"
            )

            send_discord(message)

            state[code]["notified"] = True

            print(f"{code} → Discord通知しました！")

        else:
            print(f"{code} → 通知済みなので今回は通知しません。")

    # 設定価格より上
    else:

        if state[code]["notified"]:

            state[code]["notified"] = False

            print(
                f"{code} → 設定価格を上回ったため、"
                f"通知状態をリセットしました。"
            )

        else:
            print(f"{code} → 条件外です。")


# =========================
# 状態を保存
# =========================

with open(STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(
        state,
        f,
        ensure_ascii=False,
        indent=4
    )

print("株価チェック完了！")