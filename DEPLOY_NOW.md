# 🚀 Railway 배포 완료 가이드

## ✅ 완료된 작업

1. ✅ 통합 서버 파일 생성 (`railway_server.py`)
   - Discord 봇 + Flask API를 하나의 서버로 통합
   - 백그라운드에서 봇 실행
   - API 엔드포인트 제공

2. ✅ Railway 배포 설정 파일
   - `Procfile`: 서버 시작 명령
   - `railway.json`: Railway 설정
   - `requirements.txt`: Python 의존성

3. ✅ 환경 변수 준비
   - `.env.example` 템플릿 제공

---

## 🌐 Railway 배포 단계

### **1단계: Railway 계정 생성**

1. https://railway.app 방문
2. "Login with GitHub" 클릭
3. GitHub 계정으로 로그인

---

### **2단계: 새 프로젝트 생성**

Railway 대시보드에서:

1. **"+ New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. GitHub 저장소 연결 (아래 3단계 먼저 진행)

---

### **3단계: GitHub 저장소 생성 및 푸시**

PowerShell에서 실행:

```powershell
# DiscordBotServer 폴더로 이동
cd f:\C\DiscordBotServer

# Git 초기화
git init
git add .
git commit -m "Initial commit: Discord Bot Server for Railway"

# GitHub에 새 저장소 생성 후 (https://github.com/new)
# 저장소 URL로 변경하세요
git remote add origin https://github.com/YOUR_USERNAME/discord-bot-server.git
git branch -M main
git push -u origin main
```

---

### **4단계: Railway에서 저장소 연결**

1. Railway 대시보드 → "+ New Project"
2. "Deploy from GitHub repo" 선택
3. 방금 만든 저장소 선택
4. 자동 배포 시작!

---

### **5단계: 환경 변수 설정** ⚠️ 중요!

Railway 프로젝트 → **Variables** 탭:

```
DISCORD_BOT_TOKEN = your_actual_discord_bot_token_here
PORT = 5000
HOST = 0.0.0.0
```

**Discord 봇 토큰 가져오기:**
1. https://discord.com/developers/applications
2. 봇 애플리케이션 선택
3. Bot → Token → "Reset Token" 또는 "Copy"

---

### **6단계: 배포 확인**

Railway 대시보드:
- **Deployments** 탭에서 배포 상태 확인
- **Logs** 탭에서 실행 로그 확인
- 성공 메시지: `✅ Discord 봇 연결됨`

---

### **7단계: 배포 URL 확인**

Railway 프로젝트 → **Settings** → **Domains**:
- **Generate Domain** 클릭
- 생성된 URL 복사 (예: `https://your-app-name.up.railway.app`)

---

### **8단계: 모바일 앱 설정**

`f:\C\DiscordBotMobile\src\services\api.ts` 수정:

```typescript
const API_BASE_URL = 'https://your-app-name.up.railway.app/api';
```

---

## 🧪 배포 테스트

### **API 테스트:**

```powershell
# 헬스 체크
curl https://your-app-name.up.railway.app/health

# 봇 상태 확인
curl https://your-app-name.up.railway.app/api/bot/status

# 서버 목록 확인
curl https://your-app-name.up.railway.app/api/bot/guilds
```

---

## 📱 모바일 앱 연결

1. 모바일 앱 재시작
2. "Home" 탭 → 봇 상태 확인
3. Discord 서버 정보 확인 가능!

---

## 💰 비용

- **무료 크레딧**: $5/월
- **예상 비용**: $3~5/월
- **자동 일시 중지**: 미사용 시 자동 중지 가능

---

## 🔧 문제 해결

### **봇이 연결되지 않음:**
```
→ Railway Variables에서 DISCORD_BOT_TOKEN 확인
→ Discord Developer Portal에서 봇 토큰 재생성
→ Railway에서 재배포
```

### **API 응답 없음:**
```
→ Railway Logs 탭에서 에러 확인
→ Domains 탭에서 URL 확인
→ 방화벽 설정 확인
```

### **배포 실패:**
```
→ requirements.txt 의존성 확인
→ Logs에서 에러 메시지 확인
→ GitHub 저장소에 모든 파일 푸시 확인
```

---

## ✅ 배포 완료 체크리스트

- [ ] Railway 계정 생성
- [ ] GitHub 저장소 생성 및 푸시
- [ ] Railway에서 저장소 연결
- [ ] 환경 변수 설정 (DISCORD_BOT_TOKEN)
- [ ] 배포 성공 확인 (Logs 확인)
- [ ] 도메인 생성
- [ ] 모바일 앱 API URL 업데이트
- [ ] 모바일 앱에서 봇 연결 테스트

---

## 🎉 완료!

이제 Discord 봇이 Railway에서 24시간 실행됩니다!
휴대폰 앱으로 언제 어디서나 봇을 제어하세요! 📱✨

**질문이나 문제가 있으면 Railway Logs를 확인하세요!**
