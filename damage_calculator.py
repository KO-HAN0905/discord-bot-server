"""
원스휴먼 대미지 계산기
아이템, 모듈, 스탯 기반 대미지 계산
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from typing import Dict, List, Tuple

# Google Sheets 설정
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_sheets_client():
    """Google Sheets API 클라이언트 초기화"""
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def find_spreadsheet(client, sheet_name="Once_Data"):
    """Once_Data 스프레드시트 찾기"""
    spreadsheets = client.list_spreadsheet_files()
    for sheet in spreadsheets:
        if sheet['name'] == sheet_name:
            return client.open_by_key(sheet['id'])
    return None

class DamageCalculator:
    """원스휴먼 대미지 계산 엔진"""
    
    def __init__(self):
        self.base_damage = 100
        self.crit_rate = 0.0  # 극대율 (%)
        self.crit_damage = 1.0  # 극대 피해배율
        self.armor_pen = 0  # 방어관통
        self.elemental_damage = 0  # 원소 피해
        self.attack_speed = 1.0  # 공격속도
        self.buffs = {}  # 버프
        
    def calculate_base_damage(self, weapon_power: int, stats: Dict) -> float:
        """기본 대미지 계산"""
        # 기본 공격력
        base = weapon_power
        
        # 스탯 기반 공격력 보정 (공격력 수치 * 0.1)
        attack_bonus = stats.get('attack', 0) * 0.1
        
        # 무기 등급 보정
        grade_bonus = {
            '신화': 1.3,
            '전설': 1.15,
            '희귀': 1.05,
            '일반': 1.0
        }
        grade = stats.get('grade', '일반')
        grade_multiplier = grade_bonus.get(grade, 1.0)
        
        return (base + attack_bonus) * grade_multiplier
    
    def calculate_crit_damage(self, base_damage: float, stats: Dict) -> Tuple[float, float, float]:
        """극대 피해 계산
        
        Returns:
            일반 피해, 극대 피해, 평균 피해
        """
        crit_rate = stats.get('crit_rate', 0) / 100.0  # % -> 소수
        crit_damage = stats.get('crit_damage', 100) / 100.0 + 1.0  # 100% = 2배
        
        normal_damage = base_damage
        crit_hit_damage = base_damage * crit_damage
        
        # 평균 대미지 = (일반확률 * 일반피해) + (극대확률 * 극대피해)
        avg_damage = (1 - crit_rate) * normal_damage + crit_rate * crit_hit_damage
        
        return normal_damage, crit_hit_damage, avg_damage
    
    def calculate_enemy_defense(self, avg_damage: float, enemy_defense: int, armor_pen: int) -> float:
        """방어력 적용
        
        방어력 계산식:
        - 실제방어력 = 적방어력 - 방어관통
        - 최종피해 = 기본피해 * (100 / (100 + 실제방어력))
        """
        actual_defense = max(0, enemy_defense - armor_pen)
        
        # 방어력이 높을수록 피해감소
        defense_reduction = 100 / (100 + actual_defense * 0.5)  # 방어력 영향도 50%
        
        final_damage = avg_damage * defense_reduction
        
        return final_damage
    
    def calculate_dps(self, final_damage: float, attack_speed: float, hit_rate: float = 1.0) -> float:
        """DPS (초당 피해) 계산"""
        return final_damage * attack_speed * hit_rate
    
    def full_calculation(self, 
                        weapon_name: str,
                        weapon_power: int,
                        stats: Dict,
                        enemy_defense: int = 30,
                        modifiers: Dict = None) -> Dict:
        """전체 대미지 계산"""
        
        if modifiers is None:
            modifiers = {}
        
        # 1. 기본 대미지
        base_dmg = self.calculate_base_damage(weapon_power, stats)
        
        # 2. 극대 피해 (일반, 극대, 평균)
        normal_dmg, crit_dmg, avg_dmg = self.calculate_crit_damage(base_dmg, stats)
        
        # 3. 방어력 적용
        armor_pen = stats.get('armor_pen', 0) + modifiers.get('armor_pen', 0)
        final_dmg = self.calculate_enemy_defense(avg_dmg, enemy_defense, armor_pen)
        
        # 4. 버프 적용
        buff_multiplier = 1.0
        if 'buff' in modifiers:
            buff_multiplier = modifiers['buff']
        
        final_dmg *= buff_multiplier
        
        # 5. DPS 계산
        attack_speed = stats.get('attack_speed', 1.0)
        dps = self.calculate_dps(final_dmg, attack_speed)
        
        return {
            'weapon': weapon_name,
            'base_damage': round(base_dmg, 2),
            'normal_damage': round(normal_dmg, 2),
            'crit_damage': round(crit_dmg, 2),
            'average_damage': round(avg_dmg, 2),
            'enemy_defense': enemy_defense,
            'armor_penetration': armor_pen,
            'final_damage': round(final_dmg, 2),
            'attack_speed': attack_speed,
            'dps': round(dps, 2),
            'crit_rate': f"{stats.get('crit_rate', 0):.1f}%",
            'crit_damage_multiplier': f"{stats.get('crit_damage', 100) / 100 + 1:.2f}x"
        }

class BuildDamageAnalyzer:
    """빌드별 대미지 분석"""
    
    def __init__(self, calculator: DamageCalculator):
        self.calculator = calculator
        self.builds = self._init_builds()
    
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
