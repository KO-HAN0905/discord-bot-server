# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button, Select
from contextlib import suppress
from config import ADMIN_PASSWORD
import json
import os

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

# 채널 설정 모달
class ChannelSettingModal(Modal):
    """채널 설정 모달"""
    
    def __init__(self, cog, setting_type):
        super().__init__(title=f"{'게임 뉴스' if setting_type == 'news' else 'D-Day'} 채널 설정")
        self.cog = cog
        self.setting_type = setting_type
        
        self.channel_id_input = TextInput(
            label="채널 ID",
            placeholder="채널 ID를 입력하세요 (예: 1234567890123456789)",
            required=True,
            min_length=17,
            max_length=20
        )
        self.add_item(self.channel_id_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """모달 제출 처리"""
        try:
            channel_id = int(self.channel_id_input.value)
            channel = interaction.guild.get_channel(channel_id)
            
            if not channel:
                embed = discord.Embed(
                    title="❌ 오류",
                    description="해당 ID의 채널을 찾을 수 없습니다.\n채널을 우클릭하고 'ID 복사'를 선택하세요.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if not isinstance(channel, discord.TextChannel):
                embed = discord.Embed(
                    title="❌ 오류",
                    description="텍스트 채널만 설정할 수 있습니다.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            settings = self.cog.load_settings()
            if self.setting_type == "news":
                settings["news_channel_id"] = channel_id
                channel_name = "게임 뉴스"
            else:
                settings["dday_channel_id"] = channel_id
                channel_name = "D-Day"
            
            self.cog.save_settings(settings)
            
            embed = discord.Embed(
                title="✅ 채널 설정 완료",
                description=f"**{channel_name} 채널:** {channel.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # 설정된 채널에 알림 메시지
            with suppress(Exception):
                await channel.send(f"✅ 이 채널이 **{channel_name} 채널**로 설정되었습니다!")
                
        except ValueError:
            embed = discord.Embed(
                title="❌ 오류",
                description="올바른 채널 ID를 입력해주세요.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ 오류",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# 채널 설정 UI 버튼 뷰
class SettingsView(View):
    """채널 설정 관리 UI 버튼"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)  # 5분 타임아웃
        self.cog = cog
    
    @discord.ui.button(label="📰 뉴스 채널 설정", style=discord.ButtonStyle.primary, row=0)
    async def set_news_channel_button(self, interaction: discord.Interaction, button: Button):
        """뉴스 채널 설정 버튼"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ 권한 부족",
                description="관리자 권한이 필요합니다.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        async def show_channel_setting(interaction, authenticated):
            if authenticated:
                modal = ChannelSettingModal(self.cog, "news")
                await interaction.response.send_modal(modal)
        
        modal = AdminPasswordModal(show_channel_setting)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📅 D-Day 채널 설정", style=discord.ButtonStyle.primary, row=0)
    async def set_dday_channel_button(self, interaction: discord.Interaction, button: Button):
        """D-Day 채널 설정 버튼"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ 권한 부족",
                description="관리자 권한이 필요합니다.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        async def show_channel_setting(interaction, authenticated):
            if authenticated:
                modal = ChannelSettingModal(self.cog, "dday")
                await interaction.response.send_modal(modal)
        
        modal = AdminPasswordModal(show_channel_setting)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 현재 설정 확인", style=discord.ButtonStyle.secondary, row=1)
    async def check_settings_button(self, interaction: discord.Interaction, button: Button):
        """현재 설정 확인 버튼"""
        settings = self.cog.load_settings()
        
        embed = discord.Embed(
            title="⚙️ 현재 채널 설정",
            description="봇이 사용하는 채널 정보입니다.",
            color=discord.Color.blue()
        )
        
        # 뉴스 채널
        if (news_channel := interaction.guild.get_channel(settings.get("news_channel_id", 0))):
            embed.add_field(
                name="📰 게임 뉴스 채널",
                value=f"{news_channel.mention}\n`ID: {news_channel.id}`",
                inline=False
            )
        else:
            embed.add_field(
                name="📰 게임 뉴스 채널",
                value="⚠️ 설정되지 않음",
                inline=False
            )
        
        # D-Day 채널
        if (dday_channel := interaction.guild.get_channel(settings.get("dday_channel_id", 0))):
            embed.add_field(
                name="📅 D-Day 채널",
                value=f"{dday_channel.mention}\n`ID: {dday_channel.id}`",
                inline=False
            )
        else:
            embed.add_field(
                name="📅 D-Day 채널",
                value="⚠️ 설정되지 않음",
                inline=False
            )
        
        embed.set_footer(text="💡 채널 ID를 얻으려면: 채널 우클릭 → 'ID 복사'")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 설정 초기화", style=discord.ButtonStyle.danger, row=1)
    async def reset_settings_button(self, interaction: discord.Interaction, button: Button):
        """설정 초기화 버튼"""
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ 권한 부족",
                description="관리자 권한이 필요합니다.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        default_settings = {
            "news_channel_id": 0,
            "dday_channel_id": 0,
            "admin_id": 0
        }
        self.cog.save_settings(default_settings)
        
        embed = discord.Embed(
            title="✅ 설정 초기화 완료",
            description="모든 채널 설정이 초기화되었습니다.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="❓ 도움말", style=discord.ButtonStyle.success, row=2)
    async def help_button(self, interaction: discord.Interaction, button: Button):
        """도움말 버튼"""
        embed = discord.Embed(
            title="💡 채널 설정 도움말",
            description="채널 ID를 얻는 방법과 설정 가이드입니다.",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="1️⃣ 채널 ID 복사하기",
            value="① 디스코드 설정 → 앱 설정 → 고급 → **개발자 모드** 활성화\n"
                  "② 원하는 채널 우클릭 → **ID 복사**\n"
                  "③ 복사한 ID를 모달에 붙여넣기",
            inline=False
        )
        
        embed.add_field(
            name="2️⃣ 뉴스 채널 설정",
            value="게임 뉴스가 자동으로 발송될 채널을 지정합니다.\n"
                  "**📰 뉴스 채널 설정** 버튼을 눌러 채널 ID를 입력하세요.",
            inline=False
        )
        
        embed.add_field(
            name="3️⃣ D-Day 채널 설정",
            value="D-Day 공지가 발송될 채널을 지정합니다.\n"
                  "**📅 D-Day 채널 설정** 버튼을 눌러 채널 ID를 입력하세요.",
            inline=False
        )
        
        embed.add_field(
            name="4️⃣ 권한 안내",
            value="⚠️ 채널 설정 및 초기화는 **관리자 권한**이 필요합니다.\n"
                  "✅ 현재 설정 확인은 모든 사용자가 가능합니다.",
            inline=False
        )
        
        embed.set_footer(text="문제가 있다면 !도움말 명령어를 입력하세요")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/settings.json"
        self.ensure_settings()

    def ensure_settings(self):
        """설정 파일 초기화"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        if not os.path.exists(self.settings_file):
            default_settings = {
                "news_channel_id": 0,
                "dday_channel_id": 0,
                "admin_id": 0
            }
            self.save_settings(default_settings)

    def load_settings(self):
        """설정 로드"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"news_channel_id": 0, "dday_channel_id": 0, "admin_id": 0}

    def save_settings(self, settings):
        """설정 저장"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    @commands.command(name="설정ui", help="채널 설정 UI 표시")
    async def settings_ui(self, ctx_or_interaction):
        """채널 설정 UI 버튼 표시"""
        embed = discord.Embed(
            title="⚙️ 채널 설정",
            description="아래 버튼을 클릭하여 채널을 설정하세요.\n"
                       "💡 **개발자 모드**를 활성화하고 채널을 우클릭하여 ID를 복사할 수 있습니다.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📰 뉴스 채널",
            value="게임 뉴스가 자동으로 발송될 채널",
            inline=True
        )
        
        embed.add_field(
            name="📅 D-Day 채널",
            value="D-Day 공지가 발송될 채널",
            inline=True
        )
        
        embed.add_field(
            name="\u200b",
            value="\u200b",
            inline=True
        )
        
        # 현재 설정 표시
        settings = self.load_settings()
        
        # guild 가져오기
        guild = ctx_or_interaction.guild
        
        news_channel = guild.get_channel(settings.get("news_channel_id", 0)) if guild else None
        dday_channel = guild.get_channel(settings.get("dday_channel_id", 0)) if guild else None
        
        current_settings = "**현재 설정:**\n"
        current_settings += f"📰 뉴스: {news_channel.mention if news_channel else '❌ 미설정'}\n"
        current_settings += f"📅 D-Day: {dday_channel.mention if dday_channel else '❌ 미설정'}"
        
        embed.add_field(
            name="📊 현재 상태",
            value=current_settings,
            inline=False
        )
        
        embed.set_footer(text="💡 관리자만 설정을 변경할 수 있습니다 | 도움말을 보려면 ❓ 버튼 클릭")
        
        view = SettingsView(self)
        
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

    @commands.group(name="채널설정", help="채널 설정 관리 (관리자 전용)")
    @commands.has_permissions(administrator=True)
    async def channel_settings(self, ctx):
        """채널 설정 그룹 명령어"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="⚙️ 채널 설정 도움말", color=discord.Color.blue())
            embed.add_field(name="UI 관리", value="`!설정ui` - 버튼식 UI 사용 (권장)", inline=False)
            embed.add_field(name="뉴스 채널 설정", value="`!채널설정 뉴스 <채널>`", inline=False)
            embed.add_field(name="D-Day 채널 설정", value="`!채널설정 디데이 <채널>`", inline=False)
            embed.add_field(name="현재 설정 확인", value="`!채널설정 확인`", inline=False)
            await ctx.send(embed=embed)

    @channel_settings.command(name="뉴스", help="게임 뉴스 채널 설정")
    @commands.has_permissions(administrator=True)
    async def set_news_channel(self, ctx, channel: discord.TextChannel):
        """게임 뉴스 채널 설정"""
        try:
            settings = self.load_settings()
            settings["news_channel_id"] = channel.id
            self.save_settings(settings)
            
            embed = discord.Embed(
                title="✅ 뉴스 채널 설정됨",
                description=f"게임 뉴스 채널: {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            await channel.send("✅ 이 채널이 게임 뉴스 채널로 설정되었습니다!")
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @channel_settings.command(name="디데이", help="D-Day 채널 설정")
    @commands.has_permissions(administrator=True)
    async def set_dday_channel(self, ctx, channel: discord.TextChannel):
        """D-Day 채널 설정"""
        try:
            settings = self.load_settings()
            settings["dday_channel_id"] = channel.id
            self.save_settings(settings)
            
            embed = discord.Embed(
                title="✅ D-Day 채널 설정됨",
                description=f"D-Day 채널: {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            await channel.send("✅ 이 채널이 D-Day 채널로 설정되었습니다!")
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @channel_settings.command(name="확인", help="현재 설정 확인")
    @commands.has_permissions(administrator=True)
    async def check_settings(self, ctx):
        """현재 설정 확인"""
        try:
            settings = self.load_settings()
            
            embed = discord.Embed(title="⚙️ 현재 채널 설정", color=discord.Color.blue())
            
            # 뉴스 채널
            if (news_channel := self.bot.get_channel(settings["news_channel_id"])):
                embed.add_field(
                    name="📰 게임 뉴스 채널",
                    value=f"{news_channel.mention} (ID: {settings['news_channel_id']})",
                    inline=False
                )
            elif settings["news_channel_id"] > 0:
                embed.add_field(
                    name="📰 게임 뉴스 채널",
                    value=f"ID: {settings['news_channel_id']} (채널을 찾을 수 없음)",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📰 게임 뉴스 채널",
                    value="⚠️ 설정되지 않음",
                    inline=False
                )
            
            # D-Day 채널
            if (dday_channel := self.bot.get_channel(settings["dday_channel_id"])):
                embed.add_field(
                    name="📅 D-Day 채널",
                    value=f"{dday_channel.mention} (ID: {settings['dday_channel_id']})",
                    inline=False
                )
            elif settings["dday_channel_id"] > 0:
                embed.add_field(
                    name="📅 D-Day 채널",
                    value=f"ID: {settings['dday_channel_id']} (채널을 찾을 수 없음)",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📅 D-Day 채널",
                    value="⚠️ 설정되지 않음",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    @channel_settings.command(name="리셋", help="채널 설정 초기화")
    @commands.has_permissions(administrator=True)
    async def reset_settings(self, ctx):
        """채널 설정 초기화"""
        try:
            default_settings = {
                "news_channel_id": 0,
                "dday_channel_id": 0,
                "admin_id": 0
            }
            self.save_settings(default_settings)
            
            embed = discord.Embed(
                title="✅ 설정이 초기화되었습니다",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ 오류: {e}")

    def get_news_channel(self):
        """뉴스 채널 가져오기"""
        settings = self.load_settings()
        channel_id = settings.get("news_channel_id", 0)
        return self.bot.get_channel(channel_id) if channel_id > 0 else None

    def get_dday_channel(self):
        """D-Day 채널 가져오기"""
        settings = self.load_settings()
        channel_id = settings.get("dday_channel_id", 0)
        return self.bot.get_channel(channel_id) if channel_id > 0 else None

async def setup(bot):
    await bot.add_cog(Settings(bot))
