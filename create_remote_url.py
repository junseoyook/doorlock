import requests
import json

def create_temporary_remote(device_id, token):
    url = f"https://api.switch-bot.com/v1.1/devices/{device_id}/commands/temporary"
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result["statusCode"] == 100:
            return result["body"]["url"]
        else:
            return f"Error: {result['message']}"
            
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # SwitchBot API 토큰을 여기에 입력하세요
    TOKEN = "YOUR_API_TOKEN"
    # 디바이스 ID를 여기에 입력하세요
    DEVICE_ID = "YOUR_DEVICE_ID"
    
    remote_url = create_temporary_remote(DEVICE_ID, TOKEN)
    print(f"Temporary Remote URL: {remote_url}") 