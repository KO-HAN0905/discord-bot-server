"""
Discord 임베드 UI 기반 대미지 계산기
초보자도 쉽게 사용할 수 있는 상호작용식 인터페이스
"""

import discord
from discord.ext import commands
from discord.ui import View, Select, Button, Modal, TextInput
import json
from damage_calculator import DamageCalculator
from typing import Dict, Optional

class DamageCalculatorModal(Modal):
    """스탯 입력 모달"""
    
    attack = TextInput(label="공격력", placeholder="100", default="100")
    crit_rate = TextInput(label="극대율 (%)", placeholder="30", default="30")
    crit_damage = TextInput(label="극대 피해 배율 (%)", placeholder="100", default="100")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

class BuildSelect(Select):
    """빌드 선택 드롭다운"""
    
    def __init__(self, callback_func):
        self.callback_func = callback_func
        
        options = [
            discord.SelectOption(label="M82A1 루퍼스 크리", value="M82A1 루퍼스 크리", emoji="🏹"),
            discord.SelectOption(label="데저트이글 백상아리 크리", value="데저트이글 백상아리 크리", emoji="🔫"),
            discord.SelectOption(label="신화검 탱커", value="신화검 탱커", emoji="⚔️"),
            discord.SelectOption(label="마법사 원소", value="마법사 원소", emoji="🔮"),
            discord.SelectOption(label="극대율 풀극", value="극대율 풀극", emoji="💀"),
        ]
        
        super().__init__(
            placeholder="빌드를 선택하세요...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_build = self.values[0]
        await self.callback_func(interaction, selected_build)

class WeaponSelect(Select):
    """무기 선택 드롭다운"""
    
    def __init__(self, callback_func):
        self.callback_func = callback_func
        
        options = [
            discord.SelectOption(label="M82A1 저격총", value="M82A1", emoji="🏹", description="원거리, 높은 피해"),
            discord.SelectOption(label="데저트이글", value="데저트이글", emoji="🔫", description="빠른 공격"),
            discord.SelectOption(label="신화검", value="신화검", emoji="⚔️", description="근거리, 균형잡힌"),
            discord.SelectOption(label="마법 반지", value="마법반지", emoji="🔮", description="마법 공격"),
            discord.SelectOption(label="기사의 검", value="기사의검", emoji="🛡️", description="방어 중심"),
        ]
        
        super().__init__(
            placeholder="무기를 선택하세요...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_weapon = self.values[0]
        await self.callback_func(interaction, selected_weapon)

class LevelSelect(Select):
    """적 레벨 선택"""
    
    def __init__(self, callback_func):
        self.callback_func = callback_func
        
        options = [
            discord.SelectOption(label="일반 몬스터 (레벨 15)", value="15"),
            discord.SelectOption(label="강한 몬스터 (레벨 20)", value="20"),
            discord.SelectOption(label="일반 보스 (레벨 25)", value="25"),
            discord.SelectOption(label="강한 보스 (레벨 30)", value="30"),
            discord.SelectOption(label="매우 강한 보스 (레벨 40)", value="40"),
        ]
        
        super().__init__(
            placeholder="적 레벨을 선택하세요...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_level = int(self.values[0])
        await self.callback_func(interaction, selected_level)

class CalculatorView(View):
    """계산기 메인 뷰"""
    
    def __init__(self, cog, user_id: int, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.user_id = user_id
        self.calculator = DamageCalculator()
        self.analyzer = BuildDamageAnalyzer(self.calculator)
        
        # 저장된 계산값
        self.calculation1: Optional[Dict] = None
        self.calculation2: Optional[Dict] = None
        
        # 입력 값
        self.selected_build = None
        self.enemy_level = 25
        
        self.add_item(BuildSelect(self.on_build_select))
    
    async def on_build_select(self, interaction: discord.Interaction, build_name: str):
        """빌드 선택 콜백"""
        self.selected_build = build_name
        
        embed = discord.Embed(
            title="⚙️ 적 레벨 선택",
            description=f"**선택된 빌드:** {build_name}\n\n적의 레벨을 선택하세요.",
            color=discord.Color.blue()
        )
        
        level_view = View()
        level_view.add_item(LevelSelect(self.on_level_select))
        
        await interaction.response.edit_message(embed=embed, view=level_view)
    
    async def on_level_select(self, interaction: discord.Interaction, level: int):
        """레벨 선택 콜백"""
        self.enemy_level = level
        
        # 계산 수행
        result = self.analyzer.analyze_build(self.selected_build, enemy_level=level)
        
        # 첫 번째 계산값으로 저장
        self.calculation1 = result
        
        embed = self.create_result_embed(result, slot=1)
        
        await interaction.response.edit_message(embed=embed, view=self.create_next_view())
    
    def create_result_embed(self, result: Dict, slot: int = 1) -> discord.Embed:
        """결과 임베드 생성"""
        build_name = result.get('build_name', '')
        weapon = result.get('weapon', '')
        description = result.get('build_description', '')
        
        embed = discord.Embed(
            title=f"{'🟢' if slot == 1 else '🔵'} 계산 결과 {slot}번",
            description=f"**빌드:** {build_name}\n**무기:** {weapon}",
            color=discord.Color.green() if slot == 1 else discord.Color.blue()
        )
        
        # 기본 정보
        embed.add_field(
            name="📋 기본 정보",
            value=f"적 레벨: {result.get('enemy_level')}\n"
                  f"적 방어력: {result.get('enemy_defense')}\n"
                  f"공격속도: {result.get('attack_speed')}회/초",
            inline=False
        )
        
        # 대미지 정보
        embed.add_field(
            name="💥 대미지",
            value=f"**일반:** {result.get('normal_damage', 0):,.0f}\n"
                  f"**극대:** {result.get('crit_damage', 0):,.0f}\n"
                  f"**평균:** {result.get('average_damage', 0):,.0f}",
            inline=True
        )
        
        # 극대율 정보
        embed.add_field(
            name="⚡ 극대율",
            value=f"**확률:** {result.get('crit_rate')}\n"
                  f"**배율:** {result.get('crit_damage_multiplier')}",
            inline=True
        )
        
        # 최종 결과
        embed.add_field(
            name="🔥 최종 결과",
            value=f"**최종 피해:** {result.get('final_damage', 0):,.0f}\n"
                  f"**DPS:** {result.get('dps', 0):,.0f}",
            inline=False
        )
        
        embed.set_footer(text=f"계산 슬롯 {slot}")
        
        return embed
    
    def create_next_view(self) -> View:
        """다음 단계 뷰 생성"""
        view = View()
        
        # 또 다른 계산 버튼
        another_btn = Button(label="➕ 또 다른 계산", style=discord.ButtonStyle.green, emoji="🧮")
        another_btn.callback = self.on_another_calculation
        view.add_item(another_btn)
        
        # 비교 버튼 (두 번째 계산이 있을 때만)
        if self.calculation1 is not None:
            compare_btn = Button(label="⚔️ 비교", style=discord.ButtonStyle.blurple, emoji="📊")
            compare_btn.callback = self.on_compare
            view.add_item(compare_btn)
        
        # 처음부터 시작
        restart_btn = Button(label="🔄 처음부터", style=discord.ButtonStyle.gray, emoji="↩️")
        restart_btn.callback = self.on_restart
        view.add_item(restart_btn)
        
        return view
    
    async def on_another_calculation(self, interaction: discord.Interaction):
        """또 다른 계산"""
        # 이전 계산을 계산2로 이동
        if self.calculation1 is not None and self.calculation2 is None:
            self.calculation2 = self.calculation1
        
        self.calculation1 = None
        self.selected_build = None
        
        embed = discord.Embed(
            title="🧮 또 다른 대미지 계산",
            description="**새로운 빌드를 선택하세요.**",
            color=discord.Color.blue()
        )
        
        main_view = CalculatorView(self.cog, self.user_id)
        await interaction.response.edit_message(embed=embed, view=main_view)
    
    async def on_compare(self, interaction: discord.Interaction):
        """계산값 비교"""
        if self.calculation1 is None or self.calculation2 is None:
            await interaction.response.send_message("❌ 비교할 계산값이 부족합니다.", ephemeral=True)
            return
        
        # 비교 임베드 생성
        embed = discord.Embed(
            title="⚔️ 대미지 계산값 비교",
            color=discord.Color.gold()
        )
        
        calc1 = self.calculation1
        calc2 = self.calculation2
        
        build1 = calc1.get('build_name', '')
        build2 = calc2.get('build_name', '')
        dps1 = calc1.get('dps', 0)
        dps2 = calc2.get('dps', 0)
        dmg1 = calc1.get('final_damage', 0)
        dmg2 = calc2.get('final_damage', 0)
        
        # 승자 결정
        dps_winner = "🟢 계산1" if dps1 > dps2 else ("🔵 계산2" if dps2 > dps1 else "동점")
        dmg_winner = "🟢 계산1" if dmg1 > dmg2 else ("🔵 계산2" if dmg2 > dmg1 else "동점")
        
        # 비교 테이블
        comparison = "```\n"
        comparison += f"{'항목':<20} {'🟢 계산1':<15} {'🔵 계산2':<15} {'차이':<10}\n"
        comparison += "-" * 65 + "\n"
        
        # DPS 비교
        dps_diff = abs(dps1 - dps2)
        dps_percent = (dps_diff / max(dps1, dps2) * 100) if max(dps1, dps2) > 0 else 0
        comparison += f"{'DPS':<20} {dps1:>13,.0f} {dps2:>13,.0f} {f'+{dps_percent:.1f}%' if dps1 > dps2 else f'-{dps_percent:.1f}%':>10}\n"
        
        # 최종 피해 비교
        dmg_diff = abs(dmg1 - dmg2)
        dmg_percent = (dmg_diff / max(dmg1, dmg2) * 100) if max(dmg1, dmg2) > 0 else 0
        comparison += f"{'최종피해':<20} {dmg1:>13,.0f} {dmg2:>13,.0f} {f'+{dmg_percent:.1f}%' if dmg1 > dmg2 else f'-{dmg_percent:.1f}%':>10}\n"
        
        # 극대율 비교
        crit1 = float(calc1.get('crit_rate', '0%').rstrip('%'))
        crit2 = float(calc2.get('crit_rate', '0%').rstrip('%'))
        comparison += f"{'극대율':<20} {crit1:>12.1f}% {crit2:>12.1f}% {f'+{crit1-crit2:.1f}%' if crit1 > crit2 else f'-{crit2-crit1:.1f}%':>10}\n"
        
        comparison += "```"
        
        embed.add_field(name="🟢 계산1", value=f"**{build1}**\nDPS: {dps1:,.0f}", inline=True)
        embed.add_field(name="🔵 계산2", value=f"**{build2}**\nDPS: {dps2:,.0f}", inline=True)
        embed.add_field(name="🏆 승자", value=f"**DPS:** {dps_winner}\n**피해:** {dmg_winner}", inline=False)
        
        embed.add_field(name="📊 상세 비교", value=comparison, inline=False)
        
        # 추천
        if dps1 > dps2:
            recommendation = f"🟢 **계산1 추천!**\n{build1}가 {build2}보다 DPS가 {dps_percent:.1f}% 높습니다."
        elif dps2 > dps1:
            recommendation = f"🔵 **계산2 추천!**\n{build2}가 {build1}보다 DPS가 {dps_percent:.1f}% 높습니다."
        else:
            recommendation = "동점입니다! 다른 요소를 고려하세요."
        
        embed.add_field(name="💡 추천", value=recommendation, inline=False)
        embed.set_footer(text="더 높은 DPS를 선택하시면 됩니다!")
        
        await interaction.response.send_message(embed=embed)
    
    async def on_restart(self, interaction: discord.Interaction):
        """처음부터 시작"""
        self.calculation1 = None
        self.calculation2 = None
        self.selected_build = None
        
        embed = discord.Embed(
            title="🧮 대미지 계산기",
            description="**빌드를 선택하여 대미지를 계산해보세요!**\n\n"
                       "1️⃣ 빌드 선택\n"
                       "2️⃣ 적 레벨 선택\n"
                       "3️⃣ 계산값 확인\n"
                       "4️⃣ 다시 계산하여 비교",
            color=discord.Color.blue()
        )
        
        main_view = CalculatorView(self.cog, self.user_id)
        await interaction.response.edit_message(embed=embed, view=main_view)

class DamageCalculatorUICog(commands.Cog):
    """대미지 계산기 UI Cog"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='계산기', aliases=['대미지UI', 'calculator'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def damage_calculator_ui(self, ctx):
        """
        대미지 계산기를 시작합니다.
        
        사용법:
        !계산기
        
        기능:
        - 빌드 선택
        - 적 레벨 선택
        - 대미지 계산
        - 계산값 비교
        """
        
        embed = discord.Embed(
            title="🧮 대미지 계산기",
            description="**빌드를 선택하여 대미지를 계산해보세요!**\n\n"
                       "📋 **사용 방법:**\n"
                       "1️⃣ 빌드 선택\n"
                       "2️⃣ 적 레벨 선택\n"
                       "3️⃣ 계산값 확인\n"
                       "4️⃣ 다시 계산하여 비교 (선택)\n\n"
                       "💡 **팁:**\n"
                       "• \"또 다른 계산\" 버튼으로 두 개의 빌드를 비교할 수 있습니다.\n"
                       "• \"비교\" 버튼으로 DPS, 피해, 극대율을 한눈에 비교할 수 있습니다.",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/🧮.png")
        embed.set_footer(text="클릭하여 시작하세요 👇")
        
        calculator_view = CalculatorView(self, ctx.author.id)
        
        await ctx.send(embed=embed, view=calculator_view)
    
    @commands.command(name='빠른계산')
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def quick_calculate(self, ctx, build_name: str, enemy_level: int = 25):
        """
        빠르게 계산합니다 (UI 없이).
        
        사용법:
        !빠른계산 "극대율 풀극"
        !빠른계산 "M82A1 루퍼스 크리" 40
        """
        
        calculator = DamageCalculator()
        analyzer = BuildDamageAnalyzer(calculator)
        
        result = analyzer.analyze_build(build_name, enemy_level=enemy_level)
        
        if 'error' in result:
            await ctx.send(f"❌ {result['error']}")
            return
        
        embed = discord.Embed(
            title=f"⚡ {result.get('build_name')}",
            description=f"무기: {result.get('weapon')}",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💥 피해",
            value=f"**최종:** {result.get('final_damage', 0):,.0f}\n"
                  f"**DPS:** {result.get('dps', 0):,.0f}",
            inline=True
        )
        
        embed.add_field(
            name="⚡ 극대율",
            value=f"{result.get('crit_rate')} × {result.get('crit_damage_multiplier')}",
            inline=True
        )
        
        embed.add_field(
            name="📊 상세",
            value=f"적 레벨: {result.get('enemy_level')}\n"
                  f"일반 공격: {result.get('normal_damage', 0):,.0f}\n"
                  f"극대 공격: {result.get('crit_damage', 0):,.0f}",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Cog 로드"""
    await bot.add_cog(DamageCalculatorUICog(bot))
