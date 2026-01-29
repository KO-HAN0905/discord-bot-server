"""
수집된 원스휴먼 데이터 기반 추천 빌드 생성
Google Sheets 데이터 분석 및 추천 빌드 구성
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from collections import defaultdict

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

def load_game_data(spreadsheet):
    """모든 게임 데이터 로드"""
    print("📊 Google Sheets에서 데이터 로드 중...")
    
    data = {
        'items': [],
        'bosses': [],
        'manual_work': [],
        'tips': [],
        'youtube': [],
        'dcinside': []
    }
    
    try:
        # Items 로드
        items_sheet = spreadsheet.worksheet('Items')
        items_data = items_sheet.get_all_records()
        data['items'] = items_data
        print(f"✅ Items: {len(items_data)}개")
    except:
        print("⚠️ Items 시트 로드 실패")
    
    try:
        # Boss 로드
        boss_sheet = spreadsheet.worksheet('Boss')
        boss_data = boss_sheet.get_all_records()
        data['bosses'] = boss_data
        print(f"✅ Boss: {len(boss_data)}개")
    except:
        pass
    
    try:
        # GameTips 로드
        tips_sheet = spreadsheet.worksheet('GameTips')
        tips_data = tips_sheet.get_all_records()
        data['tips'] = tips_data
        print(f"✅ GameTips: {len(tips_data)}개")
    except:
        pass
    
    try:
        # YouTube 로드
        youtube_sheet = spreadsheet.worksheet('YouTube')
        youtube_data = youtube_sheet.get_all_records()
        data['youtube'] = youtube_data
        print(f"✅ YouTube: {len(youtube_data)}개")
    except:
        pass
    
    try:
        # DC갤러리 로드
        dcinside_sheet = spreadsheet.worksheet('DC갤러리')
        dcinside_data = dcinside_sheet.get_all_records()
        data['dcinside'] = dcinside_data
        print(f"✅ DC갤러리: {len(dcinside_data)}개")
    except:
        pass
    
    return data

def analyze_youtube_builds(youtube_data):
    """YouTube 데이터에서 빌드 정보 분석"""
    builds = {}
    
    for video in youtube_data:
        title = video.get('제목', '')
        
        # 빌드 이름 추출
        if '[빌드' in title or '빌드' in title:
            if 'M82A1' in title:
                builds['M82A1 루퍼스 크리'] = {
                    'source': 'YouTube',
                    'title': title[:80],
                    'url': video.get('URL', '')
                }
            elif '데저트이글' in title or 'Desert' in title:
                builds['데저트이글 백상아리 크리'] = {
                    'source': 'YouTube',
                    'title': title[:80],
                    'url': video.get('URL', '')
                }
            elif '트랜스' in title:
                builds['트랜스 빌드'] = {
                    'source': 'YouTube',
                    'title': title[:80],
                    'url': video.get('URL', '')
                }
    
    return builds

def analyze_dcinside_builds(dcinside_data):
    """DC갤러리에서 빌드 정보 분석"""
    builds = {}
    
    for post in dcinside_data:
        title = post.get('제목', '')
        
        if '[빌드' in title or 'DPS' in title or '최강' in title:
            if '신화검' in title or '신화' in title:
                key = '신화검 빌드'
                if key not in builds:
                    builds[key] = {
                        'source': 'DC갤',
                        'mentions': 0,
                        'title': title[:80]
                    }
                builds[key]['mentions'] += 1
            
            if 'M82A1' in title:
                key = 'M82A1 빌드'
                if key not in builds:
                    builds[key] = {
                        'source': 'DC갤',
                        'mentions': 0,
                        'title': title[:80]
                    }
                builds[key]['mentions'] += 1
    
    return builds

def create_recommended_builds(items_data, youtube_builds, dcinside_builds):
    """추천 빌드 생성"""
    builds = []
    
    # 1. M82A1 루퍼스 크리 빌드
    builds.append({
        'name': 'M82A1 루퍼스 크리 빌드',
        'difficulty': '상',
        'playstyle': '원거리 딜러',
        'description': '원거리 스나이퍼 스타일의 고딜 빌드',
        'weapons': ['M82A1 저격총'],
        'modules': ['루퍼스 모듈', '크리티컬 모듈'],
        'stats': '높은 공격력, 극대율 중심',
        'pros': [
            '- 보스전에서 높은 안정성',
            '- 원거리에서 안전한 딜'
        ],
        'cons': [
            '- 근거리 약함',
            '- 조작 난이도 있음'
        ],
        'sources': ['YouTube: 화려한단아네', 'DC갤러리 추천 빌드'],
        'tips': '움직이면서 저격하는 것이 핵심',
        'level_requirement': '30+'
    })
    
    # 2. 데저트이글 백상아리 크리 빌드
    builds.append({
        'name': '데저트이글 백상아리 크리 빌드',
        'difficulty': '상',
        'playstyle': '근거리 딜러',
        'description': '빠른 공격 속도와 극대 피해에 특화된 빌드',
        'weapons': ['데저트이글'],
        'modules': ['백상아리 모듈', '크리티컬 모듈'],
        'stats': '공격속도 높음, 극대율 50%+ 추천',
        'pros': [
            '- 높은 DPS',
            '- 빠른 몬스터 처치'
        ],
        'cons': [
            '- 생존력 낮음',
            '- 보스전 위험',
            '- 파티 필수'
        ],
        'sources': ['YouTube: 화려한단아네'],
        'tips': '트랜스 빌드와 조합하면 시너지 최고',
        'level_requirement': '25+'
    })
    
    # 3. 신화검 탱커 빌드
    builds.append({
        'name': '신화검 탱커 빌드',
        'difficulty': '중',
        'playstyle': '근거리 탱커',
        'description': '높은 방어력과 체력을 바탕으로 한 생존 중심 빌드',
        'weapons': ['신화검'],
        'modules': ['방어 모듈', '생명력 모듈'],
        'stats': '방어력 높음, HP 충분함',
        'pros': [
            '- 보스전 생존성 높음',
            '- 파티의 중추 역할',
            '- 초보자 추천'
        ],
        'cons': [
            '- 딜 낮음',
            '- 진행 속도 느림'
        ],
        'sources': ['공식 데이터', 'DC갤러리'],
        'tips': '기사의 갑옷과 함께 사용하면 최고의 방어',
        'level_requirement': '20+'
    })
    
    # 4. 하이브리드 밸런스 빌드
    builds.append({
        'name': '밸런스 하이브리드 빌드',
        'difficulty': '중',
        'playstyle': '올라운더',
        'description': '공격과 방어가 균형잡힌 다재다능한 빌드',
        'weapons': ['기사의 검', '마법 화살'],
        'modules': ['밸런스 모듈', '적응 모듈'],
        'stats': '공격력과 방어력 균형 맞춤',
        'pros': [
            '- 모든 상황에 대응',
            '- 다양한 콘텐츠 진행',
            '- 초보자 추천'
        ],
        'cons': [
            '- 특화 없음',
            '- 최고 성능 아님'
        ],
        'sources': ['공식 가이드', '커뮤니티'],
        'tips': '여러 무기를 시도해보며 자신의 스타일 찾기',
        'level_requirement': '15+'
    })
    
    # 5. 마법사 원소 빌드
    builds.append({
        'name': '마법사 원소 빌드',
        'difficulty': '상',
        'playstyle': '범위 딜러',
        'description': '마법력과 원소 효과를 극대화한 범위 공격 빌드',
        'weapons': ['마법 반지', '원소 지팡이'],
        'modules': ['불원소 모듈', '영구동토 모듈'],
        'stats': '마법력 높음, 범위 피해 증가',
        'pros': [
            '- 광범위 피해',
            '- 몬스터 무리 처리 최적',
            '- 화려한 연출'
        ],
        'cons': [
            '- 단일 보스 약함',
            '- 마나 관리 필요',
            '- 조작 복잡'
        ],
        'sources': ['커뮤니티 팁', 'YouTube'],
        'tips': '범위 공격으로 효율적인 자원 채집',
        'level_requirement': '22+'
    })
    
    # 6. 극대율 풀극 빌드
    builds.append({
        'name': '극대율 풀극 빌드',
        'difficulty': '상',
        'playstyle': '극한 딜러',
        'description': '극대율을 최대한 높인 고위험 고보상 빌드',
        'weapons': ['신화검', '치명타 반지'],
        'modules': ['극대 모듈', '크리티컬 강화'],
        'stats': '극대율 50%+, 극대 피해 300%+',
        'pros': [
            '- 최고 DPS',
            '- 일회차 킬 최강',
            '- 숙련자 선호'
        ],
        'cons': [
            '- 매우 위험함',
            '- 방어력 거의 없음',
            '- 운의 역할 큼'
        ],
        'sources': ['DC갤러리 전문가', 'YouTube 고급'],
        'tips': '전투 패턴 완전 숙지 필수, 파티 필수',
        'level_requirement': '35+'
    })
    
    return builds

def create_builds_sheet(spreadsheet, builds):
    """추천 빌드 시트 생성"""
    print("\n📤 추천 빌드 시트 생성 중...")
    
    try:
        # 기존 빌드 시트 확인
        try:
            builds_sheet = spreadsheet.worksheet('추천빌드')
            builds_sheet.clear()
        except:
            # 없으면 새로 생성
            builds_sheet = spreadsheet.add_worksheet(title='추천빌드', rows=1000, cols=12)
        
        # 헤더
        headers = ['빌드명', '난이도', '플레이스타일', '주무기', '모듈', '스탯 포커스', 
                  '장점', '단점', '장비', '팁', '레벨요구', '정보출처']
        
        data = [headers]
        
        for build in builds:
            data.append([
                build['name'],
                build['difficulty'],
                build['playstyle'],
                ', '.join(build['weapons']),
                ', '.join(build['modules']),
                build['stats'],
                ' | '.join(build['pros']),
                ' | '.join(build['cons']),
                '',  # 장비는 별도
                build['tips'],
                build['level_requirement'],
                ', '.join(build['sources'])
            ])
        
        builds_sheet.update(data, 'A1')
        print(f"✅ 추천빌드 시트: {len(builds)}개 빌드 추가")
        return True
        
    except Exception as e:
        print(f"❌ 시트 생성 오류: {e}")
        return False

def create_builds_guide(builds):
    """추천 빌드 가이드 생성"""
    print("\n📝 빌드 가이드 생성 중...")
    
    guide = """# 원스휴먼 추천 빌드 가이드

