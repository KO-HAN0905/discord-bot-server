"""
Discord 봇용 대미지 계산기 Cog
!대미지 명령어 제공
"""

import discord
from discord.ext import commands
from damage_calculator import DamageCalculator, BuildDamageAnalyzer, format_damage_result
import json

class DamageCalculatorCog(commands.Cog):
    """대미지 계산 기능"""
    
    def __init__(self, bot):
        self.bot = bot
        self.calculator = DamageCalculator()
        self.analyzer = BuildDamageAnalyzer(self.calculator)
    
    @commands.command(name='대미지', aliases=['damage', '피해', 'dps'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def calculate_damage(self, ctx, build_name: str = None, enemy_level: int = 25):
        """
        빌드의 대미지를 계산합니다.
        
        사용법:
        !대미지                           - 모든 빌드 비교
        !대미지 "극대율 풀극"             - 특정 빌드 분석 (기본 레벨 25)
        !대미지 "M82A1 루퍼스 크리" 40   - 특정 빌드 특정 레벨 분석
        
        지원되는 빌드:
        - M82A1 루퍼스 크리
        - 데저트이글 백상아리 크리
        - 신화검 탱커
        - 마법사 원소
        - 극대율 풀극
        """
        
        # 레벨 범위 체크
        if enemy_level < 1 or enemy_level > 100:
            await ctx.send("❌ 적 레벨은 1~100 사이여야 합니다.")
            return
        
        if build_name is None:
            # 모든 빌드 비교
            await self._show_all_builds(ctx, enemy_level)
        else:
            # 특정 빌드 분석
            await self._show_single_build(ctx, build_name, enemy_level)
    
    async def _show_all_builds(self, ctx, enemy_level: int):
        """모든 빌드 비교"""
        all_builds = self.analyzer.get_all_builds()
        results = self.analyzer.compare_builds(all_builds, enemy_level=enemy_level)
        
        # 임베드 생성
        embed = discord.Embed(
            title=f"🎮 빌드별 대미지 비교 (적 레벨 {enemy_level})",
            description="모든 빌드의 대미지를 비교합니다",
            color=discord.Color.gold()
        )
        
        # DPS 순위
        dps_text = ""
        for i, result in enumerate(results, 1):
            build_name = result.get('build_name', '')
            dps = result.get('dps', 0)
            final_dmg = result.get('final_damage', 0)
            dps_text += f"**{i}. {build_name}**\n"
            dps_text += f"   DPS: {dps:,.0f} | 피해: {final_dmg:,.0f}\n"
        
        embed.add_field(name="📊 DPS 순위", value=dps_text, inline=False)
        
        # 빌드별 극대율
        crit_text = ""
        for result in sorted(results, key=lambda x: x.get('crit_rate', ''), reverse=True)[:3]:
            build_name = result.get('build_name', '')
            crit_rate = result.get('crit_rate', '0%')
            crit_text += f"**{build_name}**: {crit_rate}\n"
        
        embed.add_field(name="⚡ 극대율 TOP 3", value=crit_text, inline=True)
        
        # 최고 단일 피해
        highest_single = max(results, key=lambda x: x.get('final_damage', 0))
        embed.add_field(
            name="💥 최고 단일 피해",
            value=f"{highest_single.get('build_name')}: {highest_single.get('final_damage', 0):,.0f}",
            inline=True
        )
        
        embed.set_footer(text=f"적의 방어력: {enemy_level * 2 + 10}")
        
        await ctx.send(embed=embed)
        
        # 상세 정보는 파일로
        details = "🎮 상세 대미지 계산 결과\n" + "=" * 50 + "\n\n"
        for result in results:
            details += format_damage_result(result) + "\n\n"
        
        # 파일 전송 (너무 길 경우)
        if len(details) > 2000:
            with open('damage_details.txt', 'w', encoding='utf-8') as f:
                f.write(details)
            await ctx.send("📄 상세 결과:", file=discord.File('damage_details.txt'))
    
    async def _show_single_build(self, ctx, build_name: str, enemy_level: int):
        """특정 빌드 분석"""
        result = self.analyzer.analyze_build(build_name, enemy_level=enemy_level)
        
        if 'error' in result:
            # 빌드 목록 제시
            available_builds = self.analyzer.get_all_builds()
            builds_list = "\n".join([f"• {b}" for b in available_builds])
            
            embed = discord.Embed(
                title="❌ 빌드를 찾을 수 없습니다",
                description=f"**사용 가능한 빌드:**\n{builds_list}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # 상세 임베드
        build_name = result.get('build_name', '')
        weapon = result.get('weapon', '')
        description = result.get('build_description', '')
        
        embed = discord.Embed(
            title=f"🎯 {build_name}",
            description=f"**무기:** {weapon}\n{description}",
            color=discord.Color.blue()
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
            value=f"기본: {result.get('base_damage', 0):,.0f}\n"
                  f"일반: {result.get('normal_damage', 0):,.0f}\n"
                  f"극대: {result.get('crit_damage', 0):,.0f}\n"
                  f"평균: {result.get('average_damage', 0):,.0f}",
            inline=True
        )
        
        # 극대율 정보
        embed.add_field(
            name="⚡ 극대율",
            value=f"확률: {result.get('crit_rate')}\n"
                  f"배율: {result.get('crit_damage_multiplier')}",
            inline=True
        )
        
        # 최종 결과
        embed.add_field(
            name="🔥 최종 결과",
            value=f"**최종 피해: {result.get('final_damage', 0):,.0f}**\n"
                  f"**DPS: {result.get('dps', 0):,.0f}**",
            inline=False
        )
        
        embed.set_footer(text="대미지 계산 v1.0")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='빌드비교')
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def compare_builds(self, ctx, *build_names):
        """
        여러 빌드를 비교합니다.
        
        사용법:
        !빌드비교 "극대율 풀극" "데저트이글 백상아리 크리"
        """
        
        if not build_names or len(build_names) < 2:
            await ctx.send("❌ 최소 2개 이상의 빌드를 지정해주세요.\n"
                          "예: `!빌드비교 \"극대율 풀극\" \"데저트이글 백상아리 크리\"`")
            return
        
        # 빌드 확인
        all_builds = self.analyzer.get_all_builds()
        valid_builds = []
        invalid_builds = []
        
        for build in build_names:
            if build in all_builds:
                valid_builds.append(build)
            else:
                invalid_builds.append(build)
        
        if invalid_builds:
            embed = discord.Embed(
                title="⚠️ 일부 빌드를 찾을 수 없습니다",
                description=f"찾을 수 없는 빌드: {', '.join(invalid_builds)}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        
        if not valid_builds:
            return
        
        # 비교
        results = self.analyzer.compare_builds(valid_builds, enemy_level=25)
        
        embed = discord.Embed(
            title="⚔️ 빌드 비교",
            color=discord.Color.purple()
        )
        
        # 비교 테이블
        comparison = ""
        comparison += "```\n"
        comparison += f"{'빌드명':<25} {'DPS':>10} {'최종피해':>10}\n"
        comparison += "-" * 50 + "\n"
        
        for result in results:
            build_name = result.get('build_name', '')[:23]
            dps = result.get('dps', 0)
            final_dmg = result.get('final_damage', 0)
            comparison += f"{build_name:<25} {dps:>10,.0f} {final_dmg:>10,.0f}\n"
        
        comparison += "```"
        embed.add_field(name="📊 비교 결과", value=comparison, inline=False)
        
        # 최고 DPS
        top_build = results[0]
        embed.add_field(
            name="🏆 최고 DPS",
            value=f"{top_build.get('build_name')}: {top_build.get('dps', 0):,.0f}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='빌드목록')
    async def list_builds(self, ctx):
        """사용 가능한 빌드 목록"""
        builds = self.analyzer.get_all_builds()
        
        embed = discord.Embed(
            title="📚 사용 가능한 빌드",
            description="다음 빌드들을 계산할 수 있습니다:",
            color=discord.Color.green()
        )
        
        builds_text = "\n".join([f"• {build}" for build in builds])
        embed.add_field(name="빌드 목록", value=builds_text, inline=False)
        
        embed.add_field(
            name="사용법",
            value="`!대미지 \"빌드명\"`\n"
                  "`!빌드비교 \"빌드1\" \"빌드2\"`",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Cog 로드"""
    await bot.add_cog(DamageCalculatorCog(bot))
