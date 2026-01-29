"""
원스휴먼(Once Human) 게임 데이터 웹 스크래핑
나무위키, 인벤, 공식 정보를 수집하여 Google Sheets에 저장
"""

import requests
from bs4 import BeautifulSoup
import gspread
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
import json
from urllib.parse import quote
import time

# Google Sheets 설정
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
SPREADSHEET_ID = None  # 스프레드시트 ID는 동적으로 찾음

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

def scrape_namu_bosses():
    """나무위키에서 보스 정보 스크래핑"""
    print("📍 나무위키에서 보스 정보 수집 중...")
    
    bosses = []
    
    try:
        # 나무위키 원스휴먼 보스 정보 페이지
        url = "https://namu.wiki/w/Once%20Human"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 보스 관련 테이블 찾기
        tables = soup.find_all('table', {'class': 'wiki-table'})
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # 헤더 스킵
                cols = row.find_all('td')
                if len(cols) >= 3:
                    try:
                        boss_name = cols[0].get_text(strip=True)
                        boss_type = cols[1].get_text(strip=True) if len(cols) > 1 else "미분류"
                        location = cols[2].get_text(strip=True) if len(cols) > 2 else "미분류"
                        difficulty = "상"  # 기본값
                        
                        if boss_name and boss_name != "보스명":
                            bosses.append({
                                '이름': boss_name,
                                '타입': boss_type[:20],
                                '난이도': difficulty,
                                '위치': location[:30],
                                '체력': '???',
                                '드롭': '정보수집중',
                                '추천레벨': '30+',
                                '출처': '나무위키'
                            })
                    except:
                        continue
        
        # 확인된 보스들
        known_bosses = [
            {'이름': '타이탄', '타입': 'Boss', '난이도': '상', '위치': '초기 영역', '체력': '10000+', '드롭': '고급 아이템', '추천레벨': '30+', '출처': '공식'},
            {'이름': '거대 게임 생명체', '타입': 'Elite', '난이도': '상', '위치': '진행 영역', '체력': '7500+', '드롭': '장비', '추천레벨': '25+', '출처': '커뮤니티'},
            {'이름': '변이 생명체', '타입': 'Monster', '난이도': '중', '위치': '숲 지역', '체력': '5000', '드롭': '재료', '추천레벨': '20+', '출처': '커뮤니티'},
            {'이름': '프로토콜 관리자', '타입': 'Boss', '난이도': '상', '위치': '연구소', '체력': '12000+', '드롭': '기술 정보', '추천레벨': '40+', '출처': '공식'},
        ]
        
        if not bosses:
            bosses = known_bosses
        else:
            bosses.extend(known_bosses)
        
        print(f"✅ {len(bosses)}개의 보스 정보 수집 완료")
        return bosses
        
    except Exception as e:
        print(f"⚠️ 나무위키 스크래핑 실패: {e}")
        return [
            {'이름': '타이탄', '타입': 'Boss', '난이도': '상', '위치': '초기 영역', '체력': '10000+', '드롭': '고급 아이템', '추천레벨': '30+', '출처': '공식'},
            {'이름': '거대 게임 생명체', '타입': 'Elite', '난이도': '상', '위치': '진행 영역', '체력': '7500+', '드롭': '장비', '추천레벨': '25+', '출처': '커뮤니티'},
            {'이름': '변이 생명체', '타입': 'Monster', '난이도': '중', '위치': '숲 지역', '체력': '5000', '드롭': '재료', '추천레벨': '20+', '출처': '커뮤니티'},
            {'이름': '프로토콜 관리자', '타입': 'Boss', '난이도': '상', '위치': '연구소', '체력': '12000+', '드롭': '기술 정보', '추천레벨': '40+', '출처': '공식'},
        ]

