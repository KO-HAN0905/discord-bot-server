import discord
from discord.ext import commands
import os
import sys
from config import DISCORD_BOT_TOKEN, PREFIX
import asyncio
from utils.bot_utils import setup_logging, BotUtils, bot_logger
from datetime import datetime

# 로깅 시스템 초기화
logger = setup_logging()
logger.info("=" * 60)
logger.info(f"봇 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("=" * 60)

# 자동 업데이트 확인
try:
    from updater import auto_update_on_startup
    logger.info("자동 업데이트 시스템 로드 성공")
    auto_update_on_startup()
except ImportError:
    logger.warning("자동 업데이트 모듈을 찾을 수 없습니다.")
except Exception as e:
    logger.warning(f"자동 업데이트 오류: {e}")

# 중복 실행 방지
if os.path.exists('.bot_running'):
    logger.error("봇이 이미 실행 중입니다. 기존 프로세스를 종료해주세요.")
    print("⚠️ 봇이 이미 실행 중입니다. 기존 프로세스를 종료해주세요.")
    sys.exit(1)

# 실행 플래그 생성
open('.bot_running', 'w').close()
logger.info("봇 실행 플래그 생성")

# 봇 초기화
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # 멤버 정보 접근
intents.guilds = True   # 서버 정보 접근
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.start_time = datetime.now()  # 시작 시간 저장
logger.info(f"봇 초기화 완료 - Prefix: {PREFIX}")

# 이벤트: 봇 준비됨
@bot.event
async def on_ready():
    logger.info(f"{bot.user}가 로그인했습니다!")
    logger.info(f"봇 ID: {bot.user.id}")
    logger.info(f"연결된 서버 수: {len(bot.guilds)}")
    logger.info(f"총 사용자 수: {sum(g.member_count for g in bot.guilds)}")
     (고도화)
@bot.event
async def on_command_error(ctx, error):
    # 명령어 찾을 수 없음
    if isinstance(error, commands.CommandNotFound):
        return  # 무시 (로그만)
    
    # 쿨다운
    elif isinstance(error, commands.CommandOnCooldown):
        await BotUtils.send_warning_embed(
            ctx,
            "쿨다운",
            f"이 명령어는 **{error.retry_after:.1f}초** 후에 다시 사용할 수 있습니다."
        )
    
    # 권한 부족
    elif isinstance(error, commands.MissingPermissions):
        missing_perms = ", ".join(error.missing_permissions)
        await BotUtils.send_error_embed(
            ctx,
            "권한 부족",
            f"이 명령어를 사용하려면 다음 권한이 필요합니다:\n**{missing_perms}**"
        )
    
    # 봇 권한 부족
    logger.info("Cogs 로딩 시작...")
    loaded = 0
    failed = 0
    
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"✓ {filename} 로드 성공")
                print(f"[OK] {filename} 로드됨")
                loaded += 1
            except Exception as e:
                logger.error(f"✗ {filename} 로드 실패: {e}", exc_info=True)
                print(f"[ERROR] {filename} 로드 실패: {e}")
                failed += 1
    
    logger.info(f"Cogs 로딩 완료 - 성공: {loaded}, 실패: {failed}")
    print(f"\n📊 Cogs 로딩 결과: {loaded}개 성공, {failed}개 실패\n"
    elif isinstance(error, commands.MissingRequiredArgument):
        await BotUtils.send_error_embed(
            ctx,
            "인자 부족",
            f"필수 인자 `{error.param.name}`이(가) 누락되었습니다.\n"
            f"사용법: `!help {ctx.command.name}`"
        )
    logger.info("사용자에 의해 봇이 종료되었습니다.")
        print("\n봇이 종료되었습니다.")
        if os.path.exists('.bot_running'):
            os.remove('.bot_running')
    except Exception as e:
        logger.critical(f"치명적 오류 발생: {e}", exc_info=True)
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists('.bot_running'):
            os.remove('.bot_running')
    finally:
        logger.info("=" * 60)
        logger.info(f"봇 종료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60
    # 기타 오류
    else:
        logger.error(f"예상치 못한 오류: {error}", exc_info=error)
        await BotUtils.send_error_embed(
            ctx,
            "오류 발생",
            f"명령어 실행 중 오류가 발생했습니다.\n"
            f"오류가 계속되면 관리자에게 문의하세요.\n\n"
            f"오류 코드: `{type(error).__name__}`",
            log=False  # 이미 로깅됨
        
    )

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
