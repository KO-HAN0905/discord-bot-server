import discord
from discord.ext import commands
import os
import sys
from config import DISCORD_BOT_TOKEN, PREFIX
import asyncio

# 중복 실행 방지
if os.path.exists('.bot_running'):
    print("⚠️ 봇이 이미 실행 중입니다. 기존 프로세스를 종료해주세요.")
    sys.exit(1)

# 실행 플래그 생성
open('.bot_running', 'w').close()

# 봇 초기화
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# 이벤트: 봇 준비됨
@bot.event
async def on_ready():
    print(f"[OK] {bot.user}가 로그인했습니다!")
    print(f"봇 준비됨: {bot.user.name} ({bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help - 도움말"))

# 이벤트: 오류 처리
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ 알 수 없는 명령어입니다. `!help`로 명령어를 확인하세요.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ 인자가 부족합니다. `!help {ctx.command.name}`으로 사용법을 확인하세요.")
    else:
        print(f"오류: {error}")
        await ctx.send(f"❌ 오류가 발생했습니다: {error}")

# Cogs 로드
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"[OK] {filename} 로드됨")
            except Exception as e:
                print(f"[ERROR] {filename} 로드 실패: {e}")
                import traceback
                traceback.print_exc()

# 메인 함수
async def main():
    async with bot:
        await load_cogs()
        try:
            await bot.start(DISCORD_BOT_TOKEN)
        finally:
            # 종료 시 플래그 파일 삭제
            if os.path.exists('.bot_running'):
                os.remove('.bot_running')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n봇이 종료되었습니다.")
        if os.path.exists('.bot_running'):
            os.remove('.bot_running')
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists('.bot_running'):
            os.remove('.bot_running')