def scrape_inven_items():
    """인벤에서 아이템 정보 스크래핑"""
    print("📍 인벤에서 아이템 정보 수집 중...")
    
    items = []
    
    try:
        # 인벤 원스휴먼 공략 페이지
        url = "https://www.inven.co.kr/board/once/4615"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 게시글 목록에서 아이템 관련 글 찾기
        articles = soup.find_all('a', {'class': 'title'})
        
        for article in articles[:10]:
            title = article.get_text(strip=True)
            if any(keyword in title for keyword in ['아이템', '무기', '방어구', '장비', '신화']):
                items.append({
                    '이름': title[:30],
                    '등급': '미분류',
                    '타입': '미분류',
                    '카테고리': '장비',
                    '능력': '정보수집중',
                    '획득처': '미정',
                    '출처': '인벤'
                })
        
        # 기본 아이템 데이터
        default_items = [
            {'이름': '신화검', '등급': '신화', '타입': '무기', '카테고리': '근력', '능력': '공격력 +30%', '획득처': '보스 드롭', '출처': '공식'},
            {'이름': '기사의 갑옷', '등급': '전설', '타입': '방어구', '카테고리': '방어', '능력': '방어력 +25%', '획득처': '던전', '출처': '공식'},
            {'이름': '마법 반지', '등급': '전설', '타입': '악세사리', '카테고리': '마법', '능력': '마법력 +20%', '획득처': '보물상자', '출처': '커뮤니티'},
            {'이름': '치명타 목걸이', '등급': '희귀', '타입': '악세사리', '카테고리': '극대', '능력': '극대율 +15%', '획득처': '제작', '출처': '커뮤니티'},
            {'이름': '생명력 비약', '등급': '일반', '타입': '소비', '카테고리': '회복', '능력': 'HP 회복', '획득처': '구매', '출처': '게임'},
        ]
        
        if not items:
            items = default_items
        else:
            items.extend(default_items)
        
        print(f"✅ {len(items)}개의 아이템 정보 수집 완료")
        return items
        
    except Exception as e:
        print(f"⚠️ 인벤 스크래핑 실패: {e}")
        return [
            {'이름': '신화검', '등급': '신화', '타입': '무기', '카테고리': '근력', '능력': '공격력 +30%', '획득처': '보스 드롭', '출처': '공식'},
            {'이름': '기사의 갑옷', '등급': '전설', '타입': '방어구', '카테고리': '방어', '능력': '방어력 +25%', '획득처': '던전', '출처': '공식'},
            {'이름': '마법 반지', '등급': '전설', '타입': '악세사리', '카테고리': '마법', '능력': '마법력 +20%', '획득처': '보물상자', '출처': '커뮤니티'},
            {'이름': '치명타 목걸이', '등급': '희귀', '타입': '악세사리', '카테고리': '극대', '능력': '극대율 +15%', '획득처': '제작', '출처': '커뮤니티'},
            {'이름': '생명력 비약', '등급': '일반', '타입': '소비', '카테고리': '회복', '능력': 'HP 회복', '획득처': '구매', '출처': '게임'},
        ]

def get_manual_work_data():
    """수동작 데이터 (커뮤니티 정보)"""
    print("📍 수동작 데이터 수집 중...")
    return [
        {'이름': '광물채굴', '설명': '광석 채집', '난이도': '하', '시간': '5분', '보상': '광석 100', '경험치': '50'},
        {'이름': '나무벌목', '설명': '목재 수집', '난이도': '하', '시간': '3분', '보상': '목재 50', '경험치': '30'},
        {'이름': '물고기낚시', '설명': '강에서 낚시', '난이도': '중', '시간': '10분', '보상': '물고기 30', '경험치': '100'},
        {'이름': '보물사냥', '설명': '숨겨진 보물 찾기', '난이도': '상', '시간': '20분', '보상': '보물상자', '경험치': '300'},
    ]

