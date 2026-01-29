#!/usr/bin/env python3
"""
Replit용 디스코드 봇 시작 파일
환경 변수에서 설정을 자동으로 로드합니다.
"""

import os
import sys

# 환경 변수 로드
from dotenv import load_dotenv

# .env 파일이 있으면 로드
if os.path.exists('.env'):
    load_dotenv()

# 필수 환경 변수 확인
required_vars = ['DISCORD_BOT_TOKEN']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ 필수 환경 변수 누락: {', '.join(missing_vars)}")
    print("Replit 'Secrets' 탭에서 설정하거나 .env 파일을 추가하세요")
    sys.exit(1)

print("✅ 환경 변수 로드 완료")

# 원래 bot.py 실행
import bot