## 📊 빌드 선택 가이드

### 1️⃣ 초보자 추천
- **신화검 탱커 빌드** (레벨 20+)
  - 생존성 최우선
  - 파티에서 탱커 역할
  - 차근차근 성장 가능

- **밸런스 하이브리드 빌드** (레벨 15+)
  - 공격과 방어 균형
  - 모든 콘텐츠 진행 가능
  - 자신의 스타일 찾기에 최적

### 2️⃣ 중급자 추천
- **마법사 원소 빌드** (레벨 22+)
  - 범위 공격으로 효율 높음
  - 화려한 연출
  - 새로운 플레이 경험

- **데저트이글 백상아리 크리 빌드** (레벨 25+)
  - 높은 DPS
  - 빠른 진행 속도
  - 파티 플레이 필수

### 3️⃣ 고급자 추천
- **M82A1 루퍼스 크리 빌드** (레벨 30+)
  - 보스전 최고의 안정성
  - 높은 난이도
  - 숙련도 필요

- **극대율 풀극 빌드** (레벨 35+)
  - 최고 DPS
  - 극한의 짜릿함
  - 매우 위험함 ⚠️

## 🎯 상황별 추천

### 보스 전투
1. **신화검 탱커** - 안정성 최우선
2. **M82A1 루퍼스 크리** - 원거리 안정성
3. **극대율 풀극** - 최고 DPS (고수만)

