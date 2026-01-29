# 구글 시트 연동 설정 가이드

## 1. 구글 클라우드 프로젝트 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "라이브러리"로 이동
4. 다음 API 활성화:
   - Google Sheets API
   - Google Drive API

## 2. 서비스 계정 생성

1. "API 및 서비스" > "사용자 인증 정보" 선택
2. "사용자 인증 정보 만들기" > "서비스 계정" 선택
3. 서비스 계정 이름 입력 (예: discord-bot-sheets)
4. "만들고 계속하기" 클릭
5. 역할은 선택하지 않고 "계속" 클릭
6. "완료" 클릭

## 3. 키 생성 및 다운로드

1. 생성된 서비스 계정 클릭
2. "키" 탭으로 이동
3. "키 추가" > "새 키 만들기" 선택
4. JSON 형식 선택하고 "만들기" 클릭
5. 다운로드된 JSON 파일을 `credentials.json`으로 이름 변경
6. 이 파일을 `f:\A\credentials.json` 경로에 저장

## 4. 구글 시트 공유

1. 구글 시트 생성 (자동으로 'Discord_Alarms'라는 이름으로 생성됨)
2. 또는 기존 시트 사용 시:
   - `credentials.json` 파일을 열어 `client_email` 확인
   - 해당 이메일 주소와 시트 공유 (편집자 권한)

## 5. credentials.json 파일 구조

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## 6. 봇 재시작

credentials.json 파일을 저장한 후 봇을 재시작하면 자동으로 구글 시트와 연동됩니다.

## 시트 구조

| 이름 | 시간 | 반복유형 | 채널ID | 생성일 | 상태 |
|------|------|----------|--------|--------|------|
| 회의 | 14:30 | 매일 | 123456 | 2026-01-19 15:30:00 | 활성 |

## 주의사항

- `credentials.json` 파일은 민감한 정보이므로 절대 공개 저장소에 업로드하지 마세요
- `.gitignore`에 `credentials.json`이 포함되어 있는지 확인하세요
