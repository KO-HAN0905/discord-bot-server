# -*- coding: utf-8 -*-
"""
원스휴먼 확장 기능 모듈
- 월드 보스 정보
- 아이템/장비 정보
- 수동작 가이드
- 자동채집 위치
- 게임 팁/공략
- 커뮤니티 이벤트
"""

import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import gspread
from google.oauth2.service_account import Credentials
from contextlib import suppress
from typing import List, Dict

class OnceHumanExtended(commands.Cog):
    """원스휴먼 확장 기능 (보스, 아이템, 수동작, 자동채집, 팁, 이벤트)"""
    
    def __init__(self, bot):
        self.bot = bot
        self.google_sheet_client = None
        self.spreadsheet = None
        self.sheets = {}  # 시트별 데이터 캐시
        self.init_google_sheet()
        self.load_all_data()
    
    def init_google_sheet(self):
        """구글 시트 초기화"""
        try:
            scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
            self.google_sheet_client = gspread.authorize(creds)
            
            # Once_Data 스프레드시트 열기
            self.spreadsheet = self.google_sheet_client.open('Once_Data')
            print("✅ 원스휴먼 확장 구글 시트 연결 성공")
        except Exception as e:
            print(f"⚠️ 구글 시트 초기화 실패: {e}")
            self.spreadsheet = None
    
    def load_all_data(self):
        """모든 시트 데이터 로드"""
        if not self.spreadsheet:
            print("⚠️ 스프레드시트가 초기화되지 않았습니다.")
            return
        
        sheet_names = ['Boss', 'Items', 'ManualWork', 'GatherLocations', 'GameTips', 'CommunityEvents']
        
        for sheet_name in sheet_names:
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                data = worksheet.get_all_records()
                self.sheets[sheet_name] = data
                print(f"✅ {sheet_name}: {len(data)}개 항목 로드")
            except Exception as e:
                print(f"⚠️ {sheet_name} 로드 실패: {e}")
                self.sheets[sheet_name] = []
    
    # ==================== 월드 보스 정보 ====================
    
    def get_all_bosses(self) -> List[Dict]:
        """모든 보스 데이터 반환"""
        return self.sheets.get('Boss', [])
    
    def get_boss_by_name(self, name: str) -> Dict:
        """보스 이름으로 검색"""
        for boss in self.get_all_bosses():
            if boss.get('보스이름', '').lower() == name.lower():
                return boss
        return {}
    
    def get_bosses_by_difficulty(self, difficulty: str) -> List[Dict]:
        """난이도별 보스 검색"""
        return [
            boss for boss in self.get_all_bosses()
            if boss.get('난이도', '').lower() == difficulty.lower()
        ]
    
    @commands.command(name="보스", aliases=["월드보스", "boss"])
    async def boss_info(self, ctx):
        """월드 보스 정보 조회"""
        bosses = self.get_all_bosses()
        
        if not bosses:
            await ctx.send("❌ 보스 데이터가 없습니다.")
            return
        
        embed = discord.Embed(
            title="🐉 원스휴먼 월드 보스 정보",
            description=f"총 {len(bosses)}개의 보스",
            color=discord.Color.red()
        )
        
        # 난이도별로 그룹화
        by_difficulty = {}
        for boss in bosses:
            difficulty = boss.get('난이도', '미분류')
            if difficulty not in by_difficulty:
                by_difficulty[difficulty] = []
            by_difficulty[difficulty].append(boss)
        
        for difficulty, boss_list in sorted(by_difficulty.items()):
            boss_names = []
            for boss in boss_list:
                name = boss.get('보스이름', '알 수 없음')
                location = boss.get('출현위치', '')
                hp = boss.get('HP', '')
                info = f"• **{name}**"
                if location:
                    info += f" (위치: {location})"
                if hp:
                    info += f" [HP: {hp}]"
                boss_names.append(info)
            
            embed.add_field(
                name=f"⚔️ {difficulty}",
                value="\n".join(boss_names),
                inline=False
            )
        
        embed.set_footer(text="보스별 상세정보는 !보스상세 <보스이름>으로 확인하세요")
        await ctx.send(embed=embed)
    
    @commands.command(name="보스상세")
    async def boss_detail(self, ctx, *, boss_name: str):
        """특정 보스의 상세 정보"""
        boss = self.get_boss_by_name(boss_name)
        
        if not boss:
            await ctx.send(f"❌ '{boss_name}' 보스를 찾을 수 없습니다.")
            return
        
        embed = discord.Embed(
            title=f"🐉 {boss.get('보스이름', '보스')} 상세정보",
            color=discord.Color.red()
        )
        
        fields = ['난이도', '출현위치', 'HP', '공격패턴', '드롭아이템', '추천장비', '팁']
        for field in fields:
            value = boss.get(field, '정보 없음')
            if value and value != '정보 없음':
                embed.add_field(name=field, value=value, inline=False)
        
        await ctx.send(embed=embed)
    
    # ==================== 아이템/장비 정보 ====================
    
    def get_all_items(self) -> List[Dict]:
        """모든 아이템 데이터 반환"""
        return self.sheets.get('Items', [])
    
    def get_item_by_name(self, name: str) -> Dict:
        """아이템 이름으로 검색"""
        for item in self.get_all_items():
            if item.get('아이템명', '').lower() == name.lower():
                return item
        return {}
    
    def get_items_by_grade(self, grade: str) -> List[Dict]:
        """등급별 아이템 검색"""
        return [
            item for item in self.get_all_items()
            if item.get('등급', '').lower() == grade.lower()
        ]
    
    def get_items_by_category(self, category: str) -> List[Dict]:
        """카테고리별 아이템 검색"""
        return [
            item for item in self.get_all_items()
            if item.get('카테고리', '').lower() == category.lower()
        ]
    
    @commands.command(name="아이템", aliases=["item", "장비"])
    async def item_info(self, ctx, *, item_name: str = None):
        """아이템/장비 정보 조회"""
        if item_name:
            item = self.get_item_by_name(item_name)
            if not item:
                await ctx.send(f"❌ '{item_name}' 아이템을 찾을 수 없습니다.")
                return
            
            embed = discord.Embed(
                title=f"⚔️ {item.get('아이템명', '아이템')}",
                color=discord.Color.gold()
            )
            
            fields = ['등급', '카테고리', '능력치', '효과', '입수방법', '판매가격']
            for field in fields:
                value = item.get(field, '정보 없음')
                if value:
                    embed.add_field(name=field, value=value, inline=False)
            
            await ctx.send(embed=embed)
        else:
            # 전체 아이템 목록
            items = self.get_all_items()
            if not items:
                await ctx.send("❌ 아이템 데이터가 없습니다.")
                return
            
            embed = discord.Embed(
                title="⚔️ 아이템/장비 목록",
                description=f"총 {len(items)}개",
                color=discord.Color.gold()
            )
            
            by_category = {}
            for item in items:
                category = item.get('카테고리', '기타')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item)
            
            for category, item_list in sorted(by_category.items()):
                item_names = [item.get('아이템명', '알 수 없음') for item in item_list]
                embed.add_field(
                    name=f"📦 {category}",
                    value=", ".join(item_names),
                    inline=False
                )
            
            embed.set_footer(text="상세정보는 !아이템 <아이템명>으로 확인하세요")
            await ctx.send(embed=embed)
    
    # ==================== 수동작 가이드 ====================
    
    def get_all_manual_works(self) -> List[Dict]:
        """모든 수동작 데이터 반환"""
        return self.sheets.get('ManualWork', [])
    
    def get_manual_work_by_name(self, name: str) -> Dict:
        """수동작 이름으로 검색"""
        for work in self.get_all_manual_works():
            if work.get('작업명', '').lower() == name.lower():
                return work
        return {}
    
    @commands.command(name="수동작", aliases=["작업", "manualwork"])
    async def manual_work_info(self, ctx, *, work_name: str = None):
        """수동작 가이드"""
        if work_name:
            work = self.get_manual_work_by_name(work_name)
            if not work:
                await ctx.send(f"❌ '{work_name}' 작업을 찾을 수 없습니다.")
                return
            
            embed = discord.Embed(
                title=f"🛠️ {work.get('작업명', '작업')}",
                color=discord.Color.blue()
            )
            
            fields = ['난이도', '위치', '시간', '보상', '필요도구', '팁']
            for field in fields:
                value = work.get(field, '정보 없음')
                if value and value != '정보 없음':
                    embed.add_field(name=field, value=value, inline=False)
            
            await ctx.send(embed=embed)
        else:
            works = self.get_all_manual_works()
            if not works:
                await ctx.send("❌ 수동작 데이터가 없습니다.")
                return
            
            embed = discord.Embed(
                title="🛠️ 수동작 목록",
                description=f"총 {len(works)}개",
                color=discord.Color.blue()
            )
            
            by_difficulty = {}
            for work in works:
                difficulty = work.get('난이도', '미분류')
                if difficulty not in by_difficulty:
                    by_difficulty[difficulty] = []
                by_difficulty[difficulty].append(work)
            
            for difficulty, work_list in sorted(by_difficulty.items()):
                work_names = [work.get('작업명', '알 수 없음') for work in work_list]
                embed.add_field(
                    name=f"⭐ {difficulty}",
                    value=", ".join(work_names),
                    inline=False
                )
            
            embed.set_footer(text="상세정보는 !수동작 <작업명>으로 확인하세요")
            await ctx.send(embed=embed)
    
    # ==================== 자동채집 위치 ====================
    
    def get_all_gather_locations(self) -> List[Dict]:
        """모든 자동채집 위치 반환"""
        return self.sheets.get('GatherLocations', [])
    
    def get_gather_by_resource(self, resource: str) -> List[Dict]:
        """자원별 채집지 검색"""
        return [
            loc for loc in self.get_all_gather_locations()
            if loc.get('자원종류', '').lower() == resource.lower()
        ]
    
    @commands.command(name="채집", aliases=["채집지", "gather"])
    async def gather_info(self, ctx, *, resource: str = None):
        """자동채집 위치 정보"""
        locations = self.get_all_gather_locations()
        
        if not locations:
            await ctx.send("❌ 자동채집 위치 데이터가 없습니다.")
            return
        
        if resource:
            locations = self.get_gather_by_resource(resource)
            if not locations:
                await ctx.send(f"❌ '{resource}' 자동채집 위치를 찾을 수 없습니다.")
                return
        
        embed = discord.Embed(
            title="📍 자동채집 위치",
            description=f"총 {len(locations)}개",
            color=discord.Color.green()
        )
        
        by_resource = {}
        for loc in locations:
            res = loc.get('자원종류', '기타')
            if res not in by_resource:
                by_resource[res] = []
            by_resource[res].append(loc)
        
        for res, loc_list in sorted(by_resource.items()):
            location_info = []
            for loc in loc_list:
                name = loc.get('위치명', '알 수 없음')
                count = loc.get('개수', '')
                time = loc.get('리스폰시간', '')
                info = f"• **{name}**"
                if count:
                    info += f" ({count}개)"
                if time:
                    info += f" [리스폰: {time}]"
                location_info.append(info)
            
            embed.add_field(
                name=f"🌿 {res}",
                value="\n".join(location_info),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    # ==================== 게임 팁/공략 ====================
    
    def get_all_tips(self) -> List[Dict]:
        """모든 게임 팁 반환"""
        return self.sheets.get('GameTips', [])
    
    def get_tips_by_category(self, category: str) -> List[Dict]:
        """카테고리별 팁 검색"""
        return [
            tip for tip in self.get_all_tips()
            if tip.get('카테고리', '').lower() == category.lower()
        ]
    
    @commands.command(name="팁", aliases=["공략", "가이드", "tips"])
    async def game_tips(self, ctx, *, category: str = None):
        """게임 팁/공략"""
        tips = self.get_all_tips()
        
        if not tips:
            await ctx.send("❌ 게임 팁 데이터가 없습니다.")
            return
        
        embed = discord.Embed(
            title="💡 게임 팁/공략",
            color=discord.Color.yellow()
        )
        
        if category:
            tips = self.get_tips_by_category(category)
            if not tips:
                await ctx.send(f"❌ '{category}' 카테고리의 팁을 찾을 수 없습니다.")
                return
        
        by_category = {}
        for tip in tips:
            cat = tip.get('카테고리', '기타')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(tip)
        
        for cat, tip_list in sorted(by_category.items()):
            tip_texts = []
            for tip in tip_list:
                title = tip.get('제목', '팁')
                content = tip.get('내용', '')
                tip_texts.append(f"**{title}**: {content}")
            
            embed.add_field(
                name=f"📌 {cat}",
                value="\n".join(tip_texts[:3]),  # 처음 3개만
                inline=False
            )
        
        embed.set_footer(text="모든 팁을 보려면 구글 시트를 확인하세요")
        await ctx.send(embed=embed)
    
    # ==================== 커뮤니티 이벤트 ====================
    
    def get_all_events(self) -> List[Dict]:
        """모든 커뮤니티 이벤트 반환"""
        return self.sheets.get('CommunityEvents', [])
    
    def get_active_events(self) -> List[Dict]:
        """진행 중인 이벤트만"""
        events = self.get_all_events()
        return [e for e in events if e.get('상태', '').lower() == '진행중']
    
    @commands.command(name="이벤트", aliases=["event"])
    async def community_events(self, ctx):
        """커뮤니티 이벤트 정보"""
        events = self.get_all_events()
        
        if not events:
            await ctx.send("❌ 이벤트 데이터가 없습니다.")
            return
        
        active = self.get_active_events()
        
        embed = discord.Embed(
            title="🎉 커뮤니티 이벤트",
            description=f"총 {len(events)}개 (진행 중: {len(active)}개)",
            color=discord.Color.magenta()
        )
        
        # 진행 중인 이벤트부터 표시
        for event in active:
            name = event.get('이벤트명', '이벤트')
            period = event.get('진행기간', '')
            reward = event.get('보상', '')
            info = f"{period}\n🎁 {reward}" if reward else period
            
            embed.add_field(
                name=f"🔥 {name}",
                value=info,
                inline=False
            )
        
        # 예정 이벤트
        upcoming = [e for e in events if e.get('상태', '').lower() != '진행중']
        if upcoming:
            embed.add_field(name="📅 예정된 이벤트", value="정보 확인 바랍니다", inline=False)
        
        await ctx.send(embed=embed)
    
    # ==================== 데이터 관리 ====================
    
    @commands.command(name="원스데이터새로고침")
    @commands.is_owner()
    async def reload_once_data(self, ctx):
        """원스휴먼 데이터 새로고침 (관리자만)"""
        self.load_all_data()
        
        embed = discord.Embed(
            title="✅ 데이터 새로고침 완료",
            color=discord.Color.green()
        )
        
        for sheet_name, data in self.sheets.items():
            embed.add_field(name=sheet_name, value=f"{len(data)}개 항목", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OnceHumanExtended(bot))
