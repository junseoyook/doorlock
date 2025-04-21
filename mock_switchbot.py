import uuid
from datetime import datetime, timedelta

class MockSwitchBot:
    def __init__(self):
        self.devices = {}
        self.temporary_urls = {}
    
    def create_temporary_url(self, device_id):
        """임시 URL 생성 모의 구현"""
        temp_url = f"mock-switchbot://{uuid.uuid4()}"
        self.temporary_urls[temp_url] = {
            'device_id': device_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=24)
        }
        return {
            "statusCode": 100,
            "body": {
                "url": temp_url
            },
            "message": "success"
        }
    
    def control_device(self, device_id, command):
        """디바이스 제어 모의 구현"""
        if command not in ['lock', 'unlock']:
            return {
                "statusCode": 400,
                "message": "Invalid command"
            }
        
        return {
            "statusCode": 100,
            "body": {},
            "message": "success"
        } 