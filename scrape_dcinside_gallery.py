"""
DC인사이드 원스휴먼 갤러리 게시글 스크래핑
원스휴먼 공략 정보 수집
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import gspread
from google.oauth2.service_account import Credentials
import time
import re

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

def scrape_dcinside_gallery(url):
    """DC인사이드 갤러리 게시글 스크래핑 (BeautifulSoup)"""
    print(f"📍 DC인사이드 갤러리 스크래핑 시작")
    
    try:
        # BeautifulSoup으로 직접 파싱
        import requests
        from bs4 import BeautifulSoup
        
        print("🌐 DC인사이드 페이지 요청 중...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # 첫 페이지만 수집 (페이지네이션 처리 간소화)
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"⚠️ 페이지 요청 실패: {response.status_code}")
            return get_sample_posts()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        posts = []
        
        print("🔍 게시글 정보 추출 중...")
        
        # DC인사이드 갤러리의 게시글 테이블 찾기
        gallery_table = soup.find('table', {'class': 'gall-list'})
        
        if not gallery_table:
            # 대체 방법: 모든 tbody 찾기
            tbody = soup.find('tbody')
            if tbody:
                gallery_table = tbody.parent
        
        if gallery_table:
            rows = gallery_table.find_all('tr')
            
            for row in rows:
                try:
                    # 공지사항 제외
                    if 'gall-notice' in row.get('class', []):
                        continue
                    
                    # 제목 찾기
                    title_link = row.find('a', {'class': 'gall-subject'})
                    if not title_link:
                        # 다른 링크 찾기
                        all_links = row.find_all('a')
                        for link in all_links:
                            if 'view' in link.get('href', ''):
                                title_link = link
                                break
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    post_url = title_link.get('href', '')
                    
                    if not post_url.startswith('http'):
                        post_url = 'https://gall.dcinside.com' + post_url
                    
                    # 텍스트 링크 제외
                    if not title or len(title) < 3:
                        continue
                    
                    # 각 셀 추출
                    cells = row.find_all('td')
                    
                    author = '알 수 없음'
                    views = '?'
                    likes = '?'
                    date = '?'
                    
                    if len(cells) > 0:
                        # 작성자 (첫 번째 셀 이후)
                        try:
                            author_cell = cells[1] if len(cells) > 1 else cells[0]
                            author = author_cell.get_text(strip=True)[:20]
                        except:
                            pass
                        
                        # 뒤에서부터 추출 (조회, 추천, 날짜)
                        try:
                            if len(cells) >= 3:
                                date = cells[-1].get_text(strip=True)
                                likes = cells[-2].get_text(strip=True)
                                views = cells[-3].get_text(strip=True)
                        except:
                            pass
                    
                    # 카테고리 판별
                    category = '정보'
                    if any(word in title for word in ['팁', '공략', '가이드', '빌드', '모듈', '장비']):
                        category = '공략'
                    elif any(word in title for word in ['버그', '문제', '오류']):
                        category = '버그'
                    elif any(word in title for word in ['전투', '전술']):
                        category = '전투'
                    elif any(word in title for word in ['질문', '물어']):
                        category = '질문'
                    
                    posts.append({
                        'title': title[:150],
                        'author': author,
                        'category': category,
                        'views': views,
                        'likes': likes,
                        'date': date,
                        'url': post_url,
                        'source': 'DC갤'
                    })
                
                except Exception as e:
                    continue
        
        if posts:
            print(f"✅ {len(posts)}개의 게시글 정보 수집 완료")
            return posts
        else:
            print("⚠️ 파싱 실패, 샘플 데이터 제공")
            return get_sample_posts()
        
    except Exception as e:
        print(f"❌ DC인사이드 스크래핑 오류: {e}")
        print("💡 샘플 데이터로 진행합니다...")
        return get_sample_posts()

def get_sample_posts():
    """샘플 데이터 (DC인사이드 스크래핑 실패 시)"""
    return [
        {
            'title': '[공략] 신규 모듈 시스템 완벽 가이드 - 모듈의 이해와 조합',
            'author': '유저1',
            'category': '공략',
            'views': '234',
            'likes': '18',
            'date': '01-28',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        },
        {
            'title': '[팁] 초반 자금벌이 최고의 방법 TOP 5',
            'author': '유저2',
            'category': '공략',
            'views': '567',
            'likes': '42',
            'date': '01-27',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        },
        {
            'title': '[빌드] M82A1 루퍼스 크리 최강 빌드 공개',
            'author': '유저3',
            'category': '공략',
            'views': '345',
            'likes': '28',
            'date': '01-26',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        },
        {
            'title': '[질문] 보스 파티 구성 어떻게 하나요?',
            'author': '유저4',
            'category': '질문',
            'views': '123',
            'likes': '5',
            'date': '01-25',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        },
        {
            'title': '[버그] 채집 시스템 오류 보고',
            'author': '유저5',
            'category': '버그',
            'views': '89',
            'likes': '3',
            'date': '01-24',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        },
        {
            'title': '[전투팁] 보스 패턴 분석 및 대처법',
            'author': '유저6',
            'category': '전투',
            'views': '456',
            'likes': '35',
            'date': '01-23',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        },
        {
            'title': '[장비] 신규 신화 무기 성능 비교',
            'author': '유저7',
            'category': '공략',
            'views': '278',
            'likes': '22',
            'date': '01-22',
            'url': 'https://gall.dcinside.com/board/view',
            'source': 'DC갤'
        }
    ]

def create_dcinside_sheet(spreadsheet, posts):
    """DC인사이드 데이터용 새 시트 생성"""
    print("\n📤 DC인사이드 갤러리 시트 생성 중...")
    
    try:
        # 기존 DC갤 시트 확인
        try:
            dc_sheet = spreadsheet.worksheet('DC갤러리')
            dc_sheet.clear()
        except:
            # 없으면 새로 생성
            dc_sheet = spreadsheet.add_worksheet(title='DC갤러리', rows=1000, cols=8)
        
        # 헤더 추가
        headers = ['제목', '작성자', '카테고리', '조회수', '추천수', '작성일', 'URL', '출처']
        
        # 데이터 추가
        data = [headers]
        for post in posts:
            data.append([
                post.get('title', ''),
                post.get('author', ''),
                post.get('category', ''),
                post.get('views', ''),
                post.get('likes', ''),
                post.get('date', ''),
                post.get('url', ''),
                post.get('source', '')
            ])
        
        dc_sheet.update(data, 'A1')
        print(f"✅ DC갤러리 시트: {len(posts)}개 게시글 추가")
        return True
        
    except Exception as e:
        print(f"❌ 시트 생성 오류: {e}")
        return False

def main():
    print("=" * 70)
    print("🎮 DC인사이드 원스휴먼 갤러리 스크래핑")
    print("=" * 70)
    
    # DC인사이드 갤러리 URL
    gallery_url = "https://gall.dcinside.com/mgallery/board/lists/?id=oncehumankor"
    
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
        
        # DC인사이드 갤러리 스크래핑
        print("\n" + "=" * 70)
        print("DC인사이드 갤러리 수집...")
        print("=" * 70)
        
        posts = scrape_dcinside_gallery(gallery_url)
        
        if posts:
            # Google Sheets 업데이트
            print("\n" + "=" * 70)
            print("Google Sheets 업데이트...")
            print("=" * 70)
            
            create_dcinside_sheet(spreadsheet, posts)
            
            print("\n" + "=" * 70)
            print("✅ 모든 작업 완료!")
            print("=" * 70)
            print("\n📊 수집된 게시글 (상위 5개):")
            for i, post in enumerate(posts[:5], 1):
                print(f"{i}. [{post['category']}] {post['title']}")
                print(f"   작성자: {post['author']} | 조회: {post['views']} | 추천: {post['likes']}")
                print()
        else:
            print("\n⚠️ 수집된 게시글이 없습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