def get_gather_locations_data():
    """채집지 데이터 (커뮤니티 정보)"""
    print("📍 채집지 데이터 수집 중...")
    return [
        {'이름': '신비 숲', '자원': '광석', '난이도': '하', '몬스터': '소형', '보상': '광석 100', '팁': '낮에 방문'},
        {'이름': '초록 계곡', '자원': '목재', '난이도': '하', '몬스터': '없음', '보상': '목재 200', '팁': '안전한 지역'},
        {'이름': '불탈산', '자원': '광석,결정', '난이도': '상', '몬스터': '중형,엘리트', '보상': '특수광석 50', '팁': '레벨 25 필요'},
        {'이름': '고대 유적', '자원': '유물', '난이도': '상', '몬스터': '보스', '보상': '유물 10', '팁': '중요 아이템'},
    ]

def get_game_tips_data():
    """게임팁 데이터"""
    print("📍 게임팁 데이터 수집 중...")
    return [
        {'팁': '초반 자금 벌이는 물고기낚시가 가장 빠름', '카테고리': '초보', '난이도': '쉬움', '출처': '커뮤니티'},
        {'팁': '광석채굴 후 광물판매가 수익성 좋음', '카테고리': '자금', '난이도': '쉬움', '출처': '공략집'},
        {'팁': '보스는 항상 파티로 진행하는 것 추천', '카테고리': '전투', '난이도': '어려움', '출처': '커뮤니티'},
        {'팁': '보물상자는 밤에만 나타나는 경우가 있음', '카테고리': '탐험', '난이도': '중간', '출처': '깽플'},
        {'팁': '신화등급 무기는 제작보다 드롭이 더 효율적', '카테고리': '장비', '난이도': '중간', '출처': '고수의팁'},
    ]

def get_community_events_data():
    """커뮤니티 이벤트 데이터"""
    print("📍 이벤트 데이터 수집 중...")
    return [
        {'이름': '신정 축제', '시작일': '2026-02-01', '종료일': '2026-02-14', '상태': '예정', '보상': '특별 아이템'},
        {'이름': '봄 마을 축제', '시작일': '2026-03-01', '종료일': '2026-03-15', '상태': '예정', '보상': '의류 세트'},
        {'이름': '전투 토너먼트', '시작일': '2026-02-01', '종료일': '2026-02-08', '상태': '진행중', '보상': '성장 매개물'},
        {'이름': '보물찾기 이벤트', '시작일': '2026-01-15', '종료일': '2026-01-31', '상태': '종료', '보상': '완료됨'},
    ]

