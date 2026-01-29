# ✅ Replit 배포 체크리스트

## 📋 준비 단계

- [ ] Replit 계정 가입 (https://replit.com)
- [ ] Discord 봇 토큰 준비
- [ ] Google Sheets credentials.json 준비 (있으면)
- [ ] 디스코드 채널 ID 확인

## 🚀 Replit 설정 단계

### 1단계: 프로젝트 생성
- [ ] Replit에서 "Create" → Python 선택
- [ ] 프로젝트 이름: `discord-bot` 입력
- [ ] 프로젝트 생성 완료

### 2단계: 파일 업로드
- [ ] `bot.py` 업로드
- [ ] `config.py` 업로드
- [ ] `requirements.txt` 업로드 (또는 내용 복사)
- [ ] `cogs/` 폴더 (전체) 업로드
- [ ] `utils/` 폴더 (전체) 업로드
- [ ] `data/` 폴더 (전체) 업로드
- [ ] `credentials.json` 업로드 (있으면)

### 3단계: 환경 변수 설정
- [ ] Replit 우측 "Secrets" 🔑 클릭
- [ ] `DISCORD_BOT_TOKEN` 입력
- [ ] `GAME_NEWS_CHANNEL_ID` 입력 (있으면)
- [ ] `DDAY_CHANNEL_ID` 입력 (있으면)
- [ ] `ADMIN_PASSWORD` 입력

### 4단계: .env 파일 생성 (선택사항)
- [ ] "New file" → `.env` 생성
- [ ] 환경 변수 내용 입력

### 5단계: 실행
- [ ] 상단 "Run" 버튼 클릭
- [ ] 터미널에서 "✅ 로그인했습니다!" 메시지 확인

## 🔄 24시간 구동 설정

### 무료 방법 (권장)
- [ ] UptimeRobot 가입 (https://uptimerobot.com)
- [ ] "Add Monitor" → Replit 웹 URL 추가
- [ ] 모니터링 활성화 (15분마다 ping → 절대 종료 안 됨)

### 유료 방법
- [ ] Replit Pro 구독 ($7/월)
- [ ] "Always On" 활성화 (무제한 24시간)

## 🎯 배포 완료 후

- [ ] 디스코드에서 봇이 온라인 상태 확인
- [ ] `!메뉴` 명령어 테스트
- [ ] `!도움말` 명령어 테스트
- [ ] Google Sheets 연동 테스트 (있으면)

## 📝 자주 하는 실수

❌ **하지 말아야 할 것**
- 토큰을 코드에 하드코딩하기
- 파일 구조를 변경하기
- requirements.txt 빠뜨리기

✅ **꼭 해야 할 것**
- Secrets에 토큰 저장
- 폴더 구조 유지
- 모든 의존성 패키지 포함

## 🆘 문제 해결

**봇이 안 켜진다?**
→ Secrets에 `DISCORD_BOT_TOKEN` 있나? 

**ImportError 나온다?**
→ requirements.txt 수정했나? 다시 Run 클릭

**Google Sheets 안 된다?**
→ credentials.json이 루트에 있나?

**계속 종료된다?**
→ UptimeRobot으로 모니터링 설정했나?

---

**모든 항목을 체크했으면 Replit에서 24시간 구동되는 봇이 완성됩니다!** 🎉
