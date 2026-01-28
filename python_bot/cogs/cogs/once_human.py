# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import gspread
from google.oauth2.service_account import Credentials
from contextlib import suppress

class MemeLevelSelect(Select):
    """메메틱 레벨 선택 드롭다운"""
    
    def __init__(self, cog):
        self.cog = cog
        options = [
            discord.SelectOption(label="Lv 1", value="1", emoji="1️⃣"),
            discord.SelectOption(label="Lv 2", value="2", emoji="2️⃣"),
            discord.SelectOption(label="Lv 3", value="3", emoji="3️⃣"),
            discord.SelectOption(label="Lv 4", value="4", emoji="4️⃣"),
            discord.SelectOption(label="Lv 5", value="5", emoji="5️⃣"),
        ]
        super().__init__(
            placeholder="메메틱 레벨을 선택하세요",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """레벨 선택 시 해당 레벨의 메메틱 정보 표시"""
        level = self.values[0]
        await interaction.response.defer()
        
        meme_data = self.cog.get_meme_by_level(level)
        
        if not meme_data:
            await interaction.followup.send(f"❌ Lv {level} 메메틱 정보를 찾을 수 없습니다.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🎮 원스휴먼 메메틱 정보 - Lv {level}",
            description=f"레벨 {level}에서 사용 가능한 메메틱 목록",
            color=discord.Color.blue()
        )
        
        # 설치기사별로 그룹화
        grouped_data = {}
        for item in meme_data:
            engineer = item.get('설치기사종류', '기타')
            if engineer not in grouped_data:
                grouped_data[engineer] = []
            grouped_data[engineer].append(item)
        
        # 설치기사별로 임베드에 추가
        for engineer, items in grouped_data.items():
            meme_list = []
            for item in items:
                meme_name = item.get('메메틱이름', '알 수 없음')
                description = item.get('설명', '정보 없음')
                meme_list.append(f"**{meme_name}**: {description}")
            
            value_text = "\n".join(meme_list) if meme_list else "정보 없음"
            embed.add_field(
                name=f"🔧 {engineer}",
                value=value_text,
                inline=False
            )
        
        embed.set_footer(text=f"총 {len(meme_data)}개의 메메틱")
        await interaction.followup.send(embed=embed, ephemeral=True)

class MemeTypeSelect(Select):
    """메메틱 타입(설치기사) 선택 드롭다운"""
    
    def __init__(self, cog):
        self.cog = cog
        engineers = cog.get_all_engineers()
        
        options = [
            discord.SelectOption(label=eng, value=eng, emoji="🔧")
            for eng in engineers[:25]  # Discord 최대 25개 제한
        ]
        
        super().__init__(
            placeholder="설치기사를 선택하세요",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        """설치기사 선택 시 해당 설치기사의 모든 메메틱 표시"""
        engineer = self.values[0]
        await interaction.response.defer()
        
        meme_data = self.cog.get_meme_by_engineer(engineer)
        
        if not meme_data:
            await interaction.followup.send(f"❌ {engineer} 정보를 찾을 수 없습니다.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🔧 {engineer}",
            description=f"{engineer}의 모든 메메틱 정보",
            color=discord.Color.blue()
        )
        
        # 레벨별로 그룹화
        level_groups = {}
        for item in meme_data:
            level = item.get('레벨', '0')
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(item)
        
        # 레벨별로 정렬하여 표시
        for level in sorted(level_groups.keys(), key=lambda x: int(x.split('/')[0]) if x else 0):
            items = level_groups[level]
            meme_names = []
            
            for item in items:
                meme_name = item.get('메메틱이름', '알 수 없음')
                item_level = item.get('레벨', '0')
                meme_names.append(f"• [{item_level}] {meme_name}")
            
            # 필드 값 생성 (메메틱 이름 + 레벨)
            value_text = "\n".join(meme_names)
            
            embed.add_field(
                name=f"📊 Lv {level}",
                value=value_text or "정보 없음",
                inline=False
            )
        
        embed.set_footer(text=f"총 {len(meme_data)}개의 메메틱")
        await interaction.followup.send(embed=embed)

class OnceHumanView(View):
    """원스휴먼 메메틱 정보 메인 UI"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
        
        # 설치기사별 검색 드롭다운만 표시
        if cog.get_all_engineers():
            self.add_item(MemeTypeSelect(cog))
    
    @discord.ui.button(label="📋 전체 목록", style=discord.ButtonStyle.primary, row=2)
    async def show_all(self, interaction: discord.Interaction, button: Button):
        """전체 메메틱 목록 요약"""
        await interaction.response.defer(ephemeral=True)
        
        all_data = self.cog.get_all_memes()
        
        if not all_data:
            await interaction.followup.send("❌ 메메틱 정보가 없습니다.", ephemeral=True)
            return
        
        # 레벨별 통계
        level_stats = {}
        engineer_stats = {}
        
        for item in all_data:
            level = item.get('레벨', '0')
            engineer = item.get('설치기사종류', '기타')
            
            level_stats[level] = level_stats.get(level, 0) + 1
            engineer_stats[engineer] = engineer_stats.get(engineer, 0) + 1
        
        embed = discord.Embed(
            title="🎮 원스휴먼 메메틱 전체 통계",
            description="모든 메메틱 정보의 요약",
            color=discord.Color.gold()
        )
        
        # 설치기사별 통계만 표시
        engineer_text = "\n".join([
            f"**{eng}**: {count}개"
            for eng, count in sorted(engineer_stats.items(), key=lambda x: x[1], reverse=True)
        ])
        embed.add_field(name="🔧 설치기사별 통계", value=engineer_text or "정보 없음", inline=False)
        
        embed.set_footer(text=f"총 {len(all_data)}개의 메메틱 등록됨")
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🔄 새로고침", style=discord.ButtonStyle.secondary, row=2)
    async def refresh(self, interaction: discord.Interaction, button: Button):
        """구글 시트 데이터 새로고침"""
        await interaction.response.defer(ephemeral=True)
        
        success = self.cog.reload_data()
        
        if success:
            await interaction.followup.send("✅ 메메틱 데이터가 새로고침되었습니다!", ephemeral=True)
        else:
            await interaction.followup.send("❌ 데이터 새로고침에 실패했습니다.", ephemeral=True)

class OnceHuman(commands.Cog):
    """원스휴먼 메메틱 정보 관리"""
    
    def __init__(self, bot):
        self.bot = bot
        self.google_sheet = None
        self.meme_cache = []  # 메메틱 데이터 캐시
        self.init_google_sheet()
        self.reload_data()
    
    def init_google_sheet(self):
        """구글 시트 초기화"""
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            client = gspread.authorize(creds)
            
            # Once_Data 시트 열기
            spreadsheet = client.open('Once_Data')
            self.google_sheet = spreadsheet.sheet1
            
            print("✅ 원스휴먼 구글 시트 연결 성공")
        except FileNotFoundError:
            print("⚠️ credentials.json 파일이 없습니다.")
            self.google_sheet = None
        except gspread.SpreadsheetNotFound:
            print("⚠️ 'Once_Data' 시트를 찾을 수 없습니다.")
            self.google_sheet = None
        except Exception as e:
            print(f"⚠️ 구글 시트 초기화 실패: {e}")
            self.google_sheet = None
    
    def reload_data(self):
        """구글 시트에서 데이터 다시 로드"""
        if not self.google_sheet:
            return False
        
        try:
            # 모든 데이터 가져오기
            all_values = self.google_sheet.get_all_records()
            self.meme_cache = all_values
            print(f"✅ {len(self.meme_cache)}개의 메메틱 데이터 로드됨")
            
            # 디버그: 첫 번째 데이터 출력
            if self.meme_cache:
                print(f"📋 첫 번째 데이터: {self.meme_cache[0]}")
                print(f"📋 로드된 설치기사: {self.get_all_engineers()}")
            return True
        except Exception as e:
            print(f"❌ 데이터 로드 실패: {e}")
            return False
    
    def get_all_memes(self):
        """모든 메메틱 데이터 반환"""
        return self.meme_cache
    
    def get_meme_by_level(self, level):
        """특정 레벨의 메메틱 데이터 반환"""
        return [
            item for item in self.meme_cache
            if str(item.get('레벨', '')) == str(level)
        ]
    
    def get_meme_by_engineer(self, engineer):
        """특정 설치기사의 메메틱 데이터 반환"""
        return [
            item for item in self.meme_cache
            if item.get('설치기사종류', '') == engineer
        ]
    
    def get_all_engineers(self):
        """모든 설치기사 목록 반환"""
        engineers = set()
        for item in self.meme_cache:
            if eng := item.get('설치기사종류'):
                engineers.add(eng)
        return sorted(engineers)
    
    @commands.command(name="메메틱", aliases=["원스휴먼", "oncehuman"])
    async def meme_info(self, ctx_or_interaction):
        """원스휘만 메메틱 정보 UI 표시"""
        # ctx와 interaction 둘 다 처리
        if isinstance(ctx_or_interaction, discord.Interaction):
            interaction = ctx_or_interaction
            send_func = interaction.response.send_message
            defer_func = interaction.response.defer
        else:
            ctx = ctx_or_interaction
            interaction = None
            send_func = ctx.send
            defer_func = None
        
        embed = discord.Embed(
            title="🎮 원스휴먼 메메틱 정보",
            description="설치기사를 선택해주세요!",
            color=discord.Color.purple()
        )
        
        if not self.meme_cache:
            embed.add_field(
                name="⚠️ 알림",
                value="메메틱 데이터가 로드되지 않았습니다.\n`credentials.json` 파일과 `Once_Data` 시트를 확인해주세요.",
                inline=False
            )
            if interaction:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed)
            return
        
        embed.set_footer(text=f"총 {len(self.meme_cache)}개의 메메틱 정보")
        
        view = OnceHumanView(self)
        if interaction:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(OnceHuman(bot))
