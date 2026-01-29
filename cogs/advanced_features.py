"""
🎯 고급 기능 모음
- 빌드 시뮬레이터
- 대미지 비교 분석
- 전투 전술 제안
- 상세 통계 및 리포트
"""

from discord.ext import commands
import discord
from typing import Dict, List, Optional, Tuple
from damage_calculator import DamageCalculator, BuildPresets
from core.data_analyzer import DataAnalyzer, AnalysisReporter
from core.cache_manager import memory_cache
import json
import asyncio
from datetime import datetime

class AdvancedFeatures(commands.Cog):
    """고급 기능 Cog"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.calculator = DamageCalculator()
        self.analyzer = DataAnalyzer()
        self.reporter = AnalysisReporter()
        self.user_simulations = {}  # 사용자별 시뮬레이션 저장
    
    # ═══════════════════════════════════════════════════════════════
    # 1️⃣ 빌드 비교 및 분석
    # ═══════════════════════════════════════════════════════════════
    
    @commands.command(name='빌드비교')
    async def compare_builds(self, ctx, build1: str = None, build2: str = None):
        """두 빌드 상세 비교"""
        if not build1 or not build2:
            available = list(BuildPresets.presets.keys())
            await ctx.send(
                f"사용법: `!빌드비교 [빌드1] [빌드2]`\n"
                f"available builds: {', '.join(available)}"
            )
            return
        
        try:
            # 빌드 데이터 가져오기
            result1 = BuildPresets.calculate_build(self.calculator, build1, enemy_level=30)
            result2 = BuildPresets.calculate_build(self.calculator, build2, enemy_level=30)
            
            # 분석
            comparison = self.analyzer.compare_builds(result1, result2)
            
            # 임베드 생성
            embed = discord.Embed(
                title="⚔️ 빌드 상세 비교 분석",
                color=discord.Color.red()
            )
            
            # 기본 정보
            embed.add_field(
                name="비교 대상",
                value=f"**{build1}** vs **{build2}**",
                inline=False
            )
            
            # 지표별 비교
            metrics_text = ""
            for metric, data in comparison['metrics'].items():
                winner = "🟢" if data['winner'] == '빌드1' else "🔴" if data['winner'] == '빌드2' else "⚪"
                metrics_text += (
                    f"{metric.upper()}: "
                    f"{data['build1']} vs {data['build2']} "
                    f"({data['difference_percent']:+.1f}%) {winner}\n"
                )
            
            embed.add_field(
                name="📊 지표 비교",
                value=metrics_text,
                inline=False
            )
            
            # 최종 평가
            overall = comparison['overall']
            verdict_text = (
                f"🏆 우수 빌드: **{overall['verdict']}**\n"
                f"   {overall['build1_wins']}승 vs {overall['build2_wins']}승"
            )
            embed.add_field(
                name="최종 평가",
                value=verdict_text,
                inline=False
            )
            
            # 상황별 추천
            embed.add_field(
                name="💡 상황별 추천",
                value=self._get_tactical_advice(build1, build2, result1, result2),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ 비교 실패: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 2️⃣ 빌드 시뮬레이터
    # ═══════════════════════════════════════════════════════════════
    
    @commands.command(name='시뮬레이터')
    async def simulator(self, ctx, 
                       build_name: str = None,
                       enemy_level: int = 30,
                       enemy_armor: int = 60):
        """빌드 시뮬레이터 (상세 분석)"""
        
        if not build_name:
            await ctx.send("사용법: `!시뮬레이터 [빌드명] [적레벨=30] [적방어력=60]`")
            return
        
        try:
            # 캐시 확인
            cache_key = f"simulation_{build_name}_{enemy_level}_{enemy_armor}"
            cached_result = memory_cache.get(cache_key)
            
            if cached_result:
                result = cached_result
                print("💾 캐시에서 로드")
            else:
                result = BuildPresets.calculate_build(
                    self.calculator, 
                    build_name, 
                    enemy_level=enemy_level,
                    enemy_armor=enemy_armor
                )
                # 캐시에 저장 (1시간)
                memory_cache.set(cache_key, result, ttl=3600)
            
            # 상세 보고서 생성
            embed = discord.Embed(
                title=f"🎮 {build_name} 시뮬레이션",
                description=f"적 레벨: Lv.{enemy_level} | 적 방어력: {enemy_armor}",
                color=discord.Color.green()
            )
            
            # 무기 정보
            if 'weapon_info' in result:
                info = result['weapon_info']
                embed.add_field(
                    name="🔫 무기 정보",
                    value=(
                        f"연사력: {info.get('fire_rate', 0)} 발/초\n"
                        f"탄창: {info.get('magazine', 0)}발\n"
                        f"재장전: {info.get('reload_time', 0)}초"
                    ),
                    inline=True
                )
            
            # 특성
            if 'stats' in result:
                stats = result['stats']
                embed.add_field(
                    name="⚙️ 빌드 특성",
                    value=(
                        f"공격력: +{stats.get('attack_power', 0)}%\n"
                        f"크리: {stats.get('crit_chance', 0)}%\n"
                        f"크리데미지: +{stats.get('crit_damage', 0)}%"
                    ),
                    inline=True
                )
            
            # 대미지 분석
            if 'damage' in result:
                dmg = result['damage']
                embed.add_field(
                    name="💥 대미지 분석",
                    value=(
                        f"일반 히트: {dmg.get('normal_hit', 0)}\n"
                        f"크리티컬: {dmg.get('crit_hit', 0)}\n"
                        f"헤드샷: {dmg.get('headshot', 0)}"
                    ),
                    inline=False
                )
            
            # DPS 분석
            if 'dps' in result:
                dps = result['dps']
                embed.add_field(
                    name="📈 DPS 분석",
                    value=(
                        f"순간 DPS: {dps.get('burst_dps', 0)}\n"
                        f"지속 DPS: {dps.get('sustained_dps', 0)}\n"
                        f"헤드샷 DPS: {dps.get('headshot_dps', 0)}"
                    ),
                    inline=False
                )
            
            # 전술 조언
            embed.add_field(
                name="🎯 전술 조언",
                value=self._generate_tactical_advice(build_name, result),
                inline=False
            )
            
            # 개선 제안
            embed.add_field(
                name="🔧 개선 제안",
                value=self._generate_improvement_tips(result),
                inline=False
            )
            
            embed.set_footer(text=f"시뮬레이션 시간: {datetime.now().strftime('%H:%M:%S')}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ 시뮬레이션 실패: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 3️⃣ 권장 빌드
    # ═══════════════════════════════════════════════════════════════
    
    @commands.command(name='권장빌드')
    async def recommend_builds(self, ctx, playstyle: str = None):
        """플레이스타일에 맞는 빌드 추천"""
        
        playstyles = {
            '원거리': ['크리티컬 스나이퍼', 'AK 관통 빌드'],
            '근거리': ['샷건 근접 빌드', '신화검 크리티컬'],
            '균형': ['고속 연사 돌격', '권총 DPS 빌드'],
            '고화력': ['크리티컬 스나이퍼'],
            '스피드': ['고속 연사 돌격', '권총 DPS 빌드']
        }
        
        if not playstyle or playstyle not in playstyles:
            styles = ', '.join(playstyles.keys())
            await ctx.send(f"사용법: `!권장빌드 [플레이스타일]`\n지원 스타일: {styles}")
            return
        
        try:
            recommended = playstyles[playstyle]
            embed = discord.Embed(
                title=f"🎯 {playstyle} 플레이스타일 추천 빌드",
                color=discord.Color.blurple()
            )
            
            results = {}
            for build in recommended:
                result = BuildPresets.calculate_build(self.calculator, build, enemy_level=30)
                results[build] = result
                
                dps = result.get('dps', {})
                embed.add_field(
                    name=f"⭐ {build}",
                    value=(
                        f"순간 DPS: {dps.get('burst_dps', 0)}\n"
                        f"지속 DPS: {dps.get('sustained_dps', 0)}\n"
                        f"특징: {self._get_build_characteristics(build)}"
                    ),
                    inline=False
                )
            
            # 최고 DPS 빌드 강조
            best_build = max(
                results.items(),
                key=lambda x: x[1].get('dps', {}).get('burst_dps', 0)
            )
            embed.add_field(
                name="🏆 이 플레이스타일에서 최고 성능",
                value=f"**{best_build[0]}**",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ 추천 실패: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 4️⃣ 통계 및 분석 리포트
    # ═══════════════════════════════════════════════════════════════
    
    @commands.command(name='빌드통계')
    async def build_statistics(self, ctx):
        """모든 빌드 통계 및 비교"""
        
        try:
            all_builds = {}
            
            # 모든 빌드 계산
            for build_name in BuildPresets.presets.keys():
                result = BuildPresets.calculate_build(self.calculator, build_name, enemy_level=30)
                all_builds[build_name] = result
            
            # 분석
            analysis = self.analyzer.analyze_damage_builds([
                {
                    'name': name,
                    'dps': data.get('dps', {}).get('burst_dps', 0),
                    'sustained_dps': data.get('dps', {}).get('sustained_dps', 0),
                    'weapon': data.get('weapon_info', {}).get('name', '불명')
                }
                for name, data in all_builds.items()
            ])
            
            # 리포트 생성
            embed = discord.Embed(
                title="📊 전체 빌드 통계",
                color=discord.Color.gold()
            )
            
            # DPS 통계
            dps_stats = analysis['dps_statistics']
            embed.add_field(
                name="📈 DPS 통계",
                value=(
                    f"평균: {dps_stats['average']}\n"
                    f"중앙값: {dps_stats['median']}\n"
                    f"최고: {dps_stats['max']}\n"
                    f"최저: {dps_stats['min']}\n"
                    f"범위: {dps_stats['range']}"
                ),
                inline=False
            )
            
            # 상위 5 빌드
            top_5_text = ""
            for i, build in enumerate(analysis['top_builds'][:5], 1):
                dps = build.get('dps', 0)
                top_5_text += f"{i}. **{build['name']}**: {dps} DPS\n"
            
            embed.add_field(
                name="🏆 상위 5 빌드",
                value=top_5_text,
                inline=False
            )
            
            # 빌드 유형
            types_text = ""
            for build_type, builds in analysis['build_types'].items():
                types_text += f"**{build_type}**: {len(builds)}개\n"
            
            if types_text:
                embed.add_field(
                    name="🎮 빌드 유형",
                    value=types_text,
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ 통계 실패: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 헬퍼 메서드
    # ═══════════════════════════════════════════════════════════════
    
    def _get_tactical_advice(self, build1: str, build2: str, result1: Dict, result2: Dict) -> str:
        """상황별 전술 조언"""
        advice = ""
        
        # PvE
        dps1 = result1.get('dps', {}).get('burst_dps', 0)
        dps2 = result2.get('dps', {}).get('burst_dps', 0)
        
        if dps1 > dps2:
            advice += f"🐉 PvE: **{build1}** 추천\n"
        else:
            advice += f"🐉 PvE: **{build2}** 추천\n"
        
        # PvP
        crit1 = result1.get('stats', {}).get('crit_chance', 0)
        crit2 = result2.get('stats', {}).get('crit_chance', 0)
        
        if crit1 > crit2:
            advice += f"⚔️ PvP: **{build1}** 추천 (높은 크리)\n"
        else:
            advice += f"⚔️ PvP: **{build2}** 추천 (높은 크리)\n"
        
        return advice
    
    def _generate_tactical_advice(self, build_name: str, result: Dict) -> str:
        """전술 조언 생성"""
        advice = ""
        
        dps = result.get('dps', {}).get('burst_dps', 0)
        
        if dps > 1000:
            advice += "💥 매우 높은 DPS - 순간 화력이 강합니다\n"
        elif dps > 500:
            advice += "⚡ 우수한 DPS - 균형잡힌 성능\n"
        else:
            advice += "🎯 낮은 DPS - 정확성과 위치 선정이 중요\n"
        
        crit = result.get('stats', {}).get('crit_chance', 0)
        if crit > 60:
            advice += "🎲 높은 크리율 - 크리티컬 운영 중심\n"
        else:
            advice += "📊 낮은 크리율 - 안정적인 딜 운영\n"
        
        return advice
    
    def _generate_improvement_tips(self, result: Dict) -> str:
        """개선 제안 생성"""
        tips = ""
        
        if result.get('dps', {}).get('sustained_dps', 0) < 400:
            tips += "⚡ 재장전 시간 단축 스킬 추천\n"
        
        if result.get('stats', {}).get('crit_chance', 0) < 50:
            tips += "🎲 크리티컬 확률 증가 스킬 추천\n"
        
        if result.get('weapon_info', {}).get('magazine', 0) < 20:
            tips += "📦 탄창 증가 스킬 추천\n"
        
        return tips or "현재 빌드가 잘 최적화되어 있습니다!"
    
    def _get_build_characteristics(self, build_name: str) -> str:
        """빌드 특징"""
        characteristics = {
            '크리티컬 스나이퍼': '높은 DPS, 원거리 전문',
            '신화검 크리티컬': '근거리 매직 딜러',
            '권총 DPS 빌드': '빠른 연사',
            'AK 관통 빌드': '방어력 무시',
            '고속 연사 돌격': '가장 높은 연사력',
            '샷건 근접 빌드': '최고의 근거리 화력'
        }
        return characteristics.get(build_name, '알려지지 않음')

async def setup(bot: commands.Bot):
    await bot.add_cog(AdvancedFeatures(bot))
