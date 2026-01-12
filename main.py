import requests
from bs4 import BeautifulSoup
import datetime
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def get_naver_trading_value_top():
    url = "https://stock.naver.com/market/stock/kr/stocklist/priceTop"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tbody tr")

    if not rows:
        return "거래대금 데이터가 없습니다.\n(네이버 페이지 구조 변경 가능)"

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"📊 장중 거래대금 TOP (네이버)\n({now} 기준)\n\n"

    rank = 1
    for row in rows[:20]:
        cols = row.select("td")
        if len(cols) < 6:
            continue

        name = cols[1].text.strip()
        price = cols[2].text.strip()
        rate = cols[4].text.strip()
        value = cols[5].text.strip()

        msg += f"{rank}. {name}\n"
        msg += f"   └ {price}원 ({rate}) | {value}\n"
        rank += 1

    return msg

def main():
    msg = get_naver_trading_value_top()
    send_telegram_message(msg)
    print("Telegram message sent")
    print("=== SCRIPT END ===")

if __name__ == "__main__":
    main()
