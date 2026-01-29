"""
🤖 자동화 및 스케줄러 시스템
- 자동 데이터 수집
- 정기 보고서 생성
- 실시간 모니터링 및 알림
"""

import asyncio
from discord.ext import commands, tasks
import discord
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from core.cache_manager import memory_cache, persistent_cache

class AutomationScheduler(commands.Cog):
    """자동화 및 스케줄링 관리자"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.automation_config = {}
        self.load_automation_config()
        
        # 스케줄 시작
        self.hourly_stats_collector.start()
        self.daily_report_generator.start()
        self.cache_cleanup.start()
        self.performance_monitor.start()
    
    def load_automation_config(self) -> None:
        """자동화 설정 로드"""
        config_file = "data/automation_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                self.automation_config = json.load(f)
        else:
            # 기본 설정
            self.automation_config = {
                'enabled': True,
                'collect_stats_interval': 3600,      # 1시간마다
                'generate_report_interval': 86400,    # 1일마다
                'cleanup_cache_interval': 10800,      # 3시간마다
                'monitor_performance_interval': 1800,  # 30분마다
                'alert_threshold': {
                    'memory_usage_mb': 512,
                    'cache_hit_rate': 0.5,
                    'error_rate': 0.1
                }
            }
            self.save_automation_config()
    
    def save_automation_config(self) -> None:
        """자동화 설정 저장"""
        os.makedirs("data", exist_ok=True)
        with open("data/automation_config.json", 'w', encoding='utf-8') as f:
            json.dump(self.automation_config, f, ensure_ascii=False, indent=2)
    
    @tasks.loop(minutes=60)
    async def hourly_stats_collector(self):
        """시간별 통계 수집"""
        if not self.automation_config.get('enabled'):
            return
        
        try:
            stats = {
                'timestamp': datetime.now().isoformat(),
                'cache_stats': memory_cache.get_stats(),
                'bot_stats': {
                    'latency': round(self.bot.latency * 1000, 2),
                    'servers': len(self.bot.guilds),
                    'users': sum(g.member_count for g in self.bot.guilds)
                }
            }
            
            # 통계 저장
            stats_file = f"data/stats/hourly_{datetime.now().strftime('%Y%m%d_%H00')}.json"
            os.makedirs("data/stats", exist_ok=True)
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 시간별 통계 수집 완료: {datetime.now().strftime('%Y-%m-%d %H:00')}")
        except Exception as e:
            print(f"❌ 통계 수집 오류: {e}")
    
    @tasks.loop(hours=24)
    async def daily_report_generator(self):
        """일일 보고서 생성"""
        if not self.automation_config.get('enabled'):
            return
        
        try:
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'generated_at': datetime.now().isoformat(),
                'cache_performance': memory_cache.get_stats(),
                'bot_status': {
                    'uptime': self._get_bot_uptime(),
                    'total_commands': self._get_total_commands(),
                    'active_users': len(set(
                        member for guild in self.bot.guilds 
                        for member in guild.members if not member.bot
                    ))
                },
                'recommendations': self._generate_recommendations()
            }
            
            # 보고서 저장
            report_file = f"data/reports/daily_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs("data/reports", exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 일일 보고서 생성 완료: {report_file}")
        except Exception as e:
            print(f"❌ 보고서 생성 오류: {e}")
    
    @tasks.loop(hours=3)
    async def cache_cleanup(self):
        """만료된 캐시 정리"""
        try:
            # 메모리 캐시 정리
            expired_keys = [
                key for key, entry in memory_cache.cache.items()
                if datetime.now() > entry['expiry']
            ]
            for key in expired_keys:
                memory_cache.delete(key)
            
            print(f"✅ 캐시 정리 완료: {len(expired_keys)}개 항목 제거")
        except Exception as e:
            print(f"❌ 캐시 정리 오류: {e}")
    
    @tasks.loop(minutes=30)
    async def performance_monitor(self):
        """성능 모니터링 및 경고"""
        try:
            stats = memory_cache.get_stats()
            thresholds = self.automation_config.get('alert_threshold', {})
            
            # 캐시 히트율 확인
            hit_rate = float(stats['hit_rate'].strip('%')) / 100
            if hit_rate < thresholds.get('cache_hit_rate', 0.5):
                print(f"⚠️ 캐시 히트율 낮음: {stats['hit_rate']}")
            
            # 캐시 크기 확인
            size = stats['size_estimate_mb']
            max_size = thresholds.get('memory_usage_mb', 512)
            if size > max_size:
                print(f"⚠️ 메모리 사용량 초과: {size:.1f} MB (제한: {max_size} MB)")
        except Exception as e:
            print(f"❌ 성능 모니터링 오류: {e}")
    
    def _get_bot_uptime(self) -> str:
        """봇 가동 시간"""
        if hasattr(self.bot, 'start_time'):
            delta = datetime.now() - self.bot.start_time
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            return f"{delta.days}일 {hours}시간 {minutes}분"
        return "불명"
    
    def _get_total_commands(self) -> int:
        """총 명령어 실행 횟수"""
        return memory_cache.get('total_commands') or 0
    
    def _generate_recommendations(self) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        stats = memory_cache.get_stats()
        
        if float(stats['hit_rate'].strip('%')) < 60:
            recommendations.append("🔍 캐시 전략 재검토 필요")
        
        if stats['size_estimate_mb'] > 250:
            recommendations.append("📦 캐시 크기 최적화 필요")
        
        if len([g for g in self.bot.guilds if g.member_count < 10]) > 5:
            recommendations.append("👥 활성 서버 관리 검토 권장")
        
        return recommendations
    
    @commands.command(name='자동화상태')
    async def automation_status(self, ctx):
        """자동화 상태 확인"""
        if not await self._check_admin(ctx):
            return
        
        embed = discord.Embed(
            title="🤖 자동화 시스템 상태",
            color=discord.Color.blue()
        )
        
        # 활성화 상태
        enabled = self.automation_config.get('enabled', True)
        embed.add_field(
            name="상태",
            value="✅ 활성화" if enabled else "❌ 비활성화",
            inline=False
        )
        
        # 스케줄 정보
        embed.add_field(
            name="📅 스케줄",
            value=(
                f"시간별 통계: 매 시간\n"
                f"일일 보고서: 매일 자정\n"
                f"캐시 정리: 3시간마다\n"
                f"성능 모니터링: 30분마다"
            ),
            inline=False
        )
        
        # 캐시 통계
        cache_stats = memory_cache.get_stats()
        embed.add_field(
            name="💾 캐시 통계",
            value=(
                f"캐시 히트: {cache_stats['hits']}\n"
                f"캐시 미스: {cache_stats['misses']}\n"
                f"히트율: {cache_stats['hit_rate']}\n"
                f"크기: {cache_stats['size_estimate_mb']:.1f} MB"
            ),
            inline=True
        )
        
        # 봇 통계
        embed.add_field(
            name="🤖 봇 통계",
            value=(
                f"서버: {len(self.bot.guilds)}\n"
                f"지연: {round(self.bot.latency * 1000)}ms\n"
                f"활성 사용자: {sum(g.member_count for g in self.bot.guilds)}"
            ),
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='자동화설정')
    async def automation_settings(self, ctx, setting: str = None, value: str = None):
        """자동화 설정 변경 (관리자 전용)"""
        if not await self._check_admin(ctx):
            return
        
        if not setting:
            # 현재 설정 표시
            embed = discord.Embed(
                title="⚙️ 자동화 설정",
                color=discord.Color.gold()
            )
            for key, val in self.automation_config.items():
                embed.add_field(
                    name=key,
                    value=str(val),
                    inline=False
                )
            await ctx.send(embed=embed)
            return
        
        if not value:
            await ctx.send("❌ 설정 값을 입력해주세요.")
            return
        
        try:
            # 설정 값 업데이트
            if value.lower() in ('true', 'false'):
                self.automation_config[setting] = value.lower() == 'true'
            elif value.isdigit():
                self.automation_config[setting] = int(value)
            else:
                self.automation_config[setting] = value
            
            self.save_automation_config()
            await ctx.send(f"✅ 설정 변경 완료: `{setting} = {value}`")
        except Exception as e:
            await ctx.send(f"❌ 설정 변경 실패: {e}")
    
    async def _check_admin(self, ctx) -> bool:
        """관리자 권한 확인"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ 관리자 권한이 필요합니다.")
            return False
        return True
    
    def cog_unload(self):
        """Cog 언로드 시 작업 취소"""
        self.hourly_stats_collector.cancel()
        self.daily_report_generator.cancel()
        self.cache_cleanup.cancel()
        self.performance_monitor.cancel()

async def setup(bot: commands.Bot):
    await bot.add_cog(AutomationScheduler(bot))
