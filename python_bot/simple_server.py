"""
간단한 Flask API 서버 - 모바일 앱 테스트용
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """봇 상태 조회"""
    return jsonify({
        'status': 'online',
        'message': 'Bot is running on F:\\A',
        'server': 'test-server'
    })

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    """봇 시작 (테스트)"""
    return jsonify({'message': '봇이 이미 실행 중입니다 (F:\\A)'})

@app.route('/api/bot/stop', methods=['POST'])
def stop_bot():
    """봇 중지 (테스트)"""
    return jsonify({'message': '봇 중지 기능은 프로덕션에서 사용 가능합니다'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """로그 조회 (테스트)"""
    return jsonify({
        'logs': [
            {'id': '1', 'timestamp': '2026-01-28 10:00:00', 'level': 'info', 'message': '봇 시작됨'},
            {'id': '2', 'timestamp': '2026-01-28 10:01:00', 'level': 'info', 'message': 'Discord 연결 성공'},
            {'id': '3', 'timestamp': '2026-01-28 10:02:00', 'level': 'info', 'message': 'API 서버 실행 중'}
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'ok', 'message': 'API 서버가 정상 작동 중입니다'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    print(f"\n✅ Flask API 서버 시작: http://{host}:{port}")
    print(f"📱 모바일 앱에서 연결하세요: http://localhost:{port}/api\n")
    app.run(host=host, port=port, debug=True)
