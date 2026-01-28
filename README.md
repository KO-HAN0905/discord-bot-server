# Discord Bot Server - Railway 배포 버전

모바일 앱과 연동되는 24시간 Discord 봇 서버

## 📁 폴더 구조

```
DiscordBotServer/
├── python_bot/          ← Discord 봇 (Python + Flask)
│   ├── main.py         ← 진입점
│   ├── app.py          ← Flask API 서버
│   ├── cogs/           ← 봇 기능 모듈
│   ├── data/           ← JSON/Excel 데이터
│   ├── utils/          ← 유틸리티
│   └── requirements.txt ← 파이썬 의존성
├── node_server/         ← Node.js API (선택사항)
├── Dockerfile          ← 도커 이미지
├── railway.toml        ← Railway 설정
└── README.md
```

## 🚀 로컬 실행

### Python 봇 설정

```bash
cd python_bot
pip install -r requirements.txt
cp .env.example .env
# .env에서 DISCORD_BOT_TOKEN 설정
python main.py
```

### API 엔드포인트

- `GET /api/bot/status` - 봇 상태 조회
- `POST /api/bot/start` - 봇 시작
- `POST /api/bot/stop` - 봇 중지
- `GET /api/logs` - 로그 조회
- `POST /api/command` - 명령어 실행
- `GET /health` - 헬스 체크

## 🛤️ Railway 배포

### 1단계: Railway 가입
- https://railway.app 에서 가입

### 2단계: 프로젝트 생성
```bash
npm install -g @railway/cli
railway login
railway init
```

### 3단계: 환경 변수 설정
Railway 대시보드에서:
- `DISCORD_BOT_TOKEN` = 봇 토큰

### 4단계: 배포
```bash
railway up
```

## 🔧 모바일 앱 연동

DiscordBotMobile 앱의 `api.ts` 수정:

```typescript
const API_BASE_URL = 'https://your-railway-app.up.railway.app/api';
```

## 📱 모바일 앱에서 제어

- 봇 상태 확인
- 봇 시작/중지
- 로그 조회
- 명령어 실행

## 💡 주의사항

- Railway는 월별 크레딧 기반 (무료 크레딧 제공)
- 봇이 연속 24시간 실행됨
- 로그는 Railway 대시보드에서 확인 가능

## 📚 참고

- [Railway 공식문서](https://docs.railway.app)
- [Discord.py 문서](https://discordpy.readthedocs.io)
- [Flask 문서](https://flask.palletsprojects.com)
