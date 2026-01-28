import os
from dotenv import load_dotenv

load_dotenv()

# 디스코드 봇 토큰
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 채널 ID (기본값 처리)
def safe_int(value, default=0):
    """안전하게 정수로 변환"""
    try:
        return int(value) if value and value.isdigit() else default
    except (ValueError, AttributeError):
        return default

GAME_NEWS_CHANNEL_ID = safe_int(os.getenv("GAME_NEWS_CHANNEL_ID"))
DDAY_CHANNEL_ID = safe_int(os.getenv("DDAY_CHANNEL_ID"))

# 데이터 경로
DATA_DIR = "data"
EXCEL_FILE = os.path.join(DATA_DIR, "dday.xlsx")
DB_FILE = os.path.join(DATA_DIR, "tasks.db")

# 명령어 프리픽스
PREFIX = "!"
# 관리자 비밀번호
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "8458aa")