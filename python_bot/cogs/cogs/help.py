# -*- coding: utf-8 -*-
import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="도움말", help="전체 명령어 도움말")
    async def help_command(self, ctx):
        """전체 도움말 표시"""
        embed = discord.Embed(
            title="🎮 디스코드 봇 사용법",
            description="**가장 쉬운 방법:**\n`!메뉴` 명령어를 입력하고 버튼을 클릭하세요!\n\n"
                       "모든 기능을 버튼으로 간편하게 사용할 수 있습니다.",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="⭐ 빠른 시작",
            value="`!메뉴` - 모든 기능 버튼으로 접근\n"
                  "`!시작` - !메뉴와 동일",
            inline=False
        )
        
        embed.add_field(
            name="📋 주요 기능",
            value="🔔 **알람** - 시간별 알람 설정\n"
                  "📋 **과제** - 일일/주간 과제 관리\n"
                  "📅 **D-Day** - 날짜 카운트다운\n"
                  "📰 **뉴스** - 게임 뉴스 확인\n"
                  "🎮 **원스휴먼** - 메메틱 정보 조회\n"
                  "⚙️ **설정** - 채널 설정 (관리자)",
            inline=False
        )
        
        embed.add_field(
            name="🔧 유용한 명령어",
            value="`!정보` - 봇 정보\n"
                  "`!메메틱` - 원스휴먼 메메틱 정보\n"
                  "`!대시보드` - 기능 요약\n"
                  "`!동기화` - 봇 재부팅 (관리자)",
            inline=False
        )
        
        embed.set_footer(text="💡 Tip: !메뉴 명령어 하나면 모든 기능을 사용할 수 있습니다!")
        await ctx.send(embed=embed)

    @commands.command(name="정보", help="봇 정보")
    async def info(self, ctx):
        """봇 정보 표시"""
        embed = discord.Embed(
            title="🤖 봇 정보",
            description="다목적 디스코드 관리 봇",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="버전", value="1.0.0", inline=True)
        embed.add_field(name="작성자", value="YourName", inline=True)
        embed.add_field(name="기능", value="5개", inline=True)
        
        embed.add_field(
            name="주요 기능",
            value="- 알람 관리\n- 게임 뉴스\n- 과제 관리\n- D-Day 관리\n- 데이터 동기화",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="대시보드", aliases=["dashboard"], help="전체 기능 한눈에 보기")
    async def dashboard(self, ctx):
        """대시보드 - 모든 기능을 한눈에"""
        embed = discord.Embed(
            title="📊 봇 기능 대시보드",
            description="**`!메뉴`** 명령어로 모든 기능에 버튼으로 접근할 수 있습니다!",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="🎯 메인 메뉴",
            value="`!메뉴` - 모든 기능을 버튼으로",
            inline=False
        )
        
        embed.add_field(
            name="🔔 알람",
            value="시간별 알람 설정 및 관리\n매일 반복 또는 1회 알람",
            inline=True
        )
        
        embed.add_field(
            name="📋 과제",
            value="일일/주간 과제 관리\n진행도 추적 (0~100%)",
            inline=True
        )
        
        embed.add_field(
            name="📅 D-Day",
            value="중요 날짜 카운트다운\nExcel 자동 저장",
            inline=True
        )
        
        embed.add_field(
            name="📰 뉴스",
            value="최신 게임 소식\n6시간마다 자동 업데이트",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ 설정",
            value="채널 설정 관리\n(관리자 전용)",
            inline=True
        )
        
        embed.add_field(
            name="🔧 시스템",
            value="`!동기화` - 봇 재부팅\n`!정보` - 봇 정보",
            inline=True
        )
        
        embed.set_footer(text="💡 가장 쉬운 사용법: !메뉴")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