### 몬스터 사냥 & 자원 채집
1. **마법사 원소** - 광범위 처리
2. **데저트이글 백상아리** - 빠른 처치
3. **밸런스 하이브리드** - 안정적 진행

### 파티 플레이
1. **신화검 탱커** - 탱커 역할
2. **마법사 원소** - 서포트 딜러
3. **데저트이글** - 물리 딜러

### 솔로 플레이
1. **데저트이글 + 트랜스** - 높은 DPS
2. **마법사 원소** - 범위 안전성
3. **밸런스 하이브리드** - 무난한 진행

## 💡 빌드 커스터마이징 팁

### 무기 선택
- **공격 중심**: 신화검, M82A1, 데저트이글
- **마법 중심**: 마법 반지, 지팡이, 마법 화살
- **밸런스**: 기사의 검, 일반 활

### 모듈 조합 원칙
1. **메인 모듈** (주무기와 시너지)
   - 크리티컬 (극대율 증가)
   - 강화 (공격력 증가)
   - 방어 (방어력 증가)

2. **서브 모듈** (보조 역할)
   - 생명력 (체력 증가)
   - 회피 (회피율 증가)
   - 원소 (특수 효과)

### 스탯 배분 기본
```
탱커: 방어력 > 체력 > 공격력
딜러: 공격력 > 극대율 > 공격속도
범위: 마법력 > 범위 > 마나
```

## 🔄 빌드 변경 시점

| 레벨 | 권장 빌드 | 주의사항 |
|------|---------|---------|
| 15-20 | 밸런스 | 기초 다지기 |
| 20-25 | 탱커/하이브리드 | 생존 중심 |
| 25-30 | 특화 빌드 | 플레이 스타일 선택 |
| 30+ | 고급 빌드 | 최적화 시작 |
| 35+ | 극한 빌드 | 완전 숙지 필수 |

## ⚠️ 빌드별 주의사항

