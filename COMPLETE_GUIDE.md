# 🎯 Discord Bot + Mobile App - 완전 가이드

모바일 앱에서 24시간 Discord 봇을 제어하세요!

## 📦 프로젝트 구조

```
f:\C\
├── DiscordBotMobile/          ← React Native 모바일 앱
│   ├── src/
│   │   ├── screens/           ← 화면 컴포넌트
│   │   ├── services/          ← API 통신
│   │   └── types/             ← TypeScript 타입
│   └── App.tsx
│
└── DiscordBotServer/          ← 24시간 서버 (Railway 호스팅)
    ├── python_bot/            ← Discord 봇 (Python + Flask)
    │   ├── main.py            ← 진입점
    │   ├── app.py             ← Flask API 서버
    │   ├── cogs/              ← 봇 기능 모듈
    │   └── requirements.txt
    ├── node_server/           ← Node.js API (선택)
    ├── Dockerfile             ← Docker 이미지
    ├── railway.toml           ← Railway 설정
    ├── README.md              ← 프로젝트 설명
    ├── RAILWAY_DEPLOYMENT.md  ← 배포 가이드 ✅
    └── LOCAL_TESTING.md       ← 로컬 테스트 가이드
```

## 🚀 빠른 시작 (5단계)

### 1️⃣ 로컬 테스트 (선택사항)

```bash
cd f:\C\DiscordBotServer\python_bot
pip install -r requirements.txt
copy .env.example .env
# .env에서 DISCORD_BOT_TOKEN 설정
python main.py
```

### 2️⃣ Railway 계정 생성

- https://railway.app 방문
- GitHub로 가입

### 3️⃣ GitHub 저장소 생성

```bash
cd f:\C\DiscordBotServer
git init
git add .
git commit -m "Discord Bot Server"
git remote add origin https://github.com/your-username/discord-bot-server.git
git push -u origin main
```

### 4️⃣ Railway에 배포

Railway 대시보드:
1. "+ New Project"
2. "Deploy from GitHub repo" 선택
3. 저장소 연결
4. Variables 탭에서 `DISCORD_BOT_TOKEN` 설정

### 5️⃣ 모바일 앱 업데이트

```bash
# DiscordBotMobile/src/services/api.ts
const API_BASE_URL = 'https://your-railway-app-name.up.railway.app/api';
```

## 📱 모바일 앱 사용

```bash
cd f:\C\DiscordBotMobile
npm run web      # 웹 브라우저에서 테스트
npm run android  # Android 에뮬레이터
```

**제어 기능:**
- ✅ 봇 상태 확인
- ✅ 봇 시작/중지
- ✅ 실시간 로그
- ✅ 명령어 실행

## 📚 상세 가이드

| 문서 | 설명 |
|------|------|
| **LOCAL_TESTING.md** | 로컬에서 테스트하는 방법 |
| **RAILWAY_DEPLOYMENT.md** | Railway에 배포하는 단계별 가이드 |
| **README.md** | 프로젝트 개요 및 API 문서 |

## 🔧 주요 기능

### Python 봇 (Flask API)

```python
GET  /api/bot/status   # 봇 상태
POST /api/bot/start    # 봇 시작
POST /api/bot/stop     # 봇 중지
GET  /api/logs         # 로그 조회
POST /api/command      # 명령어 실행
GET  /health           # 헬스 체크
```

### 모바일 앱 (React Native)

```typescript
HomeScreen   → 봇 제어 (시작/중지)
LogsScreen   → 실시간 로그 확인
SettingsScreen → API 설정
```

## 💡 사용 시나리오

### 시나리오 1: 로컬 테스트

```
로컬 PC에서 봇 서버 실행
→ 모바일 앱 연결 (로컬 IP)
→ 기능 테스트
→ 문제 해결
```

### 시나리오 2: 클라우드 배포

```
코드 → GitHub 푸시
→ Railway 자동 배포
→ 24시간 실행
→ 모바일 앱 연결 (Railway URL)
```

### 시나리오 3: 프로덕션

```
Railway에서 24시간 운영
→ 휴대폰에서 언제 어디서나 제어
→ 실시간 모니터링
→ 알림 수신
```

## 💰 비용 분석

| 항목 | 월 비용 |
|------|--------|
| Railway 봇 호스팅 | $3~5 |
| 데이터베이스 (선택) | $0~10 |
| **총액** | **$3~5** |

Railway 제공:
- 매월 $5 무료 크레딧
- 초과 시 자동 알림

## ⚠️ 중요 주의사항

⚠️ **보안**
- Discord 토큰은 절대 공개하지 마세요
- Railway Secrets 탭에서만 관리
- `.env` 파일은 `.gitignore`에 추가

⚠️ **운영**
- 월간 사용량 모니터링
- 봇 로그 정기 확인
- API 엔드포인트 보안

## 🆘 문제 해결

### 문제: 봇이 연결되지 않음
```
→ Discord 토큰 확인
→ Railway 로그 확인
→ 네트워크 연결 확인
```

### 문제: 모바일 앱이 API에 연결 안 됨
```
→ Railway URL 확인
→ 방화벽 설정 확인
→ CORS 설정 확인
```

### 문제: 월간 크레딧 초과
```
→ Railway 대시보드에서 사용량 확인
→ 자동 중지 설정 검토
→ 리소스 최적화
```

## 📞 지원 링크

- Railway 문서: https://docs.railway.app
- Discord.py: https://discordpy.readthedocs.io
- Flask: https://flask.palletsprojects.com
- React Native: https://reactnative.dev

## ✅ 완료 체크리스트

```
[ ] 로컬 테스트 완료
[ ] GitHub 저장소 생성
[ ] Railway 배포 완료
[ ] 환경 변수 설정
[ ] 모바일 앱 API URL 업데이트
[ ] API 엔드포인트 테스트
[ ] 모바일 앱에서 봇 제어 확인
[ ] 24시간 연속 실행 테스트
```

---

**🎉 축하합니다!**

이제 언제 어디서나 휴대폰으로 Discord 봇을 24시간 운영할 수 있습니다!

질문이 있으시면 언제든지 물어보세요.
