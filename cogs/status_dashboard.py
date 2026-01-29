"""
📊 봇 상태 모니터링 대시보드 Cog
실시간 성능, 통계, 시스템 상태
"""

import discord
from discord.ext import commands
import psutil
import os
from datetime import datetime, timedelta
from utils.bot_utils import BotUtils, advanced_error_handler
from core.cache_manager import memory_cache

class StatusDashboard(commands.Cog):
    """봇 상태 모니터링"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name='상태', aliases=['status', 'health'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @advanced_error_handler
    async def check_status(self, ctx):
        """봇 상태 확인"""
        
        # CPU 및 메모리
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / (1024 * 1024)
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # 가동 시간
        uptime = datetime.now() - self.bot.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # 캐시 통계
        cache_stats = memory_cache.get_stats()
        
        embed = discord.Embed(
            title="📊 봇 상태 대시보드",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # 시스템 정보
        embed.add_field(
            name="⚙️ 시스템",
            value=(
                f"CPU: {cpu_percent:.1f}%\n"
                f"메모리: {memory_mb:.1f} MB\n"
                f"가동시간: {hours}시간 {minutes}분"
            ),
            inline=True
        )
        
        # 서버 정보
        total_members = sum(g.member_count for g in self.bot.guilds)
        embed.add_field(
            name="🌐 연결 정보",
            value=(
                f"서버: {len(self.bot.guilds)}개\n"
                f"사용자: {total_members:,}명\n"
                f"지연: {round(self.bot.latency * 1000)}ms"
            ),
            inline=True
        )
        
        # 캐시 정보
        embed.add_field(
            name="💾 캐시",
            value=(
                f"히트율: {cache_stats['hit_rate']}\n"
                f"항목: {cache_stats['cached_items']}개\n"
                f"크기: {cache_stats['size_estimate_mb']:.2f} MB"
            ),
            inline=True
        )
        
        # Cogs 정보
        loaded_cogs = len(self.bot.cogs)
        embed.add_field(
            name="🔌 모듈",
            value=f"{loaded_cogs}개 로드됨",
            inline=True
        )
        
        # 상태 표시
        if cpu_percent < 50 and memory_mb < 500:
            status = "✅ 정상"
            color = discord.Color.green()
        elif cpu_percent < 80 and memory_mb < 1000:
            status = "⚠️ 주의"
            color = discord.Color.orange()
        else:
            status = "🔴 경고"
            color = discord.Color.red()
        
        embed.add_field(
            name="📈 전체 상태",
            value=status,
            inline=True
        )
        
        embed.color = color
        embed.set_footer(text=f"Python {psutil.PYTHON_VERSION}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='서버목록', aliases=['servers', 'guilds'])
    @commands.is_owner()
    @advanced_error_handler
    async def list_servers(self, ctx):
        """봇이 참여한 서버 목록 (소유자 전용)"""
        
        guilds_info = []
        for guild in sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True):
            guilds_info.append(
                f"**{guild.name}**\n"
                f"  ├ ID: {guild.id}\n"
                f"  ├ 멤버: {guild.member_count:,}명\n"
                f"  └ 생성: {guild.created_at.strftime('%Y-%m-%d')}"
            )
        
        # 페이지네이션 (10개씩)
        pages = [guilds_info[i:i+10] for i in range(0, len(guilds_info), 10)]
        
        for i, page in enumerate(pages, 1):
            embed = discord.Embed(
                title=f"🌐 서버 목록 ({i}/{len(pages)})",
                description="\n\n".join(page),
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"총 {len(self.bot.guilds)}개 서버")
            await ctx.send(embed=embed)
    
    @commands.command(name='통계', aliases=['stats'])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @advanced_error_handler
    async def statistics(self, ctx):
        """전체 통계"""
        
        # 데이터 수집
        total_members = sum(g.member_count for g in self.bot.guilds)
        total_channels = sum(len(g.channels) for g in self.bot.guilds)
        total_roles = sum(len(g.roles) for g in self.bot.guilds)
        
        # 봇 비율
        total_bots = sum(sum(1 for m in g.members if m.bot) for g in self.bot.guilds)
        bot_ratio = (total_bots / total_members * 100) if total_members > 0 else 0
        
        # 명령어 통계 (캐시에서)
        command_count = memory_cache.get('total_commands_executed') or 0
        
        embed = discord.Embed(
            title="📊 전체 통계",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🏢 서버",
            value=f"{len(self.bot.guilds):,}개",
            inline=True
        )
        
        embed.add_field(
            name="👥 사용자",
            value=f"{total_members:,}명",
            inline=True
        )
        
        embed.add_field(
            name="📺 채널",
            value=f"{total_channels:,}개",
            inline=True
        )
        
        embed.add_field(
            name="🎭 역할",
            value=f"{total_roles:,}개",
            inline=True
        )
        
        embed.add_field(
            name="🤖 봇 비율",
            value=f"{bot_ratio:.1f}%",
            inline=True
        )
        
        embed.add_field(
            name="⚡ 명령어 실행",
            value=f"{command_count:,}회",
            inline=True
        )
        
        # 가장 큰 서버
        if self.bot.guilds:
            largest = max(self.bot.guilds, key=lambda g: g.member_count)
            embed.add_field(
                name="👑 최대 서버",
                value=f"{largest.name}\n({largest.member_count:,}명)",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='핑', aliases=['ping', 'latency'])
    @commands.cooldown(2, 5, commands.BucketType.user)
    async def ping(self, ctx):
        """응답 속도 측정"""
        
        # Discord API 지연
        api_latency = round(self.bot.latency * 1000)
        
        # 메시지 전송 시간 측정
        start = datetime.now()
        msg = await ctx.send("🏓 Pong!")
        end = datetime.now()
        
        message_latency = round((end - start).total_seconds() * 1000)
        
        # 임베드 업데이트
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.green() if api_latency < 100 else discord.Color.orange()
        )
        
        embed.add_field(
            name="📡 API 지연",
            value=f"{api_latency}ms",
            inline=True
        )
        
        embed.add_field(
            name="📨 메시지 지연",
            value=f"{message_latency}ms",
            inline=True
        )
        
        # 상태 평가
        if api_latency < 100:
            status = "✅ 매우 빠름"
        elif api_latency < 200:
            status = "🟢 양호"
        elif api_latency < 500:
            status = "🟡 보통"
        else:
            status = "🔴 느림"
        
        embed.add_field(
            name="상태",
            value=status,
            inline=True
        )
        
        await msg.edit(content=None, embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(StatusDashboard(bot))
