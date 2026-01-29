"""
디스코드 채널 모니터링 Cog
여러 서버/채널의 원스휴먼 정보 수집
"""

import discord
from discord.ext import commands, tasks
import json
import re
from datetime import datetime
from typing import List, Dict

class DiscordMonitor(commands.Cog):
    """디스코드 채널 모니터링"""
    
    def __init__(self, bot):
        self.bot = bot
        self.monitored_channels = self.load_monitored_channels()
        self.keywords = [
            "대미지", "빌드", "공식", "패치", "업데이트",
            "damage", "build", "patch", "update",
            "계산", "DPS", "크리티컬", "무기"
        ]
        self.collected_data = []
        
        # 자동 모니터링 시작
        self.auto_monitor.start()
    
    def cog_unload(self):
        self.auto_monitor.cancel()
    
    def load_monitored_channels(self) -> List[int]:
        """모니터링할 채널 목록 로드"""
        try:
            with open('data/monitored_channels.json', 'r', encoding='utf-8') as f:
                return json.load(f).get('channels', [])
        except FileNotFoundError:
            return []
    
    def save_monitored_channels(self):
        """모니터링 채널 저장"""
        with open('data/monitored_channels.json', 'w', encoding='utf-8') as f:
            json.dump({'channels': self.monitored_channels}, f, indent=2)
    
    @commands.command(name='채널추가')
    @commands.has_permissions(administrator=True)
    async def add_channel(self, ctx, channel: discord.TextChannel = None):
        """모니터링 채널 추가
        
        사용법: !채널추가 #채널명
        """
        channel = channel or ctx.channel
        
        if channel.id in self.monitored_channels:
            await ctx.send(f"❌ {channel.mention}은 이미 모니터링 중입니다.")
            return
        
        self.monitored_channels.append(channel.id)
        self.save_monitored_channels()
        await ctx.send(f"✅ {channel.mention} 모니터링을 시작합니다!")
    
    @commands.command(name='채널제거')
    @commands.has_permissions(administrator=True)
    async def remove_channel(self, ctx, channel: discord.TextChannel = None):
        """모니터링 채널 제거
        
        사용법: !채널제거 #채널명
        """
        channel = channel or ctx.channel
        
        if channel.id not in self.monitored_channels:
            await ctx.send(f"❌ {channel.mention}은 모니터링 중이 아닙니다.")
            return
        
        self.monitored_channels.remove(channel.id)
        self.save_monitored_channels()
        await ctx.send(f"✅ {channel.mention} 모니터링을 중지합니다.")
    
    @commands.command(name='모니터링목록')
    async def list_monitored(self, ctx):
        """모니터링 중인 채널 목록"""
        if not self.monitored_channels:
            await ctx.send("📭 모니터링 중인 채널이 없습니다.")
            return
        
        embed = discord.Embed(
            title="📡 모니터링 채널 목록",
            color=discord.Color.blue()
        )
        
        channels = []
        for channel_id in self.monitored_channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                channels.append(f"✅ {channel.mention} ({channel.guild.name})")
            else:
                channels.append(f"❌ 채널 ID: {channel_id} (접근 불가)")
        
        embed.description = "\n".join(channels) if channels else "채널 없음"
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """메시지 감지 - 실시간 모니터링"""
        # 봇 자신의 메시지 무시
        if message.author.bot:
            return
        
        # 모니터링 대상 채널 확인
        if message.channel.id not in self.monitored_channels:
            return
        
        # 키워드 감지
        content_lower = message.content.lower()
        if any(keyword in content_lower for keyword in self.keywords):
            await self.process_message(message)
    
    async def process_message(self, message):
        """메시지 처리 및 저장"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'server': message.guild.name,
            'channel': message.channel.name,
            'author': str(message.author),
            'content': message.content,
            'attachments': [att.url for att in message.attachments],
            'jump_url': message.jump_url
        }
        
        self.collected_data.append(data)
        
        # 로그 출력
        print(f"[MONITOR] 📌 {message.guild.name} > {message.channel.name}")
        print(f"[MONITOR] 👤 {message.author}: {message.content[:50]}...")
        
        # 데이터 저장 (100개마다)
        if len(self.collected_data) >= 100:
            await self.save_collected_data()
    
    async def save_collected_data(self):
        """수집된 데이터 저장"""
        filename = f"data/collected_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
        
        print(f"[MONITOR] 💾 {len(self.collected_data)}개 데이터 저장: {filename}")
        self.collected_data = []
    
    @tasks.loop(hours=1)
    async def auto_monitor(self):
        """자동 채널 스캔 (1시간마다)"""
        print("[MONITOR] 🔍 자동 스캔 시작...")
        
        for channel_id in self.monitored_channels:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue
            
            try:
                # 최근 50개 메시지 스캔
                messages = [msg async for msg in channel.history(limit=50)]
                
                for message in messages:
                    if message.author.bot:
                        continue
                    
                    content_lower = message.content.lower()
                    if any(keyword in content_lower for keyword in self.keywords):
                        # 중복 체크
                        if not any(d.get('jump_url') == message.jump_url for d in self.collected_data):
                            await self.process_message(message)
                
            except discord.Forbidden:
                print(f"[MONITOR] ❌ 권한 없음: {channel.name}")
            except Exception as e:
                print(f"[MONITOR] ⚠️ 오류: {e}")
        
        # 수집 데이터 저장
        if self.collected_data:
            await self.save_collected_data()
        
        print("[MONITOR] ✅ 자동 스캔 완료")
    
    @auto_monitor.before_loop
    async def before_auto_monitor(self):
        await self.bot.wait_until_ready()
    
    @commands.command(name='수동스캔')
    @commands.has_permissions(administrator=True)
    async def manual_scan(self, ctx, limit: int = 100):
        """현재 채널 수동 스캔
        
        사용법: !수동스캔 [메시지수]
        """
        await ctx.send(f"🔍 최근 {limit}개 메시지 스캔 중...")
        
        count = 0
        messages = [msg async for msg in ctx.channel.history(limit=limit)]
        
        for message in messages:
            if message.author.bot:
                continue
            
            content_lower = message.content.lower()
            if any(keyword in content_lower for keyword in self.keywords):
                await self.process_message(message)
                count += 1
        
        await ctx.send(f"✅ {count}개의 관련 메시지를 수집했습니다!")
    
    @commands.command(name='수집통계')
    async def collection_stats(self, ctx):
        """수집 데이터 통계"""
        embed = discord.Embed(
            title="📊 데이터 수집 통계",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="현재 메모리",
            value=f"{len(self.collected_data)}개",
            inline=True
        )
        
        embed.add_field(
            name="모니터링 채널",
            value=f"{len(self.monitored_channels)}개",
            inline=True
        )
        
        embed.add_field(
            name="키워드",
            value=f"{len(self.keywords)}개",
            inline=True
        )
        
        # 서버별 통계
        server_counts = {}
        for data in self.collected_data:
            server = data.get('server', 'Unknown')
            server_counts[server] = server_counts.get(server, 0) + 1
        
        if server_counts:
            stats = "\n".join([f"• {k}: {v}개" for k, v in server_counts.items()])
            embed.add_field(
                name="서버별 수집량",
                value=stats,
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DiscordMonitor(bot))
