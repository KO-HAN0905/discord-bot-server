#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원스휴먼 구글 시트 자동 생성 스크립트
필요한 모든 시트와 샘플 데이터를 자동으로 생성합니다.
"""

import gspread
from google.oauth2.service_account import Credentials
import os

def create_sheets_and_data():
    """모든 필요한 시트와 데이터 생성"""
    
    print("=" * 60)
    print("🎮 원스휴먼 - 구글 시트 자동 생성")
    print("=" * 60)
    
    # Google API 인증
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        print("✅ Google API 인증 성공\n")
    except Exception as e:
        print(f"❌ 인증 실패: {e}")
        return
    
    # Once_Data 스프레드시트 열기
    try:
        spreadsheet = client.open('Once_Data')
        print("✅ 'Once_Data' 스프레드시트 발견\n")
    except Exception as e:
        print(f"❌ 스프레드시트 오픈 실패: {e}")
        return
    
    # 시트별 헤더 및 샘플 데이터
    sheets_config = {
        'Boss': {
            'headers': ['보스이름', '난이도', '출현위치', 'HP', '공격패턴', '드롭아이템', '추천장비', '팁'],
            'sample': ['타이탄', '최상', '방사능 지역', '50000', '원형 충격파', '타이탄 핵심', '신화 방어구', '측면 공격 추천']
        },
        'Items': {
            'headers': ['아이템명', '등급', '카테고리', '능력치', '효과', '입수방법', '판매가격'],
            'sample': ['신화검', '신화', '무기', '공격+50', '치명타율+25%', '월드보스 드롭', '50000']
        },
        'ManualWork': {
            'headers': ['작업명', '난이도', '위치', '시간', '보상', '필요도구', '팁'],
            'sample': ['광물채굴', '초급', '광산', '30초', '광석100', '곡괭이', '체력 관리 필수']
        },
        'GatherLocations': {
            'headers': ['위치명', '자원종류', '개수', '리스폰시간', '지도좌표', '특이사항'],
            'sample': ['신비 숲', '목재', '10', '5분', '(128, 456)', '야수 주의']
        },
        'GameTips': {
            'headers': ['제목', '카테고리', '내용', '난이도', '작성자', '업데이트'],
            'sample': ['초반 자금 벌이', '초급 가이드', '목재를 먼저 모아서 집을 지으면 생산성이 올라갑니다', '초급', 'Admin', '2026-01-29']
        },
        'CommunityEvents': {
            'headers': ['이벤트명', '상태', '진행기간', '보상', '참여방법', '상세설명'],
            'sample': ['신정 축제', '진행중', '2026-01-01~01-31', '보상 박스', '스킬 강화', '매일 참여 가능']
        }
    }
    
    # 각 시트 생성 또는 업데이트
    for sheet_name, config in sheets_config.items():
        try:
            # 기존 시트 확인
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                print(f"⚠️  {sheet_name} 시트가 이미 존재합니다. 스킵합니다.")
                continue
            except gspread.WorksheetNotFound:
                # 새 시트 생성
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=len(config['headers']))
                print(f"✅ {sheet_name} 시트 생성")
            
            # 헤더 추가
            worksheet.append_row(config['headers'])
            print(f"   헤더 추가: {len(config['headers'])}개 칼럼")
            
            # 샘플 데이터 추가
            worksheet.append_row(config['sample'])
            print(f"   샘플 데이터 추가: {config['sample'][0]}")
            
            print()
            
        except Exception as e:
            print(f"❌ {sheet_name} 생성 실패: {e}\n")
    
    print("=" * 60)
    print("✅ 모든 시트 설정 완료!")
    print("=" * 60)
    print("\n📋 다음 단계:")
    print("1. 각 시트에 더 많은 데이터를 추가하세요")
    print("2. 봇을 실행하세요: python bot.py")
    print("3. 다음 명령어를 사용하세요:")
    print("   !보스, !아이템, !수동작, !채집, !팁, !이벤트")
    print("\n💡 구글 시트 가이드: ONCEHUMAN_SHEET_GUIDE.md 참고")

if __name__ == "__main__":
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json 파일이 없습니다.")
        print("   Google Cloud 서비스 계정 설정이 필요합니다.")
        exit(1)
    
    create_sheets_and_data()