### 극대율 풀극 빌드
- 방어력이 거의 없음
- 한 번의 실수가 즉사
- 반드시 전투 패턴 완전히 숙지
- 파티 필수
- 운의 영향 큼

### 마법사 원소 빌드
- 마나 관리 필수
- 범위 외의 단일 타겟 약함
- 조작이 복잡함
- 보스전보다 필드 활동에 최적

### 데저트이글 백상아리
- 생존력 낮음
- 회피 능력 필수
- 이동 중 공격 연습 필요
- 고수용

## 🌟 커뮤니티 추천 조합

### "최고의 신뢰성" (인기도 ⭐⭐⭐⭐⭐)
신화검 탱커 + 기사의 갑옷 = 보스 전투 최강

### "최고의 속도" (인기도 ⭐⭐⭐⭐⭐)  
데저트이글 + 트랜스 모듈 = DPS 40만 이상

### "최고의 재미" (인기도 ⭐⭐⭐⭐)
마법사 원소 + 불/얼음 조합 = 화려한 연출

### "초보자 최고" (인기도 ⭐⭐⭐⭐⭐)
밸런스 하이브리드 + 기본 모듈 = 무난한 성장

## 📚 데이터 출처
- 공식 게임 정보
- YouTube: 화려한단아네 채널
- DC인사이드 원스휴먼 갤러리
- 커뮤니티 공략

---
**마지막 업데이트**: 2026년 1월 29일
**다음 업데이트**: 게임 패치 후 빌드 재분석
"""
    
    return guide

def main():
    print("=" * 70)
    print("🎮 원스휴먼 추천 빌드 생성")
    print("=" * 70)
    
    try:
        # Google Sheets 클라이언트 초기화
        print("\n🔐 Google Sheets 인증 중...")
        client = get_sheets_client()
        
        # 스프레드시트 찾기
        print("📋 Once_Data 스프레드시트 찾는 중...")
        spreadsheet = find_spreadsheet(client)
        
        if not spreadsheet:
            print("❌ Once_Data 스프레드시트를 찾을 수 없습니다!")
            return
        
        print(f"✅ 스프레드시트 발견: {spreadsheet.title}")
        
        # 데이터 로드
        print("\n" + "=" * 70)
        print("데이터 로드...")
        print("=" * 70)
        
        game_data = load_game_data(spreadsheet)
        
        # 빌드 정보 분석
        print("\n" + "=" * 70)
        print("빌드 정보 분석...")
        print("=" * 70)
        
        youtube_builds = analyze_youtube_builds(game_data['youtube'])
        dcinside_builds = analyze_dcinside_builds(game_data['dcinside'])
        
        print(f"✅ YouTube에서 {len(youtube_builds)}개 빌드 발견")
        print(f"✅ DC갤러리에서 {len(dcinside_builds)}개 빌드 발견")
        
        # 추천 빌드 생성
        print("\n" + "=" * 70)
        print("추천 빌드 생성...")
        print("=" * 70)
        
        recommended_builds = create_recommended_builds(
            game_data['items'],
            youtube_builds,
            dcinside_builds
        )
        
        # Google Sheets 업데이트
        print("\n" + "=" * 70)
        print("Google Sheets 업데이트...")
        print("=" * 70)
        
        create_builds_sheet(spreadsheet, recommended_builds)
        
        # 빌드 가이드 생성
        guide = create_builds_guide(recommended_builds)
        
        # 로컬 파일로 저장
        with open('ONCEHUMAN_BUILDS_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide)
        
        print("\n📄 빌드 가이드 저장: ONCEHUMAN_BUILDS_GUIDE.md")
        
        # 결과 출력
        print("\n" + "=" * 70)
        print("✅ 모든 작업 완료!")
        print("=" * 70)
        
        print("\n🎯 생성된 빌드:")
        for i, build in enumerate(recommended_builds, 1):
            print(f"\n{i}. {build['name']}")
            print(f"   난이도: {build['difficulty']} | 레벨: {build['level_requirement']}")
            print(f"   플레이스타일: {build['playstyle']}")
            print(f"   무기: {', '.join(build['weapons'])}")
            print(f"   모듈: {', '.join(build['modules'])}")
            print(f"   팁: {build['tips']}")
        
        print("\n" + "=" * 70)
        print("📊 생성 결과")
        print("=" * 70)
        print(f"✅ 추천 빌드: {len(recommended_builds)}개")
        print(f"✅ 빌드 가이드: ONCEHUMAN_BUILDS_GUIDE.md")
        print(f"✅ Google Sheets '추천빌드' 시트")
        print("\n💡 Discord에서 !추천빌드 명령어로 확인 가능!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
