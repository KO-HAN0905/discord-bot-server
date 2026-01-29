"""
Railway 배포용 통합 서버
Discord 봇 + Flask API를 동시에 실행
"""
import os
import sys
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
import discord
from discord.ext import commands

# 환경 변수 로드
load_dotenv()

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 봇 상태 저장
bot_status = {
    'running': False,
    'start_time': None,
    'user': None
}

# Discord 봇 이벤트
@bot.event
async def on_ready():
    global bot_status
    bot_status['running'] = True
    bot_status['user'] = str(bot.user)
    print(f'✅ Discord 봇 연결됨: {bot.user}')

# Cogs 로드
async def load_cogs():
    """봇 기능 모듈(Cogs) 로드"""
    cogs_dir = 'cogs'
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✓ Loaded: {filename}')
                except Exception as e:
                    print(f'✗ Failed to load {filename}: {e}')

# Flask API 라우트
@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """봇 상태 조회"""
    return jsonify({
        'status': 'online' if bot_status['running'] else 'offline',
        'user': bot_status['user'],
        'latency': round(bot.latency * 1000) if bot.is_ready() else None,
        'guild_count': len(bot.guilds) if bot.is_ready() else 0
    })

@app.route('/api/bot/guilds', methods=['GET'])
def get_guilds():
    """봇이 참여한 서버 목록"""
    if not bot.is_ready():
        return jsonify({'error': 'Bot is not ready'}), 503
    
    guilds = [{'id': str(g.id), 'name': g.name, 'member_count': g.member_count} 
              for g in bot.guilds]
    return jsonify({'guilds': guilds, 'count': len(guilds)})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """로그 조회"""
    limit = request.args.get('limit', 50, type=int)
    # TODO: 실제 로그 파일에서 읽기
    return jsonify({
        'logs': [
            {'id': '1', 'timestamp': '2026-01-28 12:00:00', 'level': 'info', 'message': '봇 시작됨'},
            {'id': '2', 'timestamp': '2026-01-28 12:01:00', 'level': 'info', 'message': 'Discord 연결 성공'},
        ]
    })

# Discord 봇 실행 (백그라운드 스레드)
def run_discord_bot():
    """Discord 봇을 별도 스레드에서 실행"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print('❌ DISCORD_BOT_TOKEN이 설정되지 않았습니다!')
        return
    
    # asyncio 이벤트 루프 설정
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Cogs 로드
    loop.run_until_complete(load_cogs())
    
    # 봇 실행
    try:
        loop.run_until_complete(bot.start(token))
    except KeyboardInterrupt:
        loop.run_until_complete(bot.close())
    finally:
        loop.close()

# 메인 실행
if __name__ == '__main__':
    # 환경 변수 확인
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print('❌ 오류: DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다!')
        print('Railway 대시보드에서 환경 변수를 설정하세요.')
        sys.exit(1)
    
    print('🚀 서버 시작 중...')
    
    # Discord 봇을 백그라운드 스레드에서 실행
    bot_thread = threading.Thread(target=run_discord_bot, daemon=True)
    bot_thread.start()
    
    # Flask API 서버 실행
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f'🌐 API 서버: http://{host}:{port}')
    print(f'📱 모바일 앱 연결 대기 중...')
    
    app.run(host=host, port=port, debug=False)