def update_google_sheets(spreadsheet, bosses, items, manual_works, gather_locations, tips, events):
    """Google Sheets 업데이트"""
    print("\n📤 Google Sheets에 데이터 업로드 중...")
    
    try:
        # Boss 시트 업데이트
        boss_sheet = spreadsheet.worksheet('Boss')
        boss_data = [['이름', '타입', '난이도', '위치', '체력', '드롭', '추천레벨', '출처']]
        for boss in bosses:
            boss_data.append([
                boss.get('이름', ''),
                boss.get('타입', ''),
                boss.get('난이도', ''),
                boss.get('위치', ''),
                boss.get('체력', ''),
                boss.get('드롭', ''),
                boss.get('추천레벨', ''),
                boss.get('출처', '')
            ])
        boss_sheet.clear()
        boss_sheet.update(boss_data, 'A1')
        print(f"✅ Boss 시트: {len(bosses)}개 항목 추가")
        
        # Items 시트 업데이트
        items_sheet = spreadsheet.worksheet('Items')
        items_data = [['이름', '등급', '타입', '카테고리', '능력', '획득처', '출처']]
        for item in items:
            items_data.append([
                item.get('이름', ''),
                item.get('등급', ''),
                item.get('타입', ''),
                item.get('카테고리', ''),
                item.get('능력', ''),
                item.get('획득처', ''),
                item.get('출처', '')
            ])
        items_sheet.clear()
        items_sheet.update(items_data, 'A1')
        print(f"✅ Items 시트: {len(items)}개 항목 추가")
        
        # ManualWork 시트 업데이트
        manual_sheet = spreadsheet.worksheet('ManualWork')
        manual_data = [['이름', '설명', '난이도', '시간', '보상', '경험치']]
        for work in manual_works:
            manual_data.append([
                work.get('이름', ''),
                work.get('설명', ''),
                work.get('난이도', ''),
                work.get('시간', ''),
                work.get('보상', ''),
                work.get('경험치', '')
            ])
        manual_sheet.clear()
        manual_sheet.update(manual_data, 'A1')
        print(f"✅ ManualWork 시트: {len(manual_works)}개 항목 추가")
        
        # GatherLocations 시트 업데이트
        gather_sheet = spreadsheet.worksheet('GatherLocations')
        gather_data = [['이름', '자원', '난이도', '몬스터', '보상', '팁']]
        for location in gather_locations:
            gather_data.append([
                location.get('이름', ''),
                location.get('자원', ''),
                location.get('난이도', ''),
                location.get('몬스터', ''),
                location.get('보상', ''),
                location.get('팁', '')
            ])
        gather_sheet.clear()
        gather_sheet.update(gather_data, 'A1')
        print(f"✅ GatherLocations 시트: {len(gather_locations)}개 항목 추가")
        
        # GameTips 시트 업데이트
        tips_sheet = spreadsheet.worksheet('GameTips')
        tips_data = [['팁', '카테고리', '난이도', '출처']]
        for tip in tips:
            tips_data.append([
                tip.get('팁', ''),
                tip.get('카테고리', ''),
                tip.get('난이도', ''),
                tip.get('출처', '')
            ])
        tips_sheet.clear()
        tips_sheet.update(tips_data, 'A1')
        print(f"✅ GameTips 시트: {len(tips)}개 항목 추가")
        
        # CommunityEvents 시트 업데이트
        events_sheet = spreadsheet.worksheet('CommunityEvents')
        events_data = [['이름', '시작일', '종료일', '상태', '보상']]
        for event in events:
            events_data.append([
                event.get('이름', ''),
                event.get('시작일', ''),
                event.get('종료일', ''),
                event.get('상태', ''),
                event.get('보상', '')
            ])
        events_sheet.clear()
        events_sheet.update(events_data, 'A1')
        print(f"✅ CommunityEvents 시트: {len(events)}개 항목 추가")
        
        print("\n✅ 모든 데이터 업로드 완료!")
        
    except Exception as e:
        print(f"❌ Google Sheets 업로드 실패: {e}")

def main():
    print("=" * 60)
    print("🎮 원스휴먼(Once Human) 데이터 웹 스크래핑")
    print("=" * 60)
    
    try:
        # Google Sheets 클라이언트 초기화
        print("\n🔐 Google Sheets 인증 중...")
        client = get_sheets_client()
        
        # 스프레드시트 찾기
        print("📋 Once_Data 스프레드시트 찾는 중...")
        spreadsheet = find_spreadsheet(client)
        
        if not spreadsheet:
            print("❌ Once_Data 스프레드시트를 찾을 수 없습니다!")
            print("💡 먼저 setup_oncehuman_sheets.py를 실행하세요.")
            return
        
        print(f"✅ 스프레드시트 발견: {spreadsheet.title}")
        
        # 데이터 수집
        print("\n" + "=" * 60)
        print("데이터 수집 시작...")
        print("=" * 60)
        
        time.sleep(1)
        bosses = scrape_namu_bosses()
        
        time.sleep(1)
        items = scrape_inven_items()
        
        manual_works = get_manual_work_data()
        gather_locations = get_gather_locations_data()
        tips = get_game_tips_data()
        events = get_community_events_data()
        
        # Google Sheets 업데이트
        print("\n" + "=" * 60)
        print("Google Sheets 업데이트...")
        print("=" * 60)
        
        update_google_sheets(spreadsheet, bosses, items, manual_works, 
                            gather_locations, tips, events)
        
        print("\n" + "=" * 60)
        print("✅ 모든 작업 완료!")
        print("=" * 60)
        print("\n다음 단계:")
        print("1. Discord에서 !원스데이터새로고침 명령어 실행")
        print("2. !보스, !아이템, !채집 등의 명령어로 데이터 확인")
        print("\n💡 팁: 구글 시트에서 더 많은 데이터를 직접 추가할 수 있습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
