#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
원스휴먼 확장 기능 테스트 스크립트
구글 시트 데이터가 제대로 로드되는지 확인합니다.
"""

import os
import sys
import gspread
from google.oauth2.service_account import Credentials

def test_sheet_connection():
    """구글 시트 연결 테스트"""
    print("=" * 50)
    print("🔍 구글 시트 연결 테스트 시작")
    print("=" * 50)
    
    try:
        # credentials.json 파일 확인
        if not os.path.exists('credentials.json'):
            print("❌ credentials.json 파일이 없습니다.")
            print("   Google Cloud 서비스 계정을 설정하세요.")
            return False
        
        print("✅ credentials.json 파일 발견")
        
        # 구글 시트 연결
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        
        print("✅ Google API 인증 성공")
        
        # Once_Data 스프레드시트 확인
        try:
            spreadsheet = client.open('Once_Data')
            print(f"✅ 'Once_Data' 스프레드시트 발견")
        except gspread.SpreadsheetNotFound:
            print("❌ 'Once_Data' 스프레드시트를 찾을 수 없습니다.")
            print("   https://docs.google.com/spreadsheets에서 생성하세요.")
            return False
        
        # 각 시트 확인
        required_sheets = ['Boss', 'Items', 'ManualWork', 'GatherLocations', 'GameTips', 'CommunityEvents']
        
        print("\n📋 필수 시트 확인:")
        for sheet_name in required_sheets:
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                records = worksheet.get_all_records()
                print(f"  ✅ {sheet_name}: {len(records)}개 항목")
            except gspread.WorksheetNotFound:
                print(f"  ❌ {sheet_name}: 시트 없음")
                return False
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 통과!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

def display_data_summary():
    """데이터 요약 표시"""
    print("\n" + "=" * 50)
    print("📊 데이터 요약")
    print("=" * 50)
    
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open('Once_Data')
        
        print("\n각 시트의 데이터 샘플:\n")
        
        sheet_info = {
            'Boss': '월드 보스',
            'Items': '아이템/장비',
            'ManualWork': '수동작',
            'GatherLocations': '자동채집 위치',
            'GameTips': '게임 팁',
            'CommunityEvents': '커뮤니티 이벤트'
        }
        
        for sheet_name, description in sheet_info.items():
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
                records = worksheet.get_all_records()
                
                print(f"🔹 {sheet_name} ({description})")
                print(f"   항목 수: {len(records)}")
                
                if records:
                    first_record = records[0]
                    # 첫 번째 항목의 첫 2개 필드만 표시
                    keys = list(first_record.keys())[:2]
                    for key in keys:
                        print(f"   - {key}: {first_record.get(key, 'N/A')}")
                
                print()
            except Exception as e:
                print(f"⚠️ {sheet_name} 읽기 실패: {e}\n")
    
    except Exception as e:
        print(f"❌ 데이터 요약 실패: {e}")

if __name__ == "__main__":
    print("\n🎮 원스휴먼 확장 기능 - 구글 시트 테스트\n")
    
    # 테스트 실행
    success = test_sheet_connection()
    
    if success:
        display_data_summary()
        print("\n✅ 모든 준비가 완료되었습니다!")
        print("   봇을 실행하면 다음 명령어를 사용할 수 있습니다:")
        print("   !보스, !아이템, !수동작, !채집, !팁, !이벤트")
    else:
        print("\n⚠️ 구글 시트 설정을 먼저 완료하세요!")
        print("   ONCEHUMAN_SHEET_GUIDE.md 파일을 참고하세요.")
