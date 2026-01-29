"""
원스휴먼 실전 대미지 계산기 (v2.0)
커뮤니티 데이터 기반으로 재구성한 실전 공식
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class WeaponStats:
    """무기 기본 스탯"""
    name: str
    damage: int  # 기본 공격력
    fire_rate: float  # 연사력 (발/초)
    magazine: int  # 탄창
    reload_time: float  # 재장전 시간 (초)
    headshot_mult: float = 2.0  # 헤드샷 배율
    weak_point_mult: float = 1.5  # 약점 배율

class DamageCalculator:
    """원스휴먼 실전 대미지 계산 엔진 v2.0
    
    커뮤니티 경험을 바탕으로 재구성한 계산 공식:
    1. 기본 데미지 = 무기 공격력 × (1 + 공격력% 증가)
    2. 크리티컬 데미지 = 기본 데미지 × (1 + 크리티컬 피해%)
    3. 약점/헤드샷 = 크리티컬 데미지 × 약점 배율
    4. 방어 감소 = 공격 × (1 - 방어력 감소율)
    5. DPS = (총 데미지 / 탄창) × 연사력 × 크리티컬 확률 고려
    """
    
    def __init__(self):
        self.weapons = self._init_weapons()
    
    def _init_weapons(self) -> Dict[str, WeaponStats]:
        """실제 무기 데이터 초기화"""
        return {
            # 돌격소총
            'AK47': WeaponStats('AK47', 38, 10, 30, 2.2),
            'M4A1': WeaponStats('M4A1', 32, 12.5, 30, 1.8),
            'SCAR': WeaponStats('SCAR', 42, 9, 20, 2.5),
            
            # 저격소총
            'M82A1': WeaponStats('M82A1 저격총', 280, 1.2, 5, 3.5, 2.5, 2.0),
            'SVD': WeaponStats('SVD', 95, 3.0, 10, 2.8, 2.2, 1.8),
            
            # 권총
            '데저트이글': WeaponStats('데저트이글', 85, 4, 7, 1.5, 2.0, 1.5),
            'USP': WeaponStats('USP', 48, 6, 12, 1.2),
            
            # 샷건
            'SPAS-12': WeaponStats('SPAS-12', 180, 1.5, 8, 3.0, 1.5, 1.5),
            
            # SMG
            'UZI': WeaponStats('UZI', 22, 15, 32, 1.5),
            'MP5': WeaponStats('MP5', 28, 13, 30, 1.6),
            
            # LMG
            'M249': WeaponStats('M249', 45, 11, 100, 4.5),
            
            # 특수무기
            '신화검': WeaponStats('신화검', 120, 2.0, 1, 0, 1.8, 1.5),
            '마법 반지': WeaponStats('마법 반지', 95, 1.5, 1, 0, 1.2, 1.3),
        }
    
    def calculate_base_damage(self, weapon: WeaponStats, attack_power_percent: float) -> float:
        """기본 데미지 계산
        
        Args:
            weapon: 무기 스탯
            attack_power_percent: 공격력 % 증가 (예: 50.0 = 50%)
        
        Returns:
            기본 데미지
        """
        return weapon.damage * (1 + attack_power_percent / 100)
    
    def calculate_crit_damage(self, base_damage: float, crit_chance: float, crit_damage_percent: float) -> Tuple[float, float]:
        """크리티컬 데미지 계산
        
        Args:
            base_damage: 기본 데미지
            crit_chance: 크리티컬 확률 % (0-100)
            crit_damage_percent: 크리티컬 피해 % (예: 150 = 기본의 2.5배)
        
        Returns:
            (일반 데미지, 크리티컬 데미지)
        """
        normal = base_damage
        critical = base_damage * (1 + crit_damage_percent / 100)
        return normal, critical
    
    def calculate_weak_point_damage(self, damage: float, is_headshot: bool, is_weak_point: bool, 
                                    weapon: WeaponStats) -> float:
        """약점/헤드샷 데미지 계산
        
        Args:
            damage: 기본 데미지
            is_headshot: 헤드샷 여부
            is_weak_point: 약점 타격 여부
            weapon: 무기 스탯
        
        Returns:
            최종 데미지
        """
        multiplier = 1.0
        if is_headshot:
            multiplier *= weapon.headshot_mult
        if is_weak_point:
            multiplier *= weapon.weak_point_mult
        return damage * multiplier
    
    def calculate_defense_reduction(self, damage: float, enemy_defense: int, armor_penetration: int) -> float:
        """방어력 계산
        
        원스휴먼 방어력 공식 (추정):
        최종 데미지 = 데미지 × (100 / (100 + (방어력 - 관통력)))
        
        Args:
            damage: 기본 데미지
            enemy_defense: 적 방어력
            armor_penetration: 방어 관통력
        
        Returns:
            방어 적용 후 데미지
        """
        effective_defense = max(0, enemy_defense - armor_penetration)
        reduction = 100 / (100 + effective_defense)
        return damage * reduction
    
    def calculate_dps(self, weapon: WeaponStats, per_shot_damage: float, 
                     crit_chance: float, crit_damage: float) -> Dict:
        """DPS (초당 피해) 계산
        
        Args:
            weapon: 무기 스탯
            per_shot_damage: 발당 일반 데미지
            crit_chance: 크리티컬 확률 %
            crit_damage: 크리티컬 데미지
        
        Returns:
            DPS 정보 (평균, 최대, 지속 DPS 등)
        """
        # 크리티컬 고려한 평균 데미지
        crit_rate = crit_chance / 100
        avg_damage_per_shot = (per_shot_damage * (1 - crit_rate)) + (crit_damage * crit_rate)
        
        # 순수 DPS (재장전 없이)
        burst_dps = avg_damage_per_shot * weapon.fire_rate
        
        # 지속 DPS (재장전 포함)
        time_to_empty = weapon.magazine / weapon.fire_rate
        total_cycle_time = time_to_empty + weapon.reload_time
        sustained_dps = (avg_damage_per_shot * weapon.magazine) / total_cycle_time
        
        # 탄창당 총 데미지
        magazine_damage = avg_damage_per_shot * weapon.magazine
        
        return {
            'burst_dps': round(burst_dps, 2),
            'sustained_dps': round(sustained_dps, 2),
            'avg_per_shot': round(avg_damage_per_shot, 2),
            'magazine_damage': round(magazine_damage, 2),
            'time_to_empty': round(time_to_empty, 2),
        }
    
    def full_calculation(self, 
                        weapon_name: str,
                        attack_power_percent: float = 0,
                        crit_chance: float = 5.0,
                        crit_damage_percent: float = 50.0,
                        armor_penetration: int = 0,
                        enemy_defense: int = 50,
                        is_headshot: bool = False,
                        is_weak_point: bool = False) -> Dict:
        """전체 데미지 계산
        
        Args:
            weapon_name: 무기 이름
            attack_power_percent: 공격력 % 증가
            crit_chance: 크리티컬 확률 %
            crit_damage_percent: 크리티컬 피해 %
            armor_penetration: 방어 관통력
            enemy_defense: 적 방어력
            is_headshot: 헤드샷 여부
            is_weak_point: 약점 타격 여부
        
        Returns:
            상세 계산 결과
        """
        if weapon_name not in self.weapons:
            return {'error': f'무기 "{weapon_name}"을 찾을 수 없습니다'}
        
        weapon = self.weapons[weapon_name]
        
        # 1단계: 기본 데미지
        base_dmg = self.calculate_base_damage(weapon, attack_power_percent)
        
        # 2단계: 크리티컬
        normal_dmg, crit_dmg = self.calculate_crit_damage(base_dmg, crit_chance, crit_damage_percent)
        
        # 3단계: 약점/헤드샷 (크리티컬에 적용)
        normal_final = self.calculate_weak_point_damage(normal_dmg, is_headshot, is_weak_point, weapon)
        crit_final = self.calculate_weak_point_damage(crit_dmg, is_headshot, is_weak_point, weapon)
        
        # 4단계: 방어력
        normal_after_def = self.calculate_defense_reduction(normal_final, enemy_defense, armor_penetration)
        crit_after_def = self.calculate_defense_reduction(crit_final, enemy_defense, armor_penetration)
        
        # 5단계: DPS
        dps_info = self.calculate_dps(weapon, normal_after_def, crit_chance, crit_after_def)
        
        return {
            'weapon': weapon.name,
            'base_damage': round(base_dmg, 2),
            'normal_hit': round(normal_after_def, 2),
            'crit_hit': round(crit_after_def, 2),
            'headshot_modifier': f"{weapon.headshot_mult}x" if is_headshot else "N/A",
            'weak_point_modifier': f"{weapon.weak_point_mult}x" if is_weak_point else "N/A",
            'crit_chance': f"{crit_chance}%",
            'crit_damage': f"+{crit_damage_percent}%",
            'armor_pen': armor_penetration,
            'enemy_def': enemy_defense,
            'fire_rate': weapon.fire_rate,
            'magazine': weapon.magazine,
            'reload_time': weapon.reload_time,
            **dps_info
        }


class BuildPresets:
    """실전 빌드 프리셋"""
    
    @staticmethod
    def get_all_builds() -> Dict:
        """모든 빌드 프리셋 반환"""
        return {
            '크리티컬 스나이퍼': {
                'weapon': 'M82A1',
                'attack_power': 80.0,  # 공격력 +80%
                'crit_chance': 65.0,  # 크리티컬 확률 65%
                'crit_damage': 180.0,  # 크리티컬 피해 +180%
                'armor_pen': 35,
                'description': '헤드샷 원킬 저격 빌드'
            },
            '고속 연사 돌격': {
                'weapon': 'M4A1',
                'attack_power': 45.0,
                'crit_chance': 40.0,
                'crit_damage': 120.0,
                'armor_pen': 20,
                'description': '안정적인 중거리 빌드'
            },
            '권총 DPS 빌드': {
                'weapon': '데저트이글',
                'attack_power': 60.0,
                'crit_chance': 55.0,
                'crit_damage': 150.0,
                'armor_pen': 25,
                'description': '근거리 고화력 빌드'
            },
            'AK 관통 빌드': {
                'weapon': 'AK47',
                'attack_power': 50.0,
                'crit_chance': 30.0,
                'crit_damage': 100.0,
                'armor_pen': 45,
                'description': '고방어 적 상대 빌드'
            },
            '샷건 근접 빌드': {
                'weapon': 'SPAS-12',
                'attack_power': 70.0,
                'crit_chance': 35.0,
                'crit_damage': 130.0,
                'armor_pen': 15,
                'description': '근접 폭딜 빌드'
            },
            '신화검 크리티컬': {
                'weapon': '신화검',
                'attack_power': 90.0,
                'crit_chance': 75.0,
                'crit_damage': 200.0,
                'armor_pen': 30,
                'description': '극한 크리티컬 빌드'
            }
        }
    
    @staticmethod
    def calculate_build(calculator: DamageCalculator, build_name: str, enemy_level: int = 30) -> Dict:
        """빌드 계산
        
        Args:
            calculator: 계산기 인스턴스
            build_name: 빌드 이름
            enemy_level: 적 레벨 (방어력 계산용)
        
        Returns:
            계산 결과
        """
        builds = BuildPresets.get_all_builds()
        if build_name not in builds:
            return {'error': f'빌드 "{build_name}"을 찾을 수 없습니다'}
        
        build = builds[build_name]
        
        # 레벨별 적 방어력 (레벨 * 2)
        enemy_def = enemy_level * 2
        
        # 일반 타격
        normal_result = calculator.full_calculation(
            weapon_name=build['weapon'],
            attack_power_percent=build['attack_power'],
            crit_chance=build['crit_chance'],
            crit_damage_percent=build['crit_damage'],
            armor_penetration=build['armor_pen'],
            enemy_defense=enemy_def,
            is_headshot=False,
            is_weak_point=False
        )
        
        # 헤드샷 크리티컬
        headshot_result = calculator.full_calculation(
            weapon_name=build['weapon'],
            attack_power_percent=build['attack_power'],
            crit_chance=build['crit_chance'],
            crit_damage_percent=build['crit_damage'],
            armor_penetration=build['armor_pen'],
            enemy_defense=enemy_def,
            is_headshot=True,
            is_weak_point=False
        )
        
        return {
            'build_name': build_name,
            'description': build['description'],
            'enemy_level': enemy_level,
            'normal': normal_result,
            'headshot': headshot_result
        }


def format_result(result: Dict) -> str:
    """결과 포맷팅"""
    if 'error' in result:
        return f"❌ {result['error']}"
    
    normal = result['normal']
    headshot = result['headshot']
    
    output = []
    output.append("=" * 80)
    output.append(f"⚔️  {result['build_name']} - {normal['weapon']}")
    output.append(f"📝 {result['description']}")
    output.append("=" * 80)
    output.append("")
    
    output.append("【 무기 정보 】")
    output.append(f"  연사력: {normal['fire_rate']} 발/초")
    output.append(f"  탄창: {normal['magazine']}발")
    output.append(f"  재장전: {normal['reload_time']}초")
    output.append(f"  크리티컬: {normal['crit_chance']} (피해 {normal['crit_damage']})")
    output.append(f"  방어관통: {normal['armor_pen']} (적 방어: {normal['enemy_def']})")
    output.append("")
    
    output.append("【 일반 타격 (몸통) 】")
    output.append(f"  기본 데미지: {normal['base_damage']:,.0f}")
    output.append(f"  일반 히트: {normal['normal_hit']:,.0f}")
    output.append(f"  크리티컬: {normal['crit_hit']:,.0f}")
    output.append(f"  발당 평균: {normal['avg_per_shot']:,.0f}")
    output.append("")
    
    output.append("【 헤드샷 타격 】")
    output.append(f"  일반 헤드샷: {headshot['normal_hit']:,.0f}")
    output.append(f"  크리 헤드샷: {headshot['crit_hit']:,.0f}")
    output.append(f"  발당 평균: {headshot['avg_per_shot']:,.0f}")
    output.append("")
    
    output.append("【 DPS 분석 】")
    output.append(f"  순간 DPS (몸통): {normal['burst_dps']:,.0f}")
    output.append(f"  순간 DPS (헤드): {headshot['burst_dps']:,.0f}")
    output.append(f"  지속 DPS (재장전 포함): {normal['sustained_dps']:,.0f}")
    output.append(f"  탄창당 총 데미지: {normal['magazine_damage']:,.0f}")
    output.append(f"  탄창 소진 시간: {normal['time_to_empty']}초")
    output.append("")
    
    return "\n".join(output)


def main():
    """메인 실행"""
    print("=" * 80)
    print("🎮 원스휴먼 실전 대미지 계산기 v2.0")
    print("=" * 80)
    print()
    
    calculator = DamageCalculator()
    
    # 모든 빌드 테스트 (레벨 30 적 기준)
    print("📊 모든 빌드 분석 (적 레벨 30)\n")
    
    all_builds = BuildPresets.get_all_builds()
    results = []
    
    for build_name in all_builds.keys():
        result = BuildPresets.calculate_build(calculator, build_name, enemy_level=30)
        results.append(result)
        print(format_result(result))
        print()
    
    # DPS 순위
    print("=" * 80)
    print("📈 DPS 순위 (몸통 타격 기준)")
    print("=" * 80)
    
    sorted_results = sorted(results, key=lambda x: x['normal']['burst_dps'], reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        normal = result['normal']
        print(f"{i}. {result['build_name']:20s} - "
              f"순간 DPS: {normal['burst_dps']:>8,.0f} | "
              f"지속 DPS: {normal['sustained_dps']:>8,.0f}")
    
    print()
    print("=" * 80)
    print("💡 팁:")
    print("  - 헤드샷 크리티컬이 가장 높은 데미지를 냅니다")
    print("  - 방어관통은 고레벨 적에게 중요합니다")
    print("  - 연사력이 높으면 실수를 용서합니다")
    print("  - 재장전 시간도 DPS에 큰 영향을 줍니다")
    print("=" * 80)


if __name__ == "__main__":
    main()
    
    def _init_builds(self) -> Dict:
        """빌드 데이터 초기화"""
        return {
            'M82A1 루퍼스 크리': {
                'weapon': 'M82A1 저격총',
                'weapon_power': 280,  # 높은 위력
                'stats': {
                    'attack': 350,
                    'crit_rate': 45,  # 45% 극대율
                    'crit_damage': 150,  # 극대 피해 150% 추가
                    'armor_pen': 20,
                    'attack_speed': 0.8,  # 느린 공격속도
                    'grade': '신화'
                },
                'description': '원거리 스나이퍼 빌드 - 높은 단일 피해'
            },
            '데저트이글 백상아리 크리': {
                'weapon': '데저트이글',
                'weapon_power': 200,
                'stats': {
                    'attack': 320,
                    'crit_rate': 50,  # 50% 극대율
                    'crit_damage': 140,  # 극대 피해 140% 추가
                    'armor_pen': 15,
                    'attack_speed': 1.5,  # 빠른 공격속도
                    'grade': '전설'
                },
                'description': '근거리 고속 공격 - 높은 DPS'
            },
            '신화검 탱커': {
                'weapon': '신화검',
                'weapon_power': 200,
                'stats': {
                    'attack': 280,
                    'crit_rate': 15,  # 낮은 극대율
                    'crit_damage': 50,  # 낮은 극대 피해
                    'armor_pen': 10,
                    'attack_speed': 1.0,
                    'grade': '신화'
                },
                'description': '탱커 빌드 - 생존 중심, 낮은 피해'
            },
            '마법사 원소': {
                'weapon': '마법 반지',
                'weapon_power': 150,
                'stats': {
                    'attack': 400,  # 마법력으로 환산
                    'crit_rate': 20,
                    'crit_damage': 100,
                    'armor_pen': 5,
                    'attack_speed': 1.2,
                    'grade': '전설'
                },
                'description': '범위 마법 공격 - 광범위 피해'
            },
            '극대율 풀극': {
                'weapon': '신화검',
                'weapon_power': 240,
                'stats': {
                    'attack': 420,
                    'crit_rate': 75,  # 매우 높은 극대율
                    'crit_damage': 200,  # 매우 높은 극대 피해
                    'armor_pen': 25,
                    'attack_speed': 1.1,
                    'grade': '신화'
                },
                'description': '극한 빌드 - 최고 DPS, 높은 위험도'
            }
        }
    
    def analyze_build(self, build_name: str, enemy_level: int = 25) -> Dict:
        """빌드 분석"""
        if build_name not in self.builds:
            return {'error': f'빌드 "{build_name}"을 찾을 수 없습니다'}
        
        build_data = self.builds[build_name]
        
        # 레벨에 따른 적 방어력 (레벨 * 2 + 10)
        enemy_defense = enemy_level * 2 + 10
        
        # 계산
        result = self.calculator.full_calculation(
            weapon_name=build_data['weapon'],
            weapon_power=build_data['weapon_power'],
            stats=build_data['stats'],
            enemy_defense=enemy_defense
        )
        
        result['build_name'] = build_name
        result['build_description'] = build_data['description']
        result['enemy_level'] = enemy_level
        
        return result
    
    def compare_builds(self, build_names: List[str], enemy_level: int = 25) -> List[Dict]:
        """빌드 비교"""
        results = []
        for build_name in build_names:
            results.append(self.analyze_build(build_name, enemy_level))
        
        # DPS 순으로 정렬
        results.sort(key=lambda x: x.get('dps', 0), reverse=True)
        
        return results
    
    def get_all_builds(self) -> List[str]:
        """모든 빌드 목록"""
        return list(self.builds.keys())

def format_damage_result(result: Dict) -> str:
    """대미지 계산 결과를 포맷팅"""
    if 'error' in result:
        return f"❌ {result['error']}"
    
    output = []
    output.append("=" * 70)
    output.append(f"🎯 {result.get('build_name', '')} - {result.get('weapon', '')}")
    output.append(f"📝 {result.get('build_description', '')}")
    output.append("=" * 70)
    output.append("")
    
    output.append("【 기본 정보 】")
    output.append(f"  적 레벨: {result.get('enemy_level', '?')} (방어력: {result.get('enemy_defense', '?')})")
    output.append(f"  공격속도: {result.get('attack_speed', '?')}회/초")
    output.append("")
    
    output.append("【 대미지 계산 】")
    output.append(f"  기본 대미지: {result.get('base_damage', '?'):,.0f}")
    output.append(f"  일반 공격: {result.get('normal_damage', '?'):,.0f}")
    output.append(f"  극대 공격: {result.get('crit_damage', '?'):,.0f} (극대율 {result.get('crit_rate', '?')})")
    output.append(f"  평균 대미지: {result.get('average_damage', '?'):,.0f}")
    output.append("")
    
    output.append("【 최종 대미지 】")
    output.append(f"  방어관통: {result.get('armor_penetration', '?')}")
    output.append(f"  최종 피해: {result.get('final_damage', '?'):,.0f}")
    output.append(f"  DPS: {result.get('dps', '?'):,.0f} 💥")
    output.append("=" * 70)
    
    return "\n".join(output)

def main():
    print("=" * 70)
    print("🎮 원스휴먼 대미지 계산기")
    print("=" * 70)
    
    # 계산기 초기화
    calculator = DamageCalculator()
    analyzer = BuildDamageAnalyzer(calculator)
    
    print("\n📊 모든 빌드 분석 (적 레벨 25):\n")
    
    # 모든 빌드 비교
    all_builds = analyzer.get_all_builds()
    results = analyzer.compare_builds(all_builds, enemy_level=25)
    
    # 결과 출력
    for result in results:
        print(format_damage_result(result))
        print()
    
    # 통계
    print("\n" + "=" * 70)
    print("📈 빌드별 대미지 비교 (적 레벨 25)")
    print("=" * 70)
    
    print("\n【 최종 피해 순위 】")
    for i, result in enumerate(results, 1):
        final_dmg = result.get('final_damage', 0)
        build_name = result.get('build_name', '')
        weapon = result.get('weapon', '')
        print(f"{i}. {build_name} ({weapon}): {final_dmg:,.0f} 피해")
    
    print("\n【 DPS 순위 】")
    dps_results = sorted(results, key=lambda x: x.get('dps', 0), reverse=True)
    for i, result in enumerate(dps_results, 1):
        dps = result.get('dps', 0)
        build_name = result.get('build_name', '')
        print(f"{i}. {build_name}: {dps:,.0f} DPS")
    
    # 상황별 분석
    print("\n" + "=" * 70)
    print("🎯 상황별 빌드 추천")
    print("=" * 70)
    
    print("\n【 보스 전투 (적 레벨 40 - 높은 방어력) 】")
    boss_results = analyzer.compare_builds(all_builds, enemy_level=40)
    for i, result in enumerate(boss_results[:3], 1):
        build_name = result.get('build_name', '')
        dps = result.get('dps', 0)
        print(f"{i}. {build_name}: {dps:,.0f} DPS")
    
    print("\n【 몬스터 사냥 (적 레벨 20 - 낮은 방어력) 】")
    mob_results = analyzer.compare_builds(all_builds, enemy_level=20)
    for i, result in enumerate(mob_results[:3], 1):
        build_name = result.get('build_name', '')
        dps = result.get('dps', 0)
        print(f"{i}. {build_name}: {dps:,.0f} DPS")
    
    print("\n" + "=" * 70)
    print("✅ 대미지 계산 완료!")
    print("=" * 70)
    
    # JSON 저장
    print("\n💾 계산 결과를 파일로 저장 중...")
    
    output_data = {
        'calculator_version': '1.0',
        'timestamp': '2026-01-29',
        'builds': {
            'level_25': results,
            'level_40_boss': boss_results,
            'level_20_mob': mob_results
        }
    }
    
    with open('damage_calculation_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print("✅ damage_calculation_results.json 저장 완료")

if __name__ == "__main__":
    main()
