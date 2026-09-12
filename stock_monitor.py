import json
import os
import requests
import yfinance as yf


# =========================
# 設定
# =========================

TARGETS = {
    "3635": 1550,
    "5032": 3000
}

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
STATE_FILE = "state.json"


# =========================
# Webhook確認
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


    # =========================
    # ① 通常の株価報告
    # =========================

    normal_message = (
        f"📊 株価定期報告 📊\n\n"
        f"{code}の現在価格：{price:.2f}円"
    )

    send_discord(normal_message)


    # =========================
    # ② 設定価格以下なら特別アラート
    # =========================

    if price <= target_price:

        if not state[code]["notified"]:

            alert_message = (
                f"🚨🚨 株価アラート 🚨🚨\n\n"
                f"{code}が設定価格以下になりました！\n\n"
                f"現在価格：{price:.2f}円\n"
                f"設定価格：{target_price}円"
            )

            send_discord(alert_message)

            state[code]["notified"] = True

            print(f"{code} → 特別アラートを送信しました！")

        else:

            print(
                f"{code} → アラート済みなので、"
                f"特別通知はしません。"
            )


    # =========================
    # ③ 設定価格より上に戻ったら
    #    再通知できる状態に戻す
    # =========================

    else:

        if state[code]["notified"]:

            state[code]["notified"] = False

            print(
                f"{code} → 設定価格より上に戻ったため、"
                f"アラート状態をリセットしました。"
            )


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