import requests
from bs4 import BeautifulSoup
import datetime

# ==========================================
# [설정] 텔레그램 토큰 & ID
# ==========================================
TELEGRAM_TOKEN = "8269518800:AAEYOa2ymfu8xOCKlPeM1HBGmZWZ4O6sLKQ"
TELEGRAM_CHAT_ID = "6186312115"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

def get_top_trading_value():
    urls = {
        "KOSPI": "https://finance.naver.com/sise/sise_value.naver?sosok=0",
        "KOSDAQ": "https://finance.naver.com/sise/sise_value.naver?sosok=1"
    }

    results = []

    for market, url in urls.items():
        res = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=10
)

        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.select("table.type_2 tr")
        count = 0

        for row in rows:
            cols = row.select("td")
            if len(cols) < 10:
                continue

            name = cols[1].text.strip()
            price = cols[2].text.strip()
            rate = cols[4].text.strip()
            value_amt = cols[9].text.strip()

            try:
                value_int = int(value_amt.replace(",", ""))
            except:
                value_int = 0

            results.append({
                "market": market,
                "name": name,
                "price": price,
                "rate": rate,
                "value_str": value_amt,
                "value_int": value_int
            })

            count += 1
            if count >= 15:
                break

    top_stocks = sorted(results, key=lambda x: x["value_int"], reverse=True)[:20]

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"📊 [거래대금 상위 20]\n({now} 기준)\n\n"

    for i, s in enumerate(top_stocks, 1):
        msg += f"{i}. {s['name']} ({s['market']})\n"
        msg += f"   └ {s['price']}원 ({s['rate']}) | {s['value_str']}백만\n"

    if not top_stocks:
    return "📊 오늘은 장이 열리지 않아 거래대금 데이터가 없습니다."

    return msg

if __name__ == "__main__":
    message = get_top_trading_value()
    send_telegram_message(message)

print("=== SCRIPT END ===")
