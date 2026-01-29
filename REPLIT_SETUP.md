# 🌐 Replit에서 디스코드 봇 24시간 구동 설정 가이드

## ✅ 사전 준비물
- Replit 계정 (https://replit.com)
- Discord 봇 토큰
- Google Sheets API 인증 정보 (credentials.json)
- 채널 ID (뉴스, D-Day)

---

## 📝 **Step 1: Replit 프로젝트 생성**

1. https://replit.com 접속
2. **"Create"** 클릭
3. **"Python"** 선택
4. 프로젝트 이름: `discord-bot` 입력
5. **"Create Repl"** 클릭

---

## 📂 **Step 2: 파일 업로드**

### 폴더 구조
```
discord-bot/
├── bot.py
├── config.py
├── requirements.txt
├── .env (토큰 정보)
├── credentials.json (구글 시트 인증)
├── cogs/
│   ├── __init__.py
│   ├── alarm.py
│   ├── dday.py
│   ├── game_news.py
│   ├── help.py
│   ├── menu.py
│   ├── once_human.py
│   ├── server_stats.py
│   ├── settings.py
│   └── tasks.py
├── utils/
│   └── (필요한 유틸 파일들)
└── data/
    └── (데이터 파일들)
```

### 업로드 방법

1. **Replit 좌측 파일 탐색기 우측 "+"** 클릭
2. **"Upload file"** 또는 **"Upload folder"** 선택
3. f:\A의 다음 폴더/파일 업로드:
   - `bot.py`
   - `config.py`
   - `requirements.txt`
   - `cogs/` (전체 폴더)
   - `utils/` (전체 폴더)
   - `data/` (전체 폴더)

---

## 🔐 **Step 3: 환경 변수 설정**

1. Replit 화면 우측 **"Secrets"** 클릭 (🔑 아이콘)
2. 다음 항목들을 추가:

| 키 | 값 |
|---|---|
| `DISCORD_BOT_TOKEN` | 당신의 Discord 봇 토큰 |
| `GAME_NEWS_CHANNEL_ID` | 뉴스 채널 ID |
| `DDAY_CHANNEL_ID` | D-Day 채널 ID |
| `ADMIN_PASSWORD` | 관리자 비밀번호 (예: 8458aa) |

---

## 📋 **Step 4: .env 파일 생성**

Replit 편집기에서:

1. **"+"** 클릭 → **"New file"** → 파일명: `.env`
2. 다음 내용 입력:
```
DISCORD_BOT_TOKEN=your_token_here
GAME_NEWS_CHANNEL_ID=your_channel_id
DDAY_CHANNEL_ID=your_channel_id
ADMIN_PASSWORD=8458aa
```

---

## 🔑 **Step 5: credentials.json 업로드 (Google Sheets용)**

1. **"Upload file"** 클릭
2. 로컬 f:\A\credentials.json 선택
3. 루트 디렉토리에 업로드

---

## 📦 **Step 6: requirements.txt 업로드 또는 수정**

Replit에서 자동으로 `requirements.txt`를 감지하여 패키지를 설치합니다.

다음 내용이 포함되어 있어야 합니다:
```
discord.py==2.3.2
openpyxl==3.11.0
requests==2.31.0
APScheduler==3.10.4
python-dotenv==1.0.0
gspread==6.1.4
google-auth==2.36.0
```

---

## ▶️ **Step 7: 봇 실행**

1. 상단 **"Run"** 버튼 클릭
2. 터미널에서 봇 로그 확인
3. "✅ 봇이 로그인했습니다!" 메시지 확인

```
✅ Tempest#5888가 로그인했습니다!
봇 준비됨: Tempest (1461693257347239992)
```

---

## 🔄 **Step 8: 24시간 구동 설정**

### Replit Always On (유료)
- **"Always On"** 기능으로 24시간 구동
- 프리 플랜: 월 1시간 무료
- Pro 플랜: 월 $7 (무제한)

### 무료 대안: **UptimeRobot** (권장)
1. https://uptimerobot.com 접속
2. 가입 후 "Add Monitor"
3. Replit 봇의 웹 URL 모니터링
4. 15분마다 ping → 절대 종료 안 됨 (무료)

---

## 🎯 **사용 명령어**

봇이 실행되면 디스코드에서 다음 명령어 사용 가능:

```
!메뉴          - 메인 메뉴 표시
!메메틱        - 원스휴먼 메메틱 정보
!알람          - 알람 설정
!과제          - 과제 관리
!디데이        - D-Day 관리
!뉴스          - 게임 뉴스
!도움말        - 도움말 표시
```

---

## ⚠️ **주의사항**

1. **토큰 보안**: Secrets에 저장하세요 (절대 코드에 하드코딩 금지)
2. **파일 업로드**: 대용량 파일은 나눠서 업로드
3. **데이터 영속성**: Replit은 세션당 24시간만 저장 가능
   - 중요 데이터는 Google Sheets/Database 사용 권장

---

## 🆘 **문제 해결**

### 토큰 오류
- Secrets에 `DISCORD_BOT_TOKEN` 정확히 입력했나?

### 모듈 import 오류
- `requirements.txt` 업로드 후 Run 다시 클릭

### Google Sheets 오류
- `credentials.json` 파일이 루트에 있나?
- 서비스 계정 권한 확인

---

## 📚 **추가 리소스**

- Replit 공식 문서: https://docs.replit.com
- discord.py 문서: https://discordpy.readthedocs.io
- UptimeRobot 설정: https://uptimerobot.com

---

**준비 완료되셨나요? 다음 단계로 진행하세요!** 🚀
