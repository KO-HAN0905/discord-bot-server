"""
Flask API 서버 - 모바일 앱과의 통신
"""

import os
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

# Discord 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # API 라우트
    @app.route('/api/bot/status', methods=['GET'])
    def get_bot_status():
        """봇 상태 조회"""
        return jsonify({
            'status': 'online' if bot.user else 'offline',
            'user': str(bot.user) if bot.user else None,
            'latency': round(bot.latency * 1000) if bot.user else None
        })
    
    @app.route('/api/bot/start', methods=['POST'])
    def start_bot():
        """봇 시작"""
        if bot.user:
            return jsonify({'message': '봇이 이미 실행 중입니다'}), 400
        
        # 봇 시작 (별도 스레드에서)
        threading.Thread(target=run_bot, daemon=True).start()
        return jsonify({'message': '봇 시작 중...'})
    
    @app.route('/api/bot/stop', methods=['POST'])
    def stop_bot():
        """봇 중지"""
        if not bot.user:
            return jsonify({'message': '봇이 실행 중이 아닙니다'}), 400
        
        # 봇 중지
        async def close_bot():
            await bot.close()
        
        import asyncio
        asyncio.run(close_bot())
        return jsonify({'message': '봇 중지됨'})
    
    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        """로그 조회"""
        limit = request.args.get('limit', 50, type=int)
        # TODO: 로그 파일에서 읽기
        return jsonify({'logs': []})
    
    @app.route('/api/command', methods=['POST'])
    def execute_command():
        """명령어 실행"""
        command = request.json.get('command')
        # TODO: 봇에 명령어 전달
        return jsonify({'result': f'명령어 실행: {command}'})
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """헬스 체크"""
        return jsonify({'status': 'ok'})
    
    return app

def run_bot():
    """Discord 봇 실행"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
