# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from config import ADMIN_PASSWORD
import os
import sys

# 관리자 비밀번호 인증 모달
class AdminPasswordModal(Modal, title="관리자 인증"):
    """관리자 비밀번호 인증"""
    
    password = TextInput(
        label="관리자 비밀번호",
        placeholder="비밀번호를 입력하세요",
        required=True,
        min_length=1,
        max_length=100
    )
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.password.value == ADMIN_PASSWORD:
            await self.callback(interaction, True)
        else:
            embed = discord.Embed(
                title="❌ 인증 실패",
                description="비밀번호가 올바르지 않습니다.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# 동기화 인증 버튼 뷰
class SyncAuthView(View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx
    
    @discord.ui.button(label="🔐 비밀번호 입력", style=discord.ButtonStyle.primary)
    async def auth_button(self, interaction: discord.Interaction, button: Button):
        async def perform_sync(modal_interaction, authenticated):
            if not authenticated:
                return
            
            embed = discord.Embed(
                title="🔄 봇 재부팅 중...",
                description="잠시만 기다려주세요.",
                color=discord.Color.orange()
            )
            await modal_interaction.response.send_message(embed=embed)
            
            try:
                for extension in list(self.bot.extensions.keys()):
                    await self.bot.reload_extension(extension)
                
                success_embed = discord.Embed(
                    title="✅ 봇 재부팅 완료!",
                    description="모든 모듈이 성공적으로 재로드되었습니다.",
                    color=discord.Color.green()
                )
                await modal_interaction.followup.send(embed=success_embed)
                
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ 재부팅 실패",
                    description=str(e),
                    color=discord.Color.red()
                )
                await modal_interaction.followup.send(embed=error_embed)
        
        modal = AdminPasswordModal(perform_sync)
        await interaction.response.send_modal(modal)

# 메인 메뉴 UI 버튼 뷰
class MainMenuView(View):
    """메인 메뉴 UI 버튼"""
    
    def __init__(self):
        super().__init__(timeout=3600)  # 1시간 타임아웃 설정
    
    @discord.ui.button(label="🔔 알람", style=discord.ButtonStyle.primary, row=0)
    async def alarm_button(self, interaction: discord.Interaction, button: Button):
        """알람 UI 버튼"""
        # 알람 Cog 가져오기
        if (alarm_cog := interaction.client.get_cog("Alarm")):
            await alarm_cog.alarm_ui(interaction)
        else:
            await interaction.response.send_message("❌ 알람 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="📋 과제", style=discord.ButtonStyle.primary, row=0)
    async def task_button(self, interaction: discord.Interaction, button: Button):
        """과제 UI 버튼"""
        if (task_cog := interaction.client.get_cog("Tasks")):
            await task_cog.tasks_ui(interaction)
        else:
            await interaction.response.send_message("❌ 과제 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="📅 D-Day", style=discord.ButtonStyle.primary, row=0)
    async def dday_button(self, interaction: discord.Interaction, button: Button):
        """D-Day UI 버튼"""
        if (dday_cog := interaction.client.get_cog("DDay")):
            await dday_cog.dday_ui(interaction)
        else:
            await interaction.response.send_message("❌ D-Day 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="📰 뉴스", style=discord.ButtonStyle.primary, row=1)
    async def news_button(self, interaction: discord.Interaction, button: Button):
        """뉴스 UI 버튼"""
        if (news_cog := interaction.client.get_cog("GameNews")):
            await news_cog.news_ui(interaction)
        else:
            await interaction.response.send_message("❌ 뉴스 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="🎮 메메틱", style=discord.ButtonStyle.primary, row=1)
    async def meme_button(self, interaction: discord.Interaction, button: Button):
        """메메틱 UI 버튼"""
        if (meme_cog := interaction.client.get_cog("OnceHuman")):
            await meme_cog.meme_info(interaction)
        else:
            await interaction.response.send_message("❌ 메메틱 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="📊 통계", style=discord.ButtonStyle.primary, row=1)
    async def stats_button(self, interaction: discord.Interaction, button: Button):
        """서버 통계 UI 버튼"""
        if (stats_cog := interaction.client.get_cog("ServerStats")):
            await stats_cog.show_server_stats(interaction)
        else:
            await interaction.response.send_message("❌ 통계 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="🎙️ TTS", style=discord.ButtonStyle.primary, row=1)
    async def tts_button(self, interaction: discord.Interaction, button: Button):
        """TTS UI 버튼"""
        if (tts_cog := interaction.client.get_cog("TTS")):
            await tts_cog.tts_ui(interaction)
        else:
            await interaction.response.send_message("❌ TTS 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="[SETTING] 설정", style=discord.ButtonStyle.secondary, row=2)
    async def settings_button(self, interaction: discord.Interaction, button: Button):
        """설정 UI 버튼"""
        if (settings_cog := interaction.client.get_cog("Settings")):
            await settings_cog.settings_ui(interaction)
        else:
            await interaction.response.send_message("❌ 설정 기능을 사용할 수 없습니다.", ephemeral=True)
    
    @discord.ui.button(label="❓ 도움말", style=discord.ButtonStyle.success, row=2)
    async def help_button(self, interaction: discord.Interaction, button: Button):
        """도움말 버튼"""
        embed = discord.Embed(
            title="💡 빠른 도움말",
            description="각 버튼을 클릭하여 기능을 사용하세요!",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🔔 알람",
            value="시간별 알람을 설정하고 관리합니다.\n매일 반복 또는 1회 알람을 추가할 수 있습니다.",
            inline=False
        )
        
        embed.add_field(
            name="📋 과제",
            value="일일 과제와 주간 과제를 관리합니다.\n진행도를 0~100%로 추적할 수 있습니다.",
            inline=False
        )
        
        embed.add_field(
            name="📅 D-Day",
            value="중요한 날짜까지 남은 기간을 관리합니다.\n자동으로 날짜를 계산하여 표시합니다.",
            inline=False
        )
        
        embed.add_field(
            name="📰 뉴스",
            value="최신 게임 뉴스를 확인합니다.\n설정된 채널에 자동으로 공지할 수 있습니다.",
            inline=False
        )
        
        embed.add_field(
            name="🎮 메메틱",
            value="원스휴먼 메메틱 정보를 조회합니다.\n설치기사별로 필요한 메메틱을 확인할 수 있습니다.",
            inline=False
        )
        
        embed.add_field(
            name="📊 통계",
            value="서버의 멤버, 채널, D-Day 정보를 확인합니다.\n서버 현황을 한눈에 파악할 수 있습니다.",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ 설정",
            value="봇이 사용할 채널을 설정합니다.\n(관리자 권한 필요)",
            inline=False
        )
        
        embed.set_footer(text="💡 더 자세한 정보는 !도움말 명령어를 입력하세요")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="메뉴", aliases=["menu", "시작", "start"], help="메인 메뉴 표시")
    async def menu(self, ctx):
        """메인 메뉴 UI 표시"""
        embed = discord.Embed(
            title="🎮 디스코드 봇 메인 메뉴",
            description="아래 버튼을 클릭하여 원하는 기능을 사용하세요!\n"
                       "모든 기능을 한 번의 클릭으로 간편하게 이용할 수 있습니다.",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="🔔 알람",
            value="시간별 알람 관리",
            inline=True
        )
        
        embed.add_field(
            name="📋 과제",
            value="일일/주간 과제 관리",
            inline=True
        )
        
        embed.add_field(
            name="📅 D-Day",
            value="날짜 카운트다운",
            inline=True
        )
        
        embed.add_field(
            name="📰 뉴스",
            value="게임 뉴스 확인",
            inline=True
        )
        
        embed.add_field(
            name="🎮 메메틱",
            value="메메틱 정보 조회",
            inline=True
        )
        
        embed.add_field(
            name="📊 통계",
            value="서버 통계 확인",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ 설정",
            value="채널 설정 (관리자)",
            inline=True
        )
        
        embed.add_field(
            name="❓ 도움말",
            value="기능 설명 보기",
            inline=True
        )
        
        embed.set_footer(text="💡 간편하게 버튼으로 모든 기능을 사용하세요!")
        
        view = MainMenuView()
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name="동기화", aliases=["sync", "재부팅", "restart", "reload"], help="봇 재부팅 (관리자 전용)")
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx):
        """봇 재부팅 및 동기화"""
        embed = discord.Embed(
            title="🔐 관리자 인증 필요",
            description="봇 재부팅을 위해 비밀번호가 필요합니다.",
            color=discord.Color.gold()
        )
        
        view = SyncAuthView(self.bot, ctx)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Menu(bot))
