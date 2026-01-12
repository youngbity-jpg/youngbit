import requests
import datetime
import os
import sys

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data, timeout=10)

def get_naver_trading_value_top():
    api_url = "https://stock.naver.com/api/domestic/market/stock/default"
    params = {
        "tradeType": "KRX",
        "marketType": "ALL",
        "orderType": "priceTop",
        "startIdx": 0,
        "pageSize": 100
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(api_url, headers=headers, params=params, timeout=10)
    data = res.json()

    if "stocks" not in data:
        return "📊 거래대금 데이터가 없습니다."

    stocks = data["stocks"]
    if not stocks:
        return "📊 거래대금 데이터가 없습니다."

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"📊 장중 거래대금 TOP 20\n({now} 기준)\n\n"

    # 거래대금이 이미 orderType=priceTop 으로 정렬되어 있음
    for i, stock in enumerate(stocks[:20], 1):
        name = stock.get("stockName", "")
        value = stock.get("accumulatedTradingValue", "")
        msg += f"{i}. {name} : {value}\n"

    return msg

def main():
    message = get_naver_trading_value_top()
    send_telegram_message(message)
    print("=== SCRIPT END ===")

if __name__ == "__main__":
    main()
    sys.exit(0)
