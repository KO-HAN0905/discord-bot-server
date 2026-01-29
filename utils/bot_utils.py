"""
🛡️ 봇 유틸리티 - 오류 처리, 권한 검증, 로깅
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime
import os
from typing import Optional, Callable
import functools
import traceback

# 로깅 설정
def setup_logging():
    """고급 로깅 시스템 설정"""
    
    # logs 디렉토리 생성
    os.makedirs("logs", exist_ok=True)
    
    # 로거 생성
    logger = logging.getLogger('discord_bot')
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러 (일별 로그)
    log_filename = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 에러 전용 핸들러
    error_filename = f"logs/error_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.FileHandler(error_filename, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷 설정
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

# 전역 로거
bot_logger = setup_logging()


class BotUtils:
    """봇 유틸리티 클래스"""
    
    @staticmethod
    def log_command(ctx: commands.Context, success: bool = True, error: str = None):
        """명령어 실행 로그"""
        if success:
            bot_logger.info(
                f"명령어 실행: {ctx.command.name} | "
                f"사용자: {ctx.author} ({ctx.author.id}) | "
                f"서버: {ctx.guild.name if ctx.guild else 'DM'}"
            )
        else:
            bot_logger.error(
                f"명령어 오류: {ctx.command.name} | "
                f"사용자: {ctx.author} | "
                f"오류: {error}"
            )
    
    @staticmethod
    async def send_error_embed(
        ctx: commands.Context, 
        title: str, 
        description: str,
        log: bool = True
    ):
        """오류 임베드 전송"""
        embed = discord.Embed(
            title=f"❌ {title}",
            description=description,
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"명령어: {ctx.command.name}")
        
        if log:
            bot_logger.error(f"{title}: {description}")
        
        await ctx.send(embed=embed)
    
    @staticmethod
    async def send_success_embed(
        ctx: commands.Context,
        title: str,
        description: str,
        log: bool = True
    ):
        """성공 임베드 전송"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        if log:
            bot_logger.info(f"{title}: {description}")
        
        await ctx.send(embed=embed)
    
    @staticmethod
    async def send_warning_embed(
        ctx: commands.Context,
        title: str,
        description: str
    ):
        """경고 임베드 전송"""
        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
    
    @staticmethod
    def validate_input(value: str, min_len: int = 1, max_len: int = 100) -> bool:
        """입력 값 검증"""
        if not value or not isinstance(value, str):
            return False
        value = value.strip()
        return min_len <= len(value) <= max_len


def require_permissions(**perms):
    """권한 데코레이터 (향상된 오류 메시지)"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            # 권한 확인
            missing_perms = []
            for perm, value in perms.items():
                if not getattr(ctx.author.guild_permissions, perm, False) == value:
                    missing_perms.append(perm)
            
            if missing_perms:
                perms_text = ", ".join([p.replace('_', ' ').title() for p in missing_perms])
                await BotUtils.send_error_embed(
                    ctx,
                    "권한 부족",
                    f"이 명령어를 사용하려면 다음 권한이 필요합니다:\n**{perms_text}**"
                )
                return
            
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def advanced_error_handler(func):
    """고급 오류 핸들러 데코레이터"""
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        try:
            return await func(self, ctx, *args, **kwargs)
        
        except commands.MissingRequiredArgument as e:
            await BotUtils.send_error_embed(
                ctx,
                "인자 부족",
                f"필수 인자 `{e.param.name}`이(가) 누락되었습니다.\n"
                f"사용법: `!help {ctx.command.name}`"
            )
        
        except commands.BadArgument as e:
            await BotUtils.send_error_embed(
                ctx,
                "잘못된 인자",
                f"인자 형식이 올바르지 않습니다.\n{str(e)}"
            )
        
        except commands.CommandOnCooldown as e:
            await BotUtils.send_warning_embed(
                ctx,
                "쿨다운",
                f"이 명령어는 {e.retry_after:.1f}초 후에 다시 사용할 수 있습니다."
            )
        
        except discord.Forbidden:
            await BotUtils.send_error_embed(
                ctx,
                "권한 오류",
                "봇이 이 작업을 수행할 권한이 없습니다."
            )
        
        except discord.HTTPException as e:
            await BotUtils.send_error_embed(
                ctx,
                "Discord API 오류",
                f"Discord API 오류가 발생했습니다: {e.text}"
            )
        
        except Exception as e:
            # 상세 오류 로깅
            error_msg = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            bot_logger.error(f"예상치 못한 오류:\n{error_msg}")
            
            await BotUtils.send_error_embed(
                ctx,
                "오류 발생",
                f"명령어 실행 중 오류가 발생했습니다.\n"
                f"오류가 계속되면 관리자에게 문의하세요.\n\n"
                f"오류 코드: `{type(e).__name__}`"
            )
    
    return wrapper


class InputValidator:
    """입력 값 검증기"""
    
    @staticmethod
    def validate_text(text: str, min_len: int = 1, max_len: int = 200) -> tuple[bool, str]:
        """텍스트 검증"""
        if not text:
            return False, "텍스트가 비어있습니다."
        
        text = text.strip()
        
        if len(text) < min_len:
            return False, f"최소 {min_len}자 이상이어야 합니다."
        
        if len(text) > max_len:
            return False, f"최대 {max_len}자를 초과할 수 없습니다."
        
        return True, text
    
    @staticmethod
    def validate_number(value: str, min_val: int = None, max_val: int = None) -> tuple[bool, Optional[int]]:
        """숫자 검증"""
        try:
            num = int(value)
            
            if min_val is not None and num < min_val:
                return False, None
            
            if max_val is not None and num > max_val:
                return False, None
            
            return True, num
        
        except ValueError:
            return False, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """파일명 안전화"""
        # 위험한 문자 제거
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        return filename[:100]  # 길이 제한


class ProgressTracker:
    """진행 상황 추적기"""
    
    def __init__(self, ctx: commands.Context, total: int, title: str = "작업 진행 중"):
        self.ctx = ctx
        self.total = total
        self.current = 0
        self.title = title
        self.message = None
    
    async def start(self):
        """진행 시작"""
        embed = discord.Embed(
            title=f"⏳ {self.title}",
            description=self._get_progress_bar(),
            color=discord.Color.blue()
        )
        self.message = await self.ctx.send(embed=embed)
    
    async def update(self, current: int):
        """진행 업데이트"""
        self.current = current
        
        if self.message:
            embed = discord.Embed(
                title=f"⏳ {self.title}",
                description=self._get_progress_bar(),
                color=discord.Color.blue()
            )
            await self.message.edit(embed=embed)
    
    async def complete(self, success_msg: str = "완료"):
        """완료"""
        if self.message:
            embed = discord.Embed(
                title=f"✅ {success_msg}",
                description=f"총 {self.total}개 항목 처리 완료",
                color=discord.Color.green()
            )
            await self.message.edit(embed=embed)
    
    def _get_progress_bar(self) -> str:
        """진행 바 생성"""
        percent = (self.current / self.total * 100) if self.total > 0 else 0
        filled = int(percent / 10)
        bar = "█" * filled + "░" * (10 - filled)
        return f"{bar} {percent:.1f}% ({self.current}/{self.total})"


# 사용 예시 데코레이터
def log_and_handle_errors(func):
    """로깅 + 오류 처리 통합"""
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        try:
            BotUtils.log_command(ctx, success=True)
            return await func(self, ctx, *args, **kwargs)
        except Exception as e:
            BotUtils.log_command(ctx, success=False, error=str(e))
            raise
    return wrapper
