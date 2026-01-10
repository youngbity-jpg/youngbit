import requests
from pykrx import stock
import datetime
import sys

TELEGRAM_TOKEN = "8269518800:AAEYOa2ymfu8xOCKlPeM1HBGmZWZ4O6sLKQ"
TELEGRAM_CHAT_ID = "6186312115"


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data, timeout=10)


def get_top_trading_value():
    today = datetime.datetime.now().strftime("%Y%m%d")

    # ✅ 시장 구분 인자 없음 (이게 핵심)
    df = stock.get_market_trading_value_by_date(today, today)

    if df.empty:
        return "📊 거래대금 데이터가 없습니다.\n(휴장일일 수 있습니다)"

    df = df.sort_values(by="거래대금", ascending=False).head(20)

    msg = f"📊 [오늘의 거래대금 상위 20]\n({today})\n\n"

    for i, (code, row) in enumerate(df.iterrows(), 1):
        name = stock.get_market_ticker_name(code)
        value = int(row["거래대금"] / 100_000_000)
        msg += f"{i}. {name} : {value:,}억\n"

    return msg


def main():
    msg = get_top_trading_value()
    send_telegram_message(msg)
    print("Telegram message sent")


if __name__ == "__main__":
    main()
    print("=== SCRIPT END ===")
    sys.exit(0)
