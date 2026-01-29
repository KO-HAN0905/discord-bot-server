# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button, Select, ChannelSelect
from contextlib import suppress
import json
import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import gspread
from google.oauth2.service_account import Credentials
from gtts import gTTS
import asyncio

# 채널 선택 View
class ChannelSelectView(View):
    """알람을 받을 채널 선택 View"""
    
    def __init__(self, cog, repeat_type="once"):
        super().__init__(timeout=300)
        self.cog = cog
        self.repeat_type = repeat_type
        self.selected_channel = None
        
        # 채널 선택 드롭다운
        channel_select = ChannelSelect(
            placeholder="알람을 받을 채널을 선택하세요",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.text]
        )
        channel_select.callback = self.channel_callback
        self.add_item(channel_select)
    
    async def channel_callback(self, interaction: discord.Interaction):
        """채널 선택 시 모달 표시"""
        self.selected_channel = interaction.data['values'][0]
        modal = AlarmTypeModal(self.cog, self.repeat_type, int(self.selected_channel))
        await interaction.response.send_modal(modal)

# 알람 타입 선택 모달
class AlarmTypeModal(Modal, title="알람 추가"):
    """알람 추가 모달 - 통합"""
    
    name = TextInput(
        label="알람 이름",
        placeholder="예: 회의, 복약시간, 운동",
        required=True,
        min_length=1,
        max_length=50
    )
    
    time = TextInput(
        label="시간",
        placeholder="HH:MM (예: 14:30)",
        required=True,
        min_length=5,
        max_length=5
    )
    
    voice = TextInput(
        label="음성 안내 사용 (y/n)",
        placeholder="y - 사용, n - 미사용 (기본값: n)",
        required=False,
        min_length=1,
        max_length=1,
        default="n"
    )
    
    def __init__(self, cog, repeat_type="once", channel_id=None):
        super().__init__()
        self.cog = cog
        self.repeat_type = repeat_type
        self.channel_id = channel_id
    
    async def on_submit(self, interaction: discord.Interaction):
        """모달 제출 처리"""
        try:
            # 시간 형식 검증
            hour, minute = map(int, self.time.value.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("시간 형식이 잘못되었습니다 (00:00-23:59)")
            
            # 음성 옵션 처리
            voice_enabled = self.voice.value.lower() in {'y', 'yes', '네', '예'}
            
            alarms = self.cog.get_alarms()
            alarms[self.name.value] = {
                "time": self.time.value,
                "repeat": self.repeat_type,
                "created": datetime.now().isoformat(),
                "channel_id": self.channel_id,  # 채널 ID 저장
                "voice": voice_enabled  # 음성 안내 설정
            }
            self.cog.save_alarms(alarms)
            
            # 구글 시트에도 저장
            self.cog.save_to_google_sheet(self.name.value, self.time.value, self.repeat_type, self.channel_id, voice_enabled)
            
            # 스케줄러에 등록
            job_id = f"alarm_{self.name.value}"
            
            # 기존 job이 있으면 제거
            if self.cog.scheduler.get_job(job_id):
                self.cog.scheduler.remove_job(job_id)
            
            if self.repeat_type == "daily":
                # 매일 반복
                self.cog.scheduler.add_job(
                    self.cog.trigger_alarm,
                    'cron',
                    hour=hour,
                    minute=minute,
                    id=job_id,
                    args=[self.channel_id, self.name.value, False, voice_enabled],
                    replace_existing=True
                )
            else:
                # 1회성 (다음 발생 시간에만 트리거)
                self.cog.scheduler.add_job(
                    self.cog.trigger_alarm,
                    'cron',
                    hour=hour,
                    minute=minute,
                    id=job_id,
                    args=[self.channel_id, self.name.value, True, voice_enabled],
                    replace_existing=True
                )
            
            repeat_text = "매일" if self.repeat_type == "daily" else "1회"
            channel_text = f"<#{self.channel_id}>" if self.channel_id else "기본 채널"
            voice_text = "[OK] 사용" if voice_enabled else "[ERROR] 미사용"
            embed = discord.Embed(
                title="[OK] 알람 추가됨",
                description=f"**{self.name.value}**\n[TIME] {self.time.value} ({repeat_text})\n[CHANNEL] {channel_text}\n[SPEAKER] 음성: {voice_text}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError as e:
            embed = discord.Embed(
                title="[ERROR] 오류",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# 알람 타입 선택 뷰
class AlarmTypeView(View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    @discord.ui.button(label="[REPEAT] 매일 반복", style=discord.ButtonStyle.primary)
    async def daily_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="[CHANNEL] 채널 선택",
            description="알람을 받을 채널을 선택해주세요.",
            color=discord.Color.blue()
        )
        view = ChannelSelectView(self.cog, "daily")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="[TIME] 1회만", style=discord.ButtonStyle.secondary)
    async def once_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="[CHANNEL] 채널 선택",
            description="알람을 받을 채널을 선택해주세요.",
            color=discord.Color.blue()
        )
        view = ChannelSelectView(self.cog, "once")
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# 알람 UI 버튼 뷰
class AlarmView(View):
    """알람 관리 UI 버튼"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)  # 5분 타임아웃
        self.cog = cog
    
    @discord.ui.button(label="➕ 알람 추가", style=discord.ButtonStyle.success)
    async def add_alarm_button(self, interaction: discord.Interaction, button: Button):
        """알람 추가 버튼 - 타입 선택"""
        embed = discord.Embed(
            title="[TIME] 알람 타입 선택",
            description="원하는 알람 타입을 선택하세요.",
            color=discord.Color.blue()
        )
        view = AlarmTypeView(self.cog)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="[LIST] 목록 보기", style=discord.ButtonStyle.primary)
    async def list_button(self, interaction: discord.Interaction, button: Button):
        """목록 보기 버튼"""
        alarms = self.cog.get_alarms()
        if not alarms:
            await interaction.response.send_message("등록된 알람이 없습니다.", ephemeral=True)
            return
        
        embed = discord.Embed(title="[ALARM] 알람 목록", color=discord.Color.blue())
        
        daily_count = 0
        once_count = 0
        
        for name, data in alarms.items():
            repeat_text = "매일" if data["repeat"] == "daily" else "1회"
            if data["repeat"] == "daily":
                daily_count += 1
            else:
                once_count += 1
            
            emoji = "[REPEAT]" if data["repeat"] == "daily" else "[TIME]"
            channel_id = data.get("channel_id")
            channel_text = f"<#{channel_id}>" if channel_id else "기본 채널"
            voice_enabled = data.get("voice", False)
            voice_text = "[SPEAKER]" if voice_enabled else ""
            
            embed.add_field(
                name=f"{emoji} {name} {voice_text}",
                value=f"[TIME] {data['time']} ({repeat_text})\n[CHANNEL] {channel_text}",
                inline=False
            )
        
        embed.set_footer(text=f"매일: {daily_count}개 | 1회: {once_count}개")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="[REPEAT] 새로고침", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction: discord.Interaction, button: Button):
        """새로고침 버튼"""
        try:
            # 모든 알람 job 제거
            self.cog.scheduler.remove_all_jobs()
            
            # 다시 등록
            alarms = self.cog.get_alarms()
            total_count = 0
            for name, data in alarms.items():
                hour, minute = map(int, data['time'].split(':'))
                job_id = f"alarm_{name}"
                is_once = data['repeat'] != 'daily'
                channel_id = data.get('channel_id')
                voice_enabled = data.get('voice', False)
                
                self.cog.scheduler.add_job(
                    self.cog.trigger_alarm,
                    'cron',
                    hour=hour,
                    minute=minute,
                    id=job_id,
                    args=[channel_id, name, is_once, voice_enabled],
                    replace_existing=True
                )
                total_count += 1
            
            embed = discord.Embed(
                title="[OK] 알람 새로고침됨",
                description=f"총 {total_count}개의 알람이 활성화되었습니다.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"[ERROR] 오류: {e}", ephemeral=True)
    
    @discord.ui.button(label="[ERROR] 삭제", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: Button):
        """삭제 안내"""
        await interaction.response.send_message(
            "삭제할 알람 이름을 입력하세요:\n`!알람 삭제 <이름>`",
            ephemeral=True
        )
    
    @discord.ui.button(label="[DELETE] 초기화", style=discord.ButtonStyle.danger, row=1)
    async def reset_button(self, interaction: discord.Interaction, button: Button):
        """모든 알람 초기화 (관리자 전용)"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("[ERROR] 관리자만 초기화할 수 있습니다.", ephemeral=True)
            return
        
        # 확인 메시지
        embed = discord.Embed(
            title="[WARNING] 경고",
            description="정말로 모든 알람을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
        # 실제 초기화는 명령어로 처리: !알람 초기화

class Alarm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alarm_file = "data/alarms.json"
        self.scheduler = AsyncIOScheduler()
        self.google_sheet = None
        self.ensure_file()
        self.init_google_sheet()
        
        if not self.scheduler.running:
            self.scheduler.start()
        
        # 봇 시작 시 기존 알람 로드
        self.load_existing_alarms()

    def ensure_file(self):
        """파일 생성 및 초기화"""
        if not os.path.exists(self.alarm_file):
            self.save_alarms({})
    
    def init_google_sheet(self):
        """구글 시트 초기화"""
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # 시트 열기 또는 생성
            try:
                self.google_sheet = client.open('Discord_Alarms').sheet1
            except gspread.SpreadsheetNotFound:
                spreadsheet = client.create('Discord_Alarms')
                self.google_sheet = spreadsheet.sheet1
                # 헤더 설정
                self.google_sheet.update('A1:F1', [['이름', '시간', '반복유형', '채널ID', '생성일', '상태']])
                print("[OK] 구글 시트 'Discord_Alarms' 생성됨")
            
            print("[OK] 구글 시트 연결 성공")
        except FileNotFoundError:
            print("[WARNING] credentials.json 파일이 없습니다. 구글 시트 연동이 비활성화됩니다.")
            self.google_sheet = None
        except Exception as e:
            print(f"[WARNING] 구글 시트 초기화 실패: {e}")
            self.google_sheet = None
    
    def load_existing_alarms(self):
        """저장된 알람을 스케줄러에 등록"""
        alarms = self.get_alarms()
        for name, data in alarms.items():
            hour, minute = map(int, data['time'].split(':'))
            job_id = f"alarm_{name}"
            is_once = data['repeat'] != 'daily'
            channel_id = data.get('channel_id')
            voice_enabled = data.get('voice', False)
            
            # 기존 job이 있으면 제거
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            self.scheduler.add_job(
                self.trigger_alarm,
                'cron',
                hour=hour,
                minute=minute,
                id=job_id,
                args=[channel_id, name, is_once, voice_enabled],
                replace_existing=True
            )

    def save_alarms(self, alarms):
        """알람 데이터 저장"""
        os.makedirs(os.path.dirname(self.alarm_file), exist_ok=True)
        with open(self.alarm_file, 'w', encoding='utf-8') as f:
            json.dump(alarms, f, ensure_ascii=False, indent=2)
    
    def save_to_google_sheet(self, name, time, repeat, channel_id, voice_enabled=False):
        """구글 시트에 알람 저장"""
        if not self.google_sheet:
            return
        
        try:
            row = [
                name,
                time,
                "매일" if repeat == "daily" else "1회",
                str(channel_id) or "기본",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "활성",
                "[SPEAKER]" if voice_enabled else ""
            ]
            self.google_sheet.append_row(row)
            print(f"[OK] 구글 시트에 알람 '{name}' 추가됨")
        except Exception as e:
            print(f"[WARNING] 구글 시트 저장 실패: {e}")
    
    def delete_from_google_sheet(self, name):
        """구글 시트에서 알람 삭제"""
        if not self.google_sheet:
            return
        
        try:
            if (cell := self.google_sheet.find(name)):
                self.google_sheet.delete_rows(cell.row)
                print(f"[OK] 구글 시트에서 알람 '{name}' 삭제됨")
        except Exception as e:
            print(f"[WARNING] 구글 시트 삭제 실패: {e}")

    def get_alarms(self):
        """저장된 알람 반환"""
        try:
            with open(self.alarm_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    @commands.command(name="알람ui", help="알람 UI 표시")
    async def alarm_ui(self, ctx_or_interaction):
        """알람 관리 UI 버튼 표시"""
        embed = discord.Embed(
            title="[ALARM] 알람 관리",
            description="아래 버튼을 클릭하여 알람을 관리하세요.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="기능",
            value="➕ **추가** - 새로운 알람 추가\n"
                  "[LIST] **목록** - 현재 알람 목록 보기\n"
                  "[REPEAT] **새로고침** - 알람 스케줄 업데이트\n"
                  "[ERROR] **삭제** - 알람 삭제하기",
            inline=False
        )
        
        view = AlarmView(self)
        
        # Context 또는 Interaction에 따라 다르게 응답
        if isinstance(ctx_or_interaction, discord.Interaction):
            await ctx_or_interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx_or_interaction.send(embed=embed, view=view)

    @commands.group(name="알람", help="알람 관리 명령어")
    async def alarm(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="[ALARM] 알람 도움말", color=discord.Color.blue())
            embed.add_field(name="UI 관리", value="`!알람ui` - 버튼식 UI 사용", inline=False)
            embed.add_field(name="추가", value="`!알람 추가 <이름> <시간(HH:MM)> [반복(daily/once)] [음성(y/n)]`", inline=False)
            embed.add_field(name="삭제", value="`!알람 삭제 <이름>`", inline=False)
            embed.add_field(name="목록", value="`!알람 목록`", inline=False)
            embed.add_field(name="새로고침", value="`!알람 새로고침`", inline=False)
            embed.add_field(name="초기화", value="`!알람 초기화` - 모든 알람 삭제 (관리자)", inline=False)
            embed.add_field(name="음성 안내", value="UI 또는 명령어에서 음성 옵션을 'y'로 설정하면 알람 발동 시 음성 채널에서 음성으로 안내됩니다.", inline=False)
            await ctx.send(embed=embed)

    @alarm.command(name="추가", help="새 알람 추가")
    async def add_alarm(self, ctx, name: str, time: str, repeat: str = "once", voice: str = "n"):
        """알람 추가"""
        try:
            hour, minute = map(int, time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("시간 형식이 잘못되었습니다 (00:00-23:59)")
            
            repeat = "daily" if repeat.lower() in {"daily", "매일"} else "once"
            voice_enabled = voice.lower() in {"y", "yes", "네", "예"}
            
            alarms = self.get_alarms()
            alarms[name] = {
                "time": time,
                "repeat": repeat,
                "created": datetime.now().isoformat(),
                "voice": voice_enabled
            }
            self.save_alarms(alarms)
            
            # 스케줄러에 등록
            job_id = f"alarm_{name}"
            
            # 기존 job이 있으면 제거
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            is_once = repeat != 'daily'
            self.scheduler.add_job(
                self.trigger_alarm,
                'cron',
                hour=hour,
                minute=minute,
                id=job_id,
                args=[None, name, is_once, voice_enabled],
                replace_existing=True
            )
            
            repeat_text = "매일" if repeat == 'daily' else "1회"
            voice_text = "[SPEAKER] 음성 안내 포함" if voice_enabled else ""
            embed = discord.Embed(
                title="[OK] 알람 추가됨",
                description=f"**이름:** {name}\n**시간:** {time}\n**반복:** {repeat_text}\n{voice_text}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"[ERROR] 오류: {e}")

    @alarm.command(name="삭제", help="알람 삭제")
    async def delete_alarm(self, ctx, name: str):
        """알람 삭제"""
        alarms = self.get_alarms()
        if name in alarms:
            # 스케줄러에서도 제거
            job_id = f"alarm_{name}"
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            del alarms[name]
            self.save_alarms(alarms)
            
            # 구글 시트에서도 삭제
            self.delete_from_google_sheet(name)
            
            await ctx.send(f"[OK] **{name}** 알람이 삭제되었습니다.")
        else:
            await ctx.send(f"[ERROR] **{name}** 알람을 찾을 수 없습니다.")

    @alarm.command(name="목록", help="모든 알람 표시")
    async def list_alarms(self, ctx):
        """저장된 알람 목록 표시"""
        alarms = self.get_alarms()
        if not alarms:
            await ctx.send("등록된 알람이 없습니다.")
            return
        
        embed = discord.Embed(title="[ALARM] 알람 목록", color=discord.Color.blue())
        for name, data in alarms.items():
            repeat_text = "매일" if data["repeat"] == "daily" else "1회"
            voice_enabled = data.get("voice", False)
            voice_text = "[SPEAKER]" if voice_enabled else ""
            embed.add_field(
                name=f"{name} {voice_text}",
                value=f"[TIME] {data['time']} ({repeat_text})",
                inline=False
            )
        await ctx.send(embed=embed)

    @alarm.command(name="새로고침", help="알람 스케줄 새로고침")
    async def refresh_alarms(self, ctx):
        """알람 스케줄 업데이트"""
        self.scheduler.remove_all_jobs()
        
        alarms = self.get_alarms()
        active_count = 0
        for name, data in alarms.items():
            hour, minute = map(int, data['time'].split(':'))
            job_id = f"alarm_{name}"
            is_once = data['repeat'] != 'daily'
            channel_id = data.get('channel_id')
            voice_enabled = data.get('voice', False)
            
            self.scheduler.add_job(
                self.trigger_alarm,
                'cron',
                hour=hour,
                minute=minute,
                id=job_id,
                args=[channel_id, name, is_once, voice_enabled],
                replace_existing=True
            )
            active_count += 1
        
        embed = discord.Embed(
            title="[OK] 알람 새로고침됨",
            description=f"총 {active_count}개의 알람이 활성화되었습니다.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @alarm.command(name="초기화", help="모든 알람 초기화 (관리자 전용)")
    @commands.has_permissions(administrator=True)
    async def reset_alarms(self, ctx):
        """모든 알람 초기화"""
        # 모든 스케줄러 작업 제거
        self.scheduler.remove_all_jobs()
        
        # JSON 파일 초기화
        self.save_alarms({})
        
        # 구글 시트 초기화
        if self.google_sheet:
            try:
                # 헤더 제외 모든 행 삭제
                if self.google_sheet.row_count > 1:
                    self.google_sheet.delete_rows(2, self.google_sheet.row_count)
                print("[OK] 구글 시트 초기화됨")
            except Exception as e:
                print(f"[WARNING] 구글 시트 초기화 실패: {e}")
        
        embed = discord.Embed(
            title="[DELETE] 알람 초기화 완료",
            description="모든 알람이 삭제되었습니다.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    async def trigger_alarm(self, channel_id, name, is_once=False, voice_enabled=False):
        """알람 발동"""
        channel = None
        
        # channel_id가 정수면 해당 채널 가져오기
        if isinstance(channel_id, int):
            channel = self.bot.get_channel(channel_id)
        
        # channel이 None이면 설정된 채널이나 첫 번째 텍스트 채널 사용
        if channel is None:
            settings = self.load_alarm_settings()
            fallback_channel_id = settings.get("alarm_channel_id", 0)
            
            if fallback_channel_id > 0:
                channel = self.bot.get_channel(fallback_channel_id)
        
        # 여전히 None이면 첫 번째 길드의 첫 번째 텍스트 채널 사용
        if channel is None:
            for guild in self.bot.guilds:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                if channel:
                    break
        
        # 텍스트 채널에 알람 메시지 전송
        if channel:
            with suppress(Exception):
                await channel.send(f"[ALARM] 알람: {name}\n시간이 되었습니다!")
        
        # 음성 안내 활성화 시
        if voice_enabled and channel:
            guild = channel.guild
            print(f"[SPEAKER] 음성 알람 준비 중: {name} (길드: {guild.name})")
            try:
                await self.play_voice_alarm(guild, name)
            except Exception as e:
                print(f"[ERROR] 음성 알람 재생 실패: {e}")
                import traceback
                traceback.print_exc()
        
        # 1회성 알람이면 자동 삭제
        if is_once:
            alarms = self.get_alarms()
            if name in alarms:
                del alarms[name]
                self.save_alarms(alarms)
                
                # 스케줄러에서 제거
                job_id = f"alarm_{name}"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)
    
    def load_alarm_settings(self):
        """알람 설정 로드"""
        settings_file = "data/settings.json"
        with suppress(Exception):
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return {}
    
    def generate_voice_file(self, alarm_name):
        """TTS로 음성 파일 생성"""
        try:
            # 음성 파일 저장 디렉토리 생성
            os.makedirs("data/voice_alarms", exist_ok=True)
            
            # 음성 파일 경로 (특수문자 제거)
            safe_name = "".join(c for c in alarm_name if c.isalnum() or c in ('_', '-'))
            voice_file = f"data/voice_alarms/{safe_name}.mp3"
            
            print(f"[MUSIC] 음성 파일 생성 중: {voice_file}")
            
            # gTTS로 음성 파일 생성 (한국어)
            text = f"{alarm_name} 알람입니다"
            tts = gTTS(text=text, lang='ko', slow=False)
            tts.save(voice_file)
            
            print(f"[OK] 음성 파일 생성 완료: {voice_file}")
            return voice_file
        except Exception as e:
            print(f"[ERROR] 음성 파일 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def play_voice_alarm(self, guild, alarm_name):
        """음성 채널에서 알람 음성 재생"""
        try:
            print(f"[SPEAKER] 음성 알람 시작: {alarm_name}")
            
            # 봇이 연결된 음성 채널 찾기
            voice_client = None
            for vc in self.bot.voice_clients:
                if vc.guild == guild:
                    voice_client = vc
                    print(f"[OK] 기존 음성 채널 발견: {vc.channel}")
                    break
            
            # 음성 채널이 없으면 첫 번째 사람이 있는 음성 채널 찾기
            if voice_client is None:
                target_channel = None
                for channel in guild.voice_channels:
                    if len(channel.members) > 0:
                        target_channel = channel
                        print(f"[VOICE_CALL] 대상 음성 채널 발견: {channel.name} (멤버: {len(channel.members)}명)")
                        break
                
                if target_channel:
                    try:
                        voice_client = await target_channel.connect()
                        print(f"[OK] 음성 채널 연결됨: {target_channel.name}")
                    except Exception as e:
                        print(f"[ERROR] 음성 채널 연결 실패: {e}")
                        return
                else:
                    print(f"[WARNING] 음성 채널에 사람이 없음")
                    return
            
            # 음성 파일 생성
            voice_file = self.generate_voice_file(alarm_name)
            print(f"[MUSIC] 음성 파일: {voice_file}")
            
            if not voice_file:
                print(f"[ERROR] 음성 파일 생성 실패")
                return
            
            if not os.path.exists(voice_file):
                print(f"[ERROR] 음성 파일이 존재하지 않음: {voice_file}")
                return
            
            if voice_client and not voice_client.is_playing():
                try:
                    print(f"[SPEAKER] 음성 재생 시작...")
                    # ffmpeg 경로 지정
                    ffmpeg_path = "F:/A/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe"
                    if not os.path.exists(ffmpeg_path):
                        ffmpeg_path = "ffmpeg"  # 시스템 PATH에서 찾기
                    
                    # ffmpeg를 사용하여 음성 재생
                    audio_source = discord.FFmpegPCMAudio(voice_file, executable=ffmpeg_path)
                    voice_client.play(
                        audio_source,
                        after=lambda e: self._voice_callback(alarm_name, e)
                    )
                    
                    # 재생 완료 대기
                    max_wait = 30  # 최대 30초 대기
                    waited = 0
                    while voice_client.is_playing() and waited < max_wait:
                        await asyncio.sleep(0.5)
                        waited += 0.5
                    
                    print(f"[OK] 음성 재생 완료: {alarm_name}")
                    
                    # 재생 후 자동으로 연결 해제
                    await asyncio.sleep(1)
                    if voice_client and voice_client.is_connected():
                        await voice_client.disconnect()
                        print(f"[OK] 음성 채널 연결 해제됨")
                
                except Exception as e:
                    print(f"[ERROR] 음성 재생 실패: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"[WARNING] 음성 클라이언트 없음 또는 이미 재생 중")
        
        except Exception as e:
            print(f"[ERROR] 음성 채널 접근 실패: {e}")
            import traceback
            traceback.print_exc()
    
    def _voice_callback(self, alarm_name, error):
        """음성 재생 콜백"""
        if error is None:
            print(f"[OK] 음성 알람 '{alarm_name}' 재생 완료")
        else:
            print(f"[ERROR] 음성 재생 오류 '{alarm_name}': {error}")

async def setup(bot):
    await bot.add_cog(Alarm(bot))
