# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
import json
import os
from contextlib import suppress
from gtts import gTTS
import asyncio
from collections import deque

class TTSSettingModal(Modal, title="TTS 채널 설정"):
    """TTS 채팅 채널 설정 모달"""
    
    channel_id = TextInput(
        label="채널 ID",
        placeholder="채널 ID를 입력하세요 (예: 1234567890123456789)",
        required=True,
        min_length=17,
        max_length=20
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel_id.value)
            channel = interaction.client.get_channel(channel_id)
            
            if channel is None:
                await interaction.response.send_message(
                    "[ERROR] 채널을 찾을 수 없습니다. 채널 ID를 확인하세요.",
                    ephemeral=True
                )
                return
            
            settings = self.cog.load_settings()
            settings["tts_channel_id"] = channel_id
            self.cog.save_settings(settings)
            
            await interaction.response.send_message(
                f"[OK] TTS 채널이 <#{channel_id}>로 설정되었습니다.",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "[ERROR] 채널 ID는 숫자여야 합니다.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"[ERROR] 오류 발생: {e}",
                ephemeral=True
            )

class TTSView(View):
    """TTS 관리 UI 버튼"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @discord.ui.button(label="[SETTING] 채널 설정", style=discord.ButtonStyle.primary)
    async def setting_button(self, interaction: discord.Interaction, button: Button):
        """채널 설정"""
        modal = TTSSettingModal(self.cog)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="[ON] TTS 켜기", style=discord.ButtonStyle.success)
    async def enable_button(self, interaction: discord.Interaction, button: Button):
        """TTS 활성화"""
        settings = self.cog.load_settings()
        
        if "tts_channel_id" not in settings or settings["tts_channel_id"] == 0:
            await interaction.response.send_message(
                "[WARNING] 먼저 TTS 채널을 설정하세요.",
                ephemeral=True
            )
            return
        
        settings["tts_enabled"] = True
        self.cog.save_settings(settings)
        
        await interaction.response.send_message(
            "[OK] TTS 기능이 활성화되었습니다.",
            ephemeral=True
        )
    
    @discord.ui.button(label="[OFF] TTS 끄기", style=discord.ButtonStyle.danger)
    async def disable_button(self, interaction: discord.Interaction, button: Button):
        """TTS 비활성화"""
        settings = self.cog.load_settings()
        settings["tts_enabled"] = False
        self.cog.save_settings(settings)
        
        await interaction.response.send_message(
            "[OK] TTS 기능이 비활성화되었습니다.",
            ephemeral=True
        )
    
    @discord.ui.button(label="[INFO] 상태 확인", style=discord.ButtonStyle.secondary)
    async def status_button(self, interaction: discord.Interaction, button: Button):
        """상태 확인"""
        settings = self.cog.load_settings()
        
        tts_enabled = settings.get("tts_enabled", False)
        tts_channel_id = settings.get("tts_channel_id", 0)
        queue_size = len(self.cog.message_queue)
        
        status_text = "[ON]" if tts_enabled else "[OFF]"
        channel_text = f"<#{tts_channel_id}>" if tts_channel_id > 0 else "설정 안됨"
        
        embed = discord.Embed(
            title="TTS 상태",
            color=discord.Color.green() if tts_enabled else discord.Color.red()
        )
        embed.add_field(name="상태", value=status_text, inline=False)
        embed.add_field(name="채팅 채널", value=channel_text, inline=False)
        embed.add_field(name="대기 메시지", value=f"{queue_size}개", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/tts_settings.json"
        self.voice_dir = "data/voice_tts"
        self.message_queue = deque()
        self.is_playing = False
        self.ffmpeg_path = "F:/A/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
        
        self.ensure_files()
    
    def ensure_files(self):
        """파일 및 디렉토리 생성"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        os.makedirs(self.voice_dir, exist_ok=True)
        
        if not os.path.exists(self.settings_file):
            self.save_settings({
                "tts_enabled": False,
                "tts_channel_id": 0,
                "tts_speed": 1.0
            })
    
    def load_settings(self):
        """설정 로드"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "tts_enabled": False,
                "tts_channel_id": 0,
                "tts_speed": 1.0
            }
    
    def save_settings(self, settings):
        """설정 저장"""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    
    def generate_tts_file(self, text):
        """TTS 파일 생성"""
        try:
            # 파일명 안전화 (특수문자 제거)
            safe_name = "".join(c for c in text[:30] if c.isalnum() or c in ('_', '-'))
            if not safe_name:
                safe_name = "tts_temp"
            
            voice_file = f"{self.voice_dir}/{safe_name}.mp3"
            
            # 이미 존재하면 재사용
            if os.path.exists(voice_file):
                return voice_file
            
            # gTTS로 음성 파일 생성
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(voice_file)
            
            print(f"[MUSIC] 음성 파일 생성: {voice_file}")
            return voice_file
        except Exception as e:
            print(f"[ERROR] 음성 파일 생성 실패: {e}")
            return None
    
    async def play_tts(self, guild, text, author_name):
        """TTS 음성 재생"""
        try:
            # 음성 채널 찾기
            voice_client = None
            for vc in self.bot.voice_clients:
                if vc.guild == guild:
                    voice_client = vc
                    break
            
            # 음성 채널이 없으면 첫 번째 사람이 있는 음성 채널에 입장
            if voice_client is None:
                target_channel = None
                for channel in guild.voice_channels:
                    if len(channel.members) > 0:
                        target_channel = channel
                        break
                
                if not target_channel:
                    print("[WARNING] 음성 채널에 사람이 없습니다.")
                    return
                
                try:
                    voice_client = await target_channel.connect()
                    print(f"[OK] 음성 채널 입장: {target_channel.name}")
                except Exception as e:
                    print(f"[ERROR] 음성 채널 입장 실패: {e}")
                    return
            
            # 사용자 닉네임 추가 (예: "(사용자) 메시지 내용")
            tts_text = f"{author_name}, {text}"
            
            # TTS 파일 생성
            voice_file = self.generate_tts_file(tts_text)
            if not voice_file:
                return
            
            if not os.path.exists(voice_file):
                print(f"[ERROR] 음성 파일이 존재하지 않음: {voice_file}")
                return
            
            if voice_client and not voice_client.is_playing():
                try:
                    # ffmpeg 경로 확인
                    ffmpeg_path = self.ffmpeg_path
                    if not os.path.exists(ffmpeg_path):
                        ffmpeg_path = "ffmpeg"
                    
                    print(f"[SPEAKER] 음성 재생 시작: ({author_name}) {text}")
                    audio_source = discord.FFmpegPCMAudio(voice_file, executable=ffmpeg_path)
                    voice_client.play(
                        audio_source,
                        after=lambda e: self._voice_callback(tts_text, e)
                    )
                    
                    # 재생 완료 대기
                    max_wait = 30
                    waited = 0
                    while voice_client.is_playing() and waited < max_wait:
                        await asyncio.sleep(0.5)
                        waited += 0.5
                    
                    print(f"[OK] 음성 재생 완료: ({author_name}) {text}")
                except Exception as e:
                    print(f"[ERROR] 음성 재생 실패: {e}")
        
        except Exception as e:
            print(f"[ERROR] TTS 재생 중 오류: {e}")
    
    def _voice_callback(self, text, error):
        """음성 재생 콜백"""
        if error is None:
            print(f"[OK] TTS '{text}' 재생 완료")
        else:
            print(f"[ERROR] 재생 오류 '{text}': {error}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """메시지 감지 및 TTS 재생"""
        # 봇 자신의 메시지는 무시
        if message.author == self.bot.user:
            return
        
        # DM은 무시
        if message.guild is None:
            return
        
        settings = self.load_settings()
        
        # TTS 비활성화 상태면 무시
        if not settings.get("tts_enabled", False):
            return
        
        # 설정된 채널이 아니면 무시
        if message.channel.id != settings.get("tts_channel_id", 0):
            return
        
        # 메시지 큐에 추가
        self.message_queue.append((message.guild, message.content, message.author))
        
        # 큐 처리 시작
        await self.process_queue()
    
    async def process_queue(self):
        """메시지 큐 처리"""
        if self.is_playing or len(self.message_queue) == 0:
            return
        
        self.is_playing = True
        
        while len(self.message_queue) > 0:
            guild, text, author = self.message_queue.popleft()
            
            # 텍스트 정제
            if len(text) > 200:
                text = text[:200] + "..."
            
            # 서버 프로필 닉네임 또는 사용자명 사용
            author_display_name = author.display_name
            print(f"[MUSIC] TTS 큐 처리: {author_display_name} - {text}")
            await self.play_tts(guild, text, author_display_name)
            await asyncio.sleep(1)  # 메시지 간 간격
        
        self.is_playing = False
    
    @commands.group(name="tts", help="TTS 음성 채팅")
    async def tts(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="TTS 도움말", color=discord.Color.blue())
            embed.add_field(name="UI 관리", value="`!ttsui` - 버튼식 UI 사용", inline=False)
            embed.add_field(name="채널 설정", value="`!tts 설정 <채널ID>`", inline=False)
            embed.add_field(name="켜기", value="`!tts 켜기`", inline=False)
            embed.add_field(name="끄기", value="`!tts 끄기`", inline=False)
            embed.add_field(name="상태", value="`!tts 상태`", inline=False)
            embed.add_field(name="설명", value="설정된 채팅 채널에 메시지를 보내면 봇이 음성 채널에서 자동으로 읽어줍니다.", inline=False)
            await ctx.send(embed=embed)
    
    @commands.command(name="ttsui", help="TTS UI 표시")
    async def tts_ui(self, ctx_or_interaction):
        """TTS 관리 UI 표시"""
        embed = discord.Embed(
            title="[MUSIC] TTS 음성 채팅",
            description="아래 버튼을 클릭하여 TTS를 관리하세요.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="기능",
            value="[SETTING] **채널 설정** - TTS 채팅 채널 설정\n"
                  "[ON] **켜기** - TTS 기능 활성화\n"
                  "[OFF] **끄기** - TTS 기능 비활성화\n"
                  "[INFO] **상태** - 현재 상태 확인",
            inline=False
        )
        
        view = TTSView(self)
        
        # Context 또는 Interaction에 따라 다르게 응답
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)
    
    @tts.command(name="설정", help="TTS 채널 설정")
    async def set_channel(self, ctx, channel_id: int):
        """TTS 채널 설정"""
        try:
            channel = ctx.bot.get_channel(channel_id)
            
            if channel is None:
                await ctx.send("[ERROR] 채널을 찾을 수 없습니다.")
                return
            
            settings = self.load_settings()
            settings["tts_channel_id"] = channel_id
            self.save_settings(settings)
            
            await ctx.send(f"[OK] TTS 채널이 <#{channel_id}>로 설정되었습니다.")
        except Exception as e:
            await ctx.send(f"[ERROR] 오류: {e}")
    
    @tts.command(name="켜기", help="TTS 활성화")
    async def enable(self, ctx):
        """TTS 활성화"""
        settings = self.load_settings()
        
        if settings.get("tts_channel_id", 0) == 0:
            await ctx.send("[WARNING] 먼저 TTS 채널을 설정하세요: `!tts 설정 <채널ID>`")
            return
        
        settings["tts_enabled"] = True
        self.save_settings(settings)
        
        await ctx.send("[OK] TTS 기능이 활성화되었습니다.")
    
    @tts.command(name="끄기", help="TTS 비활성화")
    async def disable(self, ctx):
        """TTS 비활성화"""
        settings = self.load_settings()
        settings["tts_enabled"] = False
        self.save_settings(settings)
        
        await ctx.send("[OK] TTS 기능이 비활성화되었습니다.")
    
    @tts.command(name="상태", help="TTS 상태 확인")
    async def status(self, ctx):
        """상태 확인"""
        settings = self.load_settings()
        
        tts_enabled = settings.get("tts_enabled", False)
        tts_channel_id = settings.get("tts_channel_id", 0)
        queue_size = len(self.message_queue)
        
        status_text = "[ON]" if tts_enabled else "[OFF]"
        channel_text = f"<#{tts_channel_id}>" if tts_channel_id > 0 else "설정 안됨"
        
        embed = discord.Embed(
            title="TTS 상태",
            color=discord.Color.green() if tts_enabled else discord.Color.red()
        )
        embed.add_field(name="상태", value=status_text, inline=False)
        embed.add_field(name="채팅 채널", value=channel_text, inline=False)
        embed.add_field(name="대기 메시지", value=f"{queue_size}개", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    try:
        await bot.add_cog(TTS(bot))
        print("[OK] tts.py 설정 완료")
    except Exception as e:
        print(f"[ERROR] tts.py 설정 실패: {e}")
        import traceback
        traceback.print_exc()
