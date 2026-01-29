# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import json
import os
from datetime import datetime

# 게임 뉴스 UI 버튼 뷰
class NewsView(View):
    """게임 뉴스 관리 UI 버튼"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)  # 5분 타임아웃
        self.cog = cog
    
    @discord.ui.button(label="📋 뉴스 목록", style=discord.ButtonStyle.primary)
    async def list_button(self, interaction: discord.Interaction, button: Button):
        """뉴스 목록 보기 버튼"""
        if not self.cog.news_cache:
            embed = discord.Embed(
                title="📰 뉴스 목록",
                description="현재 뉴스를 불러올 수 없습니다.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📰 게임 뉴스",
            color=discord.Color.gold()
        )
        
        for idx, news in enumerate(self.cog.news_cache[:5], 1):
            embed.add_field(
                name=f"{idx}. {news['title']}",
                value=f"{news['description']}\n*{news['date']}*",
                inline=False
            )
        
        embed.set_footer(text=f"총 {len(self.cog.news_cache)}개의 뉴스")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 뉴스 새로고침", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction: discord.Interaction, button: Button):
        """뉴스 새로고침 버튼"""
        try:
            self.cog.news_cache = self.cog.fetch_game_news()
            
            embed = discord.Embed(
                title="✅ 뉴스 새로고침 완료",
                description=f"{len(self.cog.news_cache)}개의 뉴스가 로드되었습니다.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📢 뉴스 공지", style=discord.ButtonStyle.success)
    async def announce_button(self, interaction: discord.Interaction, button: Button):
        """뉴스 공지 버튼"""
        try:
            if not interaction.user.guild_permissions.manage_messages:
                embed = discord.Embed(
                    title="❌ 권한 부족",
                    description="메시지 관리 권한이 필요합니다.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not self.cog.news_cache:
                embed = discord.Embed(
                    title="❌ 뉴스 없음",
                    description="현재 뉴스를 불러올 수 없습니다.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            settings = self.cog.load_settings()
            channel_id = settings.get("news_channel_id", 0)
            
            if channel_id == 0:
                embed = discord.Embed(
                    title="❌ 채널 설정 필요",
                    description="`!채널설정 뉴스 <채널>`로 뉴스 채널을 설정해주세요.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            news_channel = interaction.guild.get_channel(channel_id) if interaction.guild else None
            if not news_channel:
                embed = discord.Embed(
                    title="❌ 채널 찾기 실패",
                    description="설정된 뉴스 채널을 찾을 수 없습니다.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📢 게임 뉴스 공지",
                description="최신 업데이트 정보를 안내해드립니다.",
                color=discord.Color.red()
            )
            
            for idx, news in enumerate(self.cog.news_cache[:3], 1):
                embed.add_field(
                    name=f"{idx}. {news['title']}",
                    value=news['description'],
                    inline=False
                )
            
            embed.set_footer(text=f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            await news_channel.send(embed=embed)
            
            result_embed = discord.Embed(
                title="✅ 뉴스 공지 완료",
                description=f"{news_channel.mention}에 뉴스가 발송되었습니다.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=result_embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class GameNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.news_cache = []
        self.settings_file = "data/settings.json"
        self.update_game_news.start()

    @tasks.loop(hours=6)
    async def update_game_news(self):
        """6시간마다 게임 뉴스 업데이트"""
        try:
            self.news_cache = self.fetch_game_news()
        except Exception as e:
            print(f"뉴스 업데이트 오류: {e}")

    @update_game_news.before_loop
    async def before_update_news(self):
        await self.bot.wait_until_ready()

    def fetch_game_news(self):
        """게임 뉴스 크롤링 (예시 - 실제로는 API 사용)"""
        return [
            {
                "title": "원스휴먼 새로운 에피소드 공개",
                "description": "최신 컨텐츠 업데이트",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "url": "https://game.example.com"
            },
            {
                "title": "대규모 밸런스 패치 예정",
                "description": "다음 주 목요일 점검",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "url": "https://game.example.com"
            }
        ]

    @commands.command(name="뉴스ui", help="뉴스 UI 표시")
    async def news_ui(self, ctx_or_interaction):
        """게임 뉴스 관리 UI 버튼 표시"""
        embed = discord.Embed(
            title="📰 게임 뉴스",
            description="아래 버튼을 클릭하여 뉴스를 관리하세요.",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="기능",
            value="📋 **목록** - 뉴스 목록 보기\n"
                  "🔄 **새로고침** - 뉴스 새로고침\n"
                  "📢 **공지** - 뉴스를 채널에 공지",
            inline=False
        )
        
        view = NewsView(self)
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

    @commands.command(name="게임뉴스", help="최신 게임 뉴스")
    async def game_news(self, ctx):
        """게임 뉴스 출력"""
        if not self.news_cache:
            await ctx.send("현재 뉴스를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")
            return
        
        embed = discord.Embed(
            title="📰 원스휴먼 최신 정보",
            color=discord.Color.gold()
        )
        
        for news in self.news_cache[:5]:  # 최대 5개 뉴스
            embed.add_field(
                name=news["title"],
                value=f"{news['description']}\n*{news['date']}*",
                inline=False
            )
        
        embed.set_footer(text="자동 업데이트됨")
        await ctx.send(embed=embed)

    def load_settings(self):
        """설정 로드"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"news_channel_id": 0, "dday_channel_id": 0}

    @commands.command(name="뉴스공지", help="뉴스를 채널에 공지")
    @commands.has_permissions(manage_messages=True)
    async def announce_news(self, ctx):
        """뉴스를 공지 형식으로 채널에 발송"""
        if not self.news_cache:
            await ctx.send("현재 뉴스를 불러올 수 없습니다.")
            return
        
        settings = self.load_settings()
        channel_id = settings.get("news_channel_id", 0)
        
        if channel_id == 0:
            await ctx.send("❌ 뉴스 채널이 설정되지 않았습니다. `!채널설정 뉴스 <채널>`로 설정해주세요.")
            return
        
        news_channel = self.bot.get_channel(channel_id)
        if not news_channel:
            await ctx.send("❌ 설정된 뉴스 채널을 찾을 수 없습니다.")
            return
        
        embed = discord.Embed(
            title="📢 게임 뉴스 공지",
            description="최신 업데이트 정보를 안내해드립니다.",
            color=discord.Color.red()
        )
        
        for idx, news in enumerate(self.news_cache[:3], 1):
            embed.add_field(
                name=f"{idx}. {news['title']}",
                value=news['description'],
                inline=False
            )
        
        embed.set_footer(text=f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        try:
            await news_channel.send(embed=embed)
            await ctx.send(f"✅ 뉴스가 {news_channel.mention}에 발송되었습니다.")
        except Exception as e:
            await ctx.send(f"❌ 뉴스 발송 실패: {e}")

async def setup(bot):
    # BeautifulSoup이 없으면 스킵
    try:
        await bot.add_cog(GameNews(bot))
    except Exception:
        print("⚠️ GameNews Cog 로드 실패 (beautifulsoup4 설치 필요)")
