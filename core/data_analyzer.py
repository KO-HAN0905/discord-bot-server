"""
📊 데이터 분석 및 통계 엔진
- 실시간 데이터 분석
- 트렌드 감지
- 시각화 데이터 생성
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import os
from core.cache_manager import memory_cache

class DataAnalyzer:
    """데이터 분석 엔진"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_damage_builds(self, builds_data: List[Dict]) -> Dict[str, Any]:
        """빌드 데이터 분석"""
        if not builds_data:
            return {'error': '데이터 없음'}
        
        # DPS 통계
        dps_values = [b.get('dps', 0) for b in builds_data]
        
        analysis = {
            'total_builds': len(builds_data),
            'dps_statistics': {
                'average': round(statistics.mean(dps_values), 2) if dps_values else 0,
                'median': round(statistics.median(dps_values), 2) if dps_values else 0,
                'stdev': round(statistics.stdev(dps_values), 2) if len(dps_values) > 1 else 0,
                'min': min(dps_values),
                'max': max(dps_values),
                'range': max(dps_values) - min(dps_values)
            },
            'top_builds': sorted(
                builds_data, 
                key=lambda x: x.get('dps', 0), 
                reverse=True
            )[:5],
            'weapon_popularity': self._calculate_weapon_popularity(builds_data),
            'build_types': self._categorize_builds(builds_data)
        }
        
        return analysis
    
    def _calculate_weapon_popularity(self, builds_data: List[Dict]) -> Dict[str, int]:
        """무기 사용 빈도"""
        weapons = [
            b.get('weapon', '불명')
            for b in builds_data
        ]
        return dict(Counter(weapons).most_common(10))
    
    def _categorize_builds(self, builds_data: List[Dict]) -> Dict[str, List[str]]:
        """빌드 유형 분류"""
        categories = defaultdict(list)
        for build in builds_data:
            category = build.get('category', '기타')
            categories[category].append(build.get('name', '불명'))
        return dict(categories)
    
    def detect_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """트렌드 감지"""
        if len(historical_data) < 2:
            return {'error': '데이터 부족'}
        
        trends = {
            'detected_at': datetime.now().isoformat(),
            'rising': [],  # 증가 추세
            'falling': [],  # 감소 추세
            'stable': []   # 안정적
        }
        
        # 시간대별 데이터 추출
        time_series = defaultdict(list)
        for data in historical_data:
            timestamp = data.get('timestamp', '')
            value = data.get('value', 0)
            time_series[timestamp].append(value)
        
        # 추세 계산
        sorted_times = sorted(time_series.keys())
        for i in range(len(sorted_times) - 1):
            current = statistics.mean(time_series[sorted_times[i]])
            next_val = statistics.mean(time_series[sorted_times[i + 1]])
            
            if next_val > current * 1.1:
                trends['rising'].append({
                    'from': sorted_times[i],
                    'to': sorted_times[i + 1],
                    'growth': f"{((next_val / current - 1) * 100):.1f}%"
                })
            elif next_val < current * 0.9:
                trends['falling'].append({
                    'from': sorted_times[i],
                    'to': sorted_times[i + 1],
                    'decline': f"{((1 - next_val / current) * 100):.1f}%"
                })
            else:
                trends['stable'].append({
                    'period': f"{sorted_times[i]} ~ {sorted_times[i + 1]}"
                })
        
        return trends
    
    def generate_heatmap_data(self, discord_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Discord 활동 히트맵 데이터 생성"""
        heatmap = defaultdict(lambda: defaultdict(int))
        
        for msg in discord_data:
            try:
                timestamp = datetime.fromisoformat(msg['timestamp'])
                hour = timestamp.hour
                day = timestamp.weekday()  # 0=월요일
                
                heatmap[day][hour] += 1
            except (ValueError, KeyError):
                continue
        
        # 시각화 형식으로 변환
        result = []
        days = ['월', '화', '수', '목', '금', '토', '일']
        
        for day_idx in range(7):
            for hour in range(24):
                result.append({
                    'day': days[day_idx],
                    'hour': f"{hour:02d}:00",
                    'count': heatmap[day_idx][hour],
                    'day_idx': day_idx,
                    'hour_idx': hour
                })
        
        return {'heatmap': result}
    
    def calculate_engagement_metrics(self, discord_data: List[Dict]) -> Dict[str, Any]:
        """참여도 지표 계산"""
        if not discord_data:
            return {'error': '데이터 없음'}
        
        # 사용자별 메시지 수
        user_messages = Counter(msg.get('author', '불명') for msg in discord_data)
        
        # 채널별 활동
        channel_activity = Counter(msg.get('channel', '불명') for msg in discord_data)
        
        # 시간대별 활동
        hour_activity = defaultdict(int)
        for msg in discord_data:
            try:
                timestamp = datetime.fromisoformat(msg['timestamp'])
                hour_activity[timestamp.hour] += 1
            except (ValueError, KeyError):
                continue
        
        # 평균 메시지 길이
        message_lengths = [
            len(msg.get('content', ''))
            for msg in discord_data
        ]
        avg_length = statistics.mean(message_lengths) if message_lengths else 0
        
        return {
            'total_messages': len(discord_data),
            'unique_users': len(user_messages),
            'messages_per_user': round(len(discord_data) / len(user_messages), 2) if user_messages else 0,
            'most_active_users': dict(user_messages.most_common(10)),
            'most_active_channels': dict(channel_activity.most_common(10)),
            'peak_hours': sorted(
                [(hour, count) for hour, count in hour_activity.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            'average_message_length': round(avg_length, 2),
            'engagement_score': self._calculate_engagement_score(user_messages, message_lengths)
        }
    
    def _calculate_engagement_score(self, user_messages: Counter, message_lengths: List[int]) -> float:
        """참여도 점수 계산 (0-100)"""
        # 활성 사용자 비중 (최대 40점)
        if user_messages:
            active_users_ratio = min(len(user_messages), 100) / 100 * 40
        else:
            active_users_ratio = 0
        
        # 메시지 길이 (최대 30점)
        avg_length = statistics.mean(message_lengths) if message_lengths else 0
        length_score = min(avg_length / 100, 1) * 30
        
        # 메시지 분포 (최대 30점)
        # 고르게 분포되어 있으면 높은 점수
        if user_messages:
            variance = statistics.variance(user_messages.values()) if len(user_messages) > 1 else 0
            distribution_score = max(0, 30 - (variance / 100))
        else:
            distribution_score = 0
        
        total_score = active_users_ratio + length_score + distribution_score
        return round(min(total_score, 100), 2)
    
    def compare_builds(self, build1: Dict, build2: Dict) -> Dict[str, Any]:
        """두 빌드 비교 분석"""
        comparison = {
            'build1': build1.get('name', '빌드1'),
            'build2': build2.get('name', '빌드2'),
            'metrics': {}
        }
        
        # 주요 지표 비교
        metrics = ['dps', 'damage', 'fire_rate', 'crit_chance', 'penetration']
        
        for metric in metrics:
            val1 = build1.get(metric, 0)
            val2 = build2.get(metric, 0)
            
            if val2 > 0:
                difference = ((val1 / val2 - 1) * 100)
            else:
                difference = 0
            
            comparison['metrics'][metric] = {
                'build1': val1,
                'build2': val2,
                'difference_percent': round(difference, 1),
                'winner': '빌드1' if val1 > val2 else '빌드2' if val2 > val1 else '동등'
            }
        
        # 전체 우수성 계산
        wins = sum(1 for m in comparison['metrics'].values() if m['winner'] == '빌드1')
        losses = sum(1 for m in comparison['metrics'].values() if m['winner'] == '빌드2')
        
        comparison['overall'] = {
            'build1_wins': wins,
            'build2_wins': losses,
            'verdict': '빌드1' if wins > losses else '빌드2' if losses > wins else '동등'
        }
        
        return comparison


class AnalysisReporter:
    """분석 보고서 생성기"""
    
    def __init__(self):
        self.analyzer = DataAnalyzer()
    
    def generate_daily_report(self, day_data: Dict[str, Any]) -> str:
        """일일 분석 보고서"""
        report = f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    📊 일일 분석 보고서                              ║
║                    {datetime.now().strftime('%Y-%m-%d')}                            ║
╚═══════════════════════════════════════════════════════════════════╝

📈 주요 통계
─────────────────────────────────────────────────────────────────────
"""
        
        if 'engagement' in day_data:
            eng = day_data['engagement']
            report += f"""
총 메시지: {eng.get('total_messages', 0)}
활성 사용자: {eng.get('unique_users', 0)}
참여도 점수: {eng.get('engagement_score', 0)}/100

가장 활동적인 시간:
"""
            for hour, count in eng.get('peak_hours', [])[:3]:
                report += f"  - {hour:02d}:00 ({count}개)\n"
        
        if 'trends' in day_data:
            trends = day_data['trends']
            report += f"""
📈 감지된 트렌드
─────────────────────────────────────────────────────────────────────
상승: {len(trends.get('rising', []))}개
감소: {len(trends.get('falling', []))}개
안정: {len(trends.get('stable', []))}개
"""
        
        report += "\n" + "═" * 65 + "\n"
        return report
    
    def generate_summary_statistics(self, analysis_data: Dict[str, Any]) -> str:
        """요약 통계"""
        summary = f"""
═════════════════════════════════════════════════════════════════════
                        📋 요약 통계
═════════════════════════════════════════════════════════════════════

분석 시점: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # 빌드 분석 추가
        if 'builds' in analysis_data:
            builds = analysis_data['builds']
            summary += f"""
🎮 빌드 통계
─────────────────────────────────────────────────────────────────────
총 빌드 수: {builds.get('total_builds', 0)}
평균 DPS: {builds.get('dps_statistics', {}).get('average', 0)}
최고 DPS: {builds.get('dps_statistics', {}).get('max', 0)}
최저 DPS: {builds.get('dps_statistics', {}).get('min', 0)}

인기 무기 Top 5:
"""
            for weapon, count in list(builds.get('weapon_popularity', {}).items())[:5]:
                summary += f"  {weapon}: {count}회\n"
        
        summary += "\n═════════════════════════════════════════════════════════════════════\n"
        return summary
