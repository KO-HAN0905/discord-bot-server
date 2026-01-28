# 실행 서버 테스트 가이드

## 로컬 개발 모드

### Python 봇 실행

```bash
# 1. 프로젝트 경로로 이동
cd f:\C\DiscordBotServer\python_bot

# 2. 가상환경 생성 (선택사항)
python -m venv venv
venv\Scripts\activate  # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. .env 파일 생성
copy .env.example .env

# 5. 토큰 설정
# .env 파일에서 DISCORD_BOT_TOKEN을 설정하세요

# 6. 서버 실행
python main.py
```

### 성공 메시지

```
✓ 환경 변수 로드 완료
🚀 API 서버 시작: 0.0.0.0:5000
```

## API 엔드포인트 테스트

### PowerShell에서 테스트

```powershell
# 1. 봇 상태 확인
Invoke-WebRequest -Uri "http://localhost:5000/api/bot/status" -Method Get

# 2. 헬스 체크
Invoke-WebRequest -Uri "http://localhost:5000/health" -Method Get

# 3. 봇 시작
Invoke-WebRequest -Uri "http://localhost:5000/api/bot/start" -Method Post

# 4. 봇 중지
Invoke-WebRequest -Uri "http://localhost:5000/api/bot/stop" -Method Post
```

### cURL 명령어

```bash
# 상태 확인
curl http://localhost:5000/api/bot/status

# 헬스 체크
curl http://localhost:5000/health
```

## 모바일 앱 테스트

### API URL 임시 설정

`f:\C\DiscordBotMobile\src\services\api.ts`:

```typescript
const API_BASE_URL = 'http://192.168.x.x:5000/api';
// 192.168.x.x는 로컬 PC의 IP 주소
```

### 로컬 PC IP 확인

```powershell
ipconfig
```

IPv4 주소를 확인하세요. 예: 192.168.219.100

### 모바일 앱 실행

```bash
cd f:\C\DiscordBotMobile
npm run web  # 웹 테스트
# 또는
npm run android  # Android 에뮬레이터
```

## 다음 단계

✅ 로컬 테스트 완료 후:

1. GitHub 저장소 생성
2. Railway 배포 (RAILWAY_DEPLOYMENT.md 참고)
3. 모바일 앱 API URL 업데이트
4. 프로덕션 테스트
