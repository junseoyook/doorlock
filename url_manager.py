import requests
import json
from datetime import datetime, timedelta
import sqlite3

class URLManager:
    def __init__(self, token, device_id):
        self.token = token
        self.device_id = device_id
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect('customer_urls.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS customer_urls
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             customer_phone TEXT,
             remote_url TEXT,
             created_at DATETIME,
             expires_at DATETIME,
             is_valid INTEGER DEFAULT 1)
        ''')
        conn.commit()
        conn.close()

    def create_temporary_remote(self):
        """SwitchBot API를 통해 임시 URL 생성"""
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
        except Exception as e:
            print(f"URL 생성 중 오류 발생: {str(e)}")
            return None

    def create_customer_url(self, customer_phone, valid_hours=24):
        """고객별 URL 생성 및 만료 시간 설정"""
        # 기존 유효한 URL이 있는지 확인
        conn = sqlite3.connect('customer_urls.db')
        c = conn.cursor()
        c.execute('''
            SELECT remote_url, expires_at 
            FROM customer_urls 
            WHERE customer_phone = ? AND is_valid = 1
            AND datetime(expires_at) > datetime('now')
        ''', (customer_phone,))
        existing_url = c.fetchone()
        
        if existing_url:
            conn.close()
            return {
                'url': existing_url[0],
                'expires_at': existing_url[1],
                'status': 'existing'
            }

        # 새 URL 생성
        remote_url = self.create_temporary_remote()
        if not remote_url:
            conn.close()
            return None

        # URL 정보 저장
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=valid_hours)
        
        try:
            c.execute('''
                INSERT INTO customer_urls 
                (customer_phone, remote_url, created_at, expires_at, is_valid)
                VALUES (?, ?, ?, ?, 1)
            ''', (customer_phone, remote_url, created_at, expires_at))
            conn.commit()
            
            return {
                'url': remote_url,
                'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'new'
            }
        except Exception as e:
            print(f"데이터베이스 저장 중 오류 발생: {str(e)}")
            return None
        finally:
            conn.close()

    def check_url_validity(self, customer_phone):
        """고객의 URL 유효성 확인"""
        conn = sqlite3.connect('customer_urls.db')
        c = conn.cursor()
        c.execute('''
            SELECT remote_url, expires_at 
            FROM customer_urls 
            WHERE customer_phone = ? AND is_valid = 1
            AND datetime(expires_at) > datetime('now')
        ''', (customer_phone,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'valid': True,
                'url': result[0],
                'expires_at': result[1]
            }
        return {'valid': False}

    def invalidate_url(self, customer_phone):
        """고객의 URL 무효화"""
        conn = sqlite3.connect('customer_urls.db')
        c = conn.cursor()
        c.execute('''
            UPDATE customer_urls
            SET is_valid = 0
            WHERE customer_phone = ?
        ''', (customer_phone,))
        conn.commit()
        conn.close()

def main():
    # SwitchBot API 설정
    TOKEN = "YOUR_API_TOKEN"
    DEVICE_ID = "YOUR_DEVICE_ID"
    
    # URL 관리자 초기화
    url_manager = URLManager(TOKEN, DEVICE_ID)
    
    # 예시: 새로운 고객 URL 생성 (24시간 유효)
    customer_phone = "010-1234-5678"
    result = url_manager.create_customer_url(customer_phone, valid_hours=24)
    
    if result:
        if result['status'] == 'new':
            print(f"새로운 URL이 생성되었습니다!")
        else:
            print(f"이미 유효한 URL이 존재합니다.")
        print(f"URL: {result['url']}")
        print(f"만료 시간: {result['expires_at']}")
    else:
        print("URL 생성에 실패했습니다.")

if __name__ == "__main__":
    main() 