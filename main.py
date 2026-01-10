import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime

# ==========================================
# [설정] 본인의 텔레그램 토큰과 ID를 입력하세요
# ==========================================
TELEGRAM_TOKEN = "8269518800:AAEYOa2ymfu8xOCKlPeM1HBGmZWZ4O6sLKQ"
TELEGRAM_CHAT_ID = "6186312115"

def send_telegram_message(message):
    """텔레그램으로 메시지를 보내는 함수"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        print("[전송 완료] 텔레그램 메시지 발송 성공")
    except Exception as e:
        print(f"[전송 실패] {e}")

def get_top_trading_value():
    """네이버 금융에서 거래대금 상위 종목을 크롤링하는 함수"""
    print("데이터 수집 중...")
    
    # 네이버 금융 거래대금 상위 URL (sosok=0: 코스피, sosok=1: 코스닥)
    # 두 시장을 모두 확인하여 합칩니다.
    urls = {
        "KOSPI": "https://finance.naver.com/sise/sise_value.naver?sosok=0",
        "KOSDAQ": "https://finance.naver.com/sise/sise_value.naver?sosok=1"
    }
    
    results = []

    for market, url in urls.items():
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # 테이블 내의 종목 행 가져오기
            rows = soup.select('table.type_2 tr')
            
            count = 0
            for row in rows:
                # 데이터가 있는 행만 추출 (구분선 등 제외)
                cols = row.select('td')
                if len(cols) < 10: 
                    continue
                
                # 종목명 (N번째 td가 종목명인지 확인 필요, 보통 1번째 인덱스)
                name = cols[1].text.strip()
                # 현재가
                price = cols[2].text.strip()
                # 등락률
                rate = cols[4].text.strip().strip()
                # 거래대금 (백만)
                value_amt = cols[9].text.strip()
                
                # 거래대금을 숫자로 변환하여 정렬 목적으로 저장 (쉼표 제거)
                try:
                    value_int = int(value_amt.replace(',', ''))
                except:
                    value_int = 0
                    
                results.append({
                    'market': market,
                    'name': name,
                    'price': price,
                    'rate': rate,
                    'value_str': value_amt,
                    'value_int': value_int
                })
                
                count += 1
                if count >= 15: # 각 시장별 상위 15개씩만 1차 추출
                    break
                    
        except Exception as e:
            print(f"{market} 데이터 수집 중 오류: {e}")

    # 거래대금(value_int) 기준으로 내림차순 정렬 후 상위 20개 자르기
    top_stocks = sorted(results, key=lambda x: x['value_int'], reverse=True)[:20]

    # 메시지 포맷 만들기
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"📊 [오늘의 거래대금 상위 20]\n({today} 기준)\n\n"
    
    for idx, stock in enumerate(top_stocks, 1):
        # 보기 좋게 포맷팅: 1. 삼성전자 (코스피) : 70,000원 (+1.5%) / 5000억
        msg += f"{idx}. {stock['name']} ({stock['market']})\n"
        msg += f"   └ {stock['price']}원 ({stock['rate']}) | {stock['value_str']}백만\n"

    return msg

def job():
    """스케줄러에 의해 실행될 작업"""
    try:
        msg = get_top_trading_value()
        send_telegram_message(msg)
    except Exception as e:
        send_telegram_message(f"오류 발생: {e}")

# ==========================================
# [스케줄링] 매일 12:00에 실행
# ==========================================
schedule.every().day.at("12:00").do(job)

print("🚀 프로그램이 시작되었습니다. 매일 12시에 알림을 보냅니다.")
print("테스트를 위해 지금 즉시 한번 실행해 봅니다...")
job() # 프로그램 시작 시 테스트로 1회 즉시 실행

while True:
    schedule.run_pending()
    time.sleep(1)
