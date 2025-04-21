from flask import Flask, render_template, jsonify, request
from url_manager import URLManager
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# Mock 설정으로 변경
url_manager = URLManager(token="mock_token", device_id="mock_device")

@app.route('/')
def index():
    return "Door Lock Remote Control Server is running!"

@app.route('/remote/<customer_phone>')
def remote_page(customer_phone):
    try:
        # URL 유효성 확인
        validity = url_manager.check_url_validity(customer_phone)
        if not validity['valid']:
            return render_template('error.html', 
                                message="만료된 또는 유효하지 않은 URL입니다."), 403
        
        return render_template('remote.html', 
                            expires_at=validity['expires_at'])
    except Exception as e:
        app.logger.error(f"Error in remote_page: {str(e)}")
        return render_template('error.html', 
                            message="서버 오류가 발생했습니다."), 500

@app.route('/api/control', methods=['POST'])
def control_device():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'Invalid request data'}), 400
        
        action = data.get('action')
        if action not in ['unlock', 'lock']:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        # Mock response
        success = True
        response_message = f"Door {action}ed successfully (Mock Response)"
        
        return jsonify({
            'success': success,
            'message': response_message
        })
    except Exception as e:
        app.logger.error(f"Error in control_device: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', message="페이지를 찾을 수 없습니다."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="서버 오류가 발생했습니다."), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 