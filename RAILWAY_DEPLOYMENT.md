# 🚀 Railway에 Discord 봇 배포 가이드

## ⚙️ 사전 준비

- Discord 봇 토큰 준비
- Railway 계정 (https://railway.app)
- Git 설치

## 📋 단계별 배포

### 1️⃣ Railway 가입 및 프로젝트 생성

1. https://railway.app 접속
2. GitHub로 로그인
3. 새 프로젝트 생성

### 2️⃣ GitHub 저장소 준비

```bash
cd f:\C\DiscordBotServer

# Git 초기화
git init
git add .
git commit -m "Initial commit: Discord bot server"

# GitHub에 푸시 (선택사항)
git remote add origin https://github.com/your-username/discord-bot-server.git
git branch -M main
git push -u origin main
```

### 3️⃣ Railway에서 배포

#### 방법 1: GitHub 연동 (추천)

1. Railway 대시보드 → "+ New Project"
2. "Deploy from GitHub repo" 선택
3. 저장소 선택
4. 자동 배포 설정

#### 방법 2: 로컬에서 배포

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 생성 및 배포
railway init
railway up
```

### 4️⃣ 환경 변수 설정

Railway 대시보드의 **Variables** 탭에서:

```
DISCORD_BOT_TOKEN = your_discord_bot_token_here
FLASK_HOST = 0.0.0.0
FLASK_PORT = 5000
```

### 5️⃣ 배포 확인

```bash
railway logs
```

출력 예시:
```
✓ 환경 변수 로드 완료
🚀 API 서버 시작: 0.0.0.0:5000
봇이 Discord에 연결되었습니다!
```

## 📱 모바일 앱 설정

`DiscordBotMobile` 프로젝트의 `.env` 또는 `api.ts` 수정:

```typescript
// src/services/api.ts
const API_BASE_URL = 'https://your-railway-app-name.up.railway.app/api';
```

Railway 배포 후 URL을 확인하고 위에 입력하세요.

## 🔍 API 테스트

### 봇 상태 조회
```bash
curl https://your-railway-app.up.railway.app/api/bot/status
```

응답:
```json
{
  "status": "online",
  "user": "YourBotName#0000",
  "latency": 45
}
```

### 봇 시작
```bash
curl -X POST https://your-railway-app.up.railway.app/api/bot/start
```

### 헬스 체크
```bash
curl https://your-railway-app.up.railway.app/health
```

## 💰 Railway 요금

- **무료 크레딧**: 월 $5 제공
- **24시간 봇 운영**: 약 $3~5/월
- 초과 시 추가 비용 (자동 중지 가능)

## ⚠️ 주의사항

1. **토큰 보안**: 절대 공개 저장소에 토큰을 올리지 마세요
2. **환경 변수**: Railway의 Secrets 탭에서만 설정
3. **로그 모니터링**: 정기적으로 로그 확인

## 🐛 트러블슈팅

### 봇이 연결되지 않음
- 토큰이 올바른지 확인
- Railway 로그에서 오류 확인

### API 응답 없음
- 방화벽 설정 확인
- Railway 상태 페이지 확인

### 월간 크레딧 초과
- Railway 대시보드에서 사용량 확인
- 자동 중지 설정 검토

## 📞 고객 지원

- Railway 문서: https://docs.railway.app
- Discord.py: https://discordpy.readthedocs.io
- 이슈 발생 시 로그 캡처 후 공유

## ✅ 배포 완료 체크리스트

- [ ] GitHub 저장소 생성
- [ ] Railway 계정 생성
- [ ] 환경 변수 설정
- [ ] 배포 성공 확인
- [ ] 모바일 앱 API URL 업데이트
- [ ] API 엔드포인트 테스트
- [ ] 봇이 Discord에서 온라인 상태
- [ ] 모바일 앱에서 봇 제어 확인

---

축하합니다! 🎉 이제 휴대폰에서 24시간 봇을 제어할 수 있습니다!
