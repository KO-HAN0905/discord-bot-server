#!/usr/bin/env python3
"""
Discord Bot 메인 파일
모바일 앱과 연동되는 Flask API 서버와 함께 실행됨
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
if os.path.exists('.env'):
    load_dotenv()

# 필수 환경 변수 확인
required_vars = ['DISCORD_BOT_TOKEN']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"필수 환경 변수 누락: {', '.join(missing_vars)}")
    print("Railway Secrets 탭에서 설정하세요.")
    sys.exit(1)

print("✓ 환경 변수 로드 완료")

# Flask API 서버 시작
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    print(f"🚀 API 서버 시작: {host}:{port}")
    app.run(host=host, port=port, debug=False)
