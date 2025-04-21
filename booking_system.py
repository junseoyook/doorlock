import requests
import json
from datetime import datetime, timedelta
import sqlite3
import schedule
import time

class BookingSystem:
    def __init__(self, token, device_id):
        self.token = token
        self.device_id = device_id
        self.init_db()

    def init_db(self):
        # 데이터베이스 초기화
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS bookings
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             customer_phone TEXT,
             booking_time DATETIME,
             remote_url TEXT,
             is_used INTEGER DEFAULT 0)
        ''')
        conn.commit()
        conn.close()

    def create_temporary_remote(self):
        url = f"https://api.switch-bot.com/v1.1/devices/{self.device_id}/commands/temporary"
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            if result["statusCode"] == 100:
                return result["body"]["url"]
            return None
        except:
            return None

    def add_booking(self, customer_phone, booking_time):
        # URL 생성
        remote_url = self.create_temporary_remote()
        if not remote_url:
            return False, "URL 생성 실패"

        # 예약 정보 저장
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO bookings (customer_phone, booking_time, remote_url)
                VALUES (?, ?, ?)
            ''', (customer_phone, booking_time, remote_url))
            conn.commit()
            return True, remote_url
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def get_today_bookings(self):
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        c.execute('''
            SELECT customer_phone, booking_time, remote_url, is_used
            FROM bookings
            WHERE date(booking_time) = date(?)
        ''', (today.isoformat(),))
        bookings = c.fetchall()
        conn.close()
        return bookings

    def mark_url_as_used(self, customer_phone, booking_time):
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute('''
            UPDATE bookings
            SET is_used = 1
            WHERE customer_phone = ? AND booking_time = ?
        ''', (customer_phone, booking_time))
        conn.commit()
        conn.close()

def main():
    # SwitchBot API 설정
    TOKEN = "YOUR_API_TOKEN"
    DEVICE_ID = "YOUR_DEVICE_ID"
    
    booking_system = BookingSystem(TOKEN, DEVICE_ID)
    
    # 예시: 예약 추가
    def add_test_booking():
        current_time = datetime.now()
        customer_phone = "010-1234-5678"
        success, result = booking_system.add_booking(customer_phone, current_time)
        if success:
            print(f"예약 성공! URL: {result}")
            # SMS나 이메일로 URL 전송 로직 추가 가능
        else:
            print(f"예약 실패: {result}")

    # 매일 예약 현황 체크
    def check_daily_bookings():
        bookings = booking_system.get_today_bookings()
        print(f"오늘의 예약 현황: {len(bookings)}건")
        for booking in bookings:
            print(f"고객: {booking[0]}, 시간: {booking[1]}, URL 사용여부: {'사용완료' if booking[3] else '미사용'}")

    # 스케줄러 설정
    schedule.every().day.at("00:01").do(check_daily_bookings)
    
    # 스케줄러 실행
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 