import requests
import os
import datetime
import json

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })

def parse_value(value_str):
    # "3,504,671백만" → 3504671
    return int(value_str.replace(",", "").replace("백만", "").strip())

def get_top_trading_value():
    url = (
        "https://stock.naver.com/api/domestic/market/stock/default"
        "?tradeType=KRX"
        "&marketType=ALL"
        "&orderType=valueTop"
        "&startIdx=0"
        "&pageSize=50"
    )

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://stock.naver.com/"
    }

    res = requests.get(url, headers=headers)

    raw = json.loads(res.text)   # 🔥 핵심 수정
    data = raw.get("result", {}).get("stocks", [])

    if not data:
        return None

    stocks = []
    for s in data:
        try:
            value = parse_value(s["accumulatedTradingValue"])
            stocks.append({
                "name": s["stockName"],
                "market": s["stockExchangeType"]["nameKor"],
                "price": s["closePrice"],
                "rate": s["fluctuationsRatio"],
                "value": value,
                "value_str": s["accumulatedTradingValue"]
            })
        except:
            continue

    stocks = sorted(stocks, key=lambda x: x["value"], reverse=True)[:20]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"📊 거래대금 상위 20 (장중)\n⏰ {now}\n\n"

    for i, s in enumerate(stocks, 1):
        msg += (
            f"{i}. {s['name']} ({s['market']})\n"
            f"   {s['price']}원 ({s['rate']}%) | {s['value_str']}\n"
        )

    return msg

def main():
    # 주말 자동 스킵
    if datetime.datetime.today().weekday() >= 5:
        print("주말 → 종료")
        return

    msg = get_top_trading_value()
    if not msg:
        send_telegram("❌ 거래대금 데이터를 불러오지 못했습니다.")
        return

    send_telegram(msg)
    print("Telegram message sent")

if __name__ == "__main__":
    main()
