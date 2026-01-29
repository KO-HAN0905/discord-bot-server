"""
YouTube에서 원스휴먼 관련 콘텐츠 정보 스크래핑
Selenium을 사용하여 동적 페이지 로드 처리
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

def scrape_youtube(url):
    """YouTube에서 동영상 정보 스크래핑"""
    print(f"📍 YouTube 스크래핑 시작: {url}")
    
    # Chrome 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = None
    try:
        # ChromeDriver 설치 및 실행
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("🌐 YouTube 페이지 로드 중...")
        driver.get(url)
        
        # 페이지 로드 대기
        time.sleep(3)
        
        # 동영상 목록 로드 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.ID, "video-title"))
            )
        except:
            print("⚠️ 페이지 로드 시간 초과, 사용 가능한 콘텐츠로 계속 진행...")
        
        # 스크롤하여 더 많은 콘텐츠 로드
        print("📜 페이지 스크롤 중...")
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1)
        
        # 동영상 정보 추출
        videos = []
        
        # 방법 1: ytInitialData 스크립트에서 JSON 추출 (더 효과적)
        try:
            print("🔍 JSON 데이터 추출 시도...")
            script = driver.find_element(By.XPATH, "//script[contains(text(), 'var ytInitialData')]").get_attribute('innerHTML')
            
            # JSON에서 videoId, title 추출
            import json
            match = re.search(r'var ytInitialData = ({.*?});', script)
            if match:
                data = json.loads(match.group(1))
                
                # 검색 결과 추출
                try:
                    results = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                    
                    for item in results:
                        if 'videoRenderer' in item:
                            video = item['videoRenderer']
                            video_id = video.get('videoId', '')
                            title = video.get('title', {}).get('runs', [{}])[0].get('text', '')
                            
                            try:
                                view_count = video.get('viewCountText', {}).get('simpleText', '0')
                                published = video.get('publishedTimeText', {}).get('simpleText', '?')
                            except:
                                view_count = '?'
                                published = '?'
                            
                            if title:
                                videos.append({
                                    'video_id': video_id,
                                    'title': title[:100],
                                    'url': f"https://www.youtube.com/watch?v={video_id}",
                                    'views': view_count,
                                    'published': published,
                                    'type': '동영상'
                                })
                except Exception as e:
                    print(f"⚠️ JSON 파싱 오류: {e}")
        
        except:
            print("⚠️ JSON 데이터 추출 실패, 대안 방법 시도...")
        
        # 방법 2: DOM에서 직접 추출 (JSON 실패 시)
        if not videos:
            print("🔍 DOM에서 동영상 정보 추출 중...")
            
            try:
                video_elements = driver.find_elements(By.XPATH, "//a[@id='video-title']")
                
                for elem in video_elements[:15]:  # 최대 15개
                    title = elem.get_attribute('title')
                    href = elem.get_attribute('href')
                    
                    if title and href:
                        # URL에서 videoId 추출
                        video_id_match = re.search(r'v=([a-zA-Z0-9_-]+)', href)
                        video_id = video_id_match.group(1) if video_id_match else ''
                        
                        videos.append({
                            'video_id': video_id,
                            'title': title[:100],
                            'url': f"https://www.youtube.com{href}",
                            'views': '?',
                            'published': '?',
                            'type': '동영상'
                        })
            
            except Exception as e:
                print(f"⚠️ DOM 추출 오류: {e}")
        
        print(f"✅ {len(videos)}개의 동영상 정보 수집 완료")
        return videos
        
    except Exception as e:
        print(f"❌ YouTube 스크래핑 오류: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    finally:
        if driver:
            driver.quit()

def create_youtube_sheet(spreadsheet, videos):
    """YouTube 데이터용 새 시트 생성"""
    print("\n📤 YouTube 데이터 시트 생성 중...")
    
    try:
        # 기존 YouTube 시트 확인
        try:
            youtube_sheet = spreadsheet.worksheet('YouTube')
            youtube_sheet.clear()
        except:
            # 없으면 새로 생성
            youtube_sheet = spreadsheet.add_worksheet(title='YouTube', rows=1000, cols=6)
        
        # 헤더 추가
        headers = ['제목', 'Video ID', 'URL', '조회수', '발행일', '타입']
        
        # 데이터 추가
        data = [headers]
        for video in videos:
            data.append([
                video.get('title', ''),
                video.get('video_id', ''),
                video.get('url', ''),
                video.get('views', ''),
                video.get('published', ''),
                video.get('type', '')
            ])
        
        youtube_sheet.update(data, 'A1')
        print(f"✅ YouTube 시트: {len(videos)}개 동영상 추가")
        return True
        
    except Exception as e:
        print(f"❌ 시트 생성 오류: {e}")
        return False

def main():
    print("=" * 70)
    print("🎬 YouTube 원스휴먼 데이터 스크래핑")
    print("=" * 70)
    
    # YouTube URL
    youtube_url = "https://www.youtube.com/results?search_query=%ED%99%94%EB%A0%A4%ED%95%9C%EB%8B%A8%EC%95%84%EB%84%A4"
    
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
        
        # YouTube 스크래핑
        print("\n" + "=" * 70)
        print("YouTube 콘텐츠 수집...")
        print("=" * 70)
        
        videos = scrape_youtube(youtube_url)
        
        if videos:
            # Google Sheets 업데이트
            print("\n" + "=" * 70)
            print("Google Sheets 업데이트...")
            print("=" * 70)
            
            create_youtube_sheet(spreadsheet, videos)
            
            print("\n" + "=" * 70)
            print("✅ 모든 작업 완료!")
            print("=" * 70)
            print("\n📊 수집된 데이터:")
            for i, video in enumerate(videos[:5], 1):
                print(f"{i}. {video['title']}")
                print(f"   URL: {video['url']}")
                print()
        else:
            print("\n⚠️ 수집된 동영상이 없습니다.")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
