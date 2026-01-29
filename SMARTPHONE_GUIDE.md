# 📱 스마트폰(Android)에서 24시간 Discord 봇 구동 가이드

스마트폰으로 Discord 봇을 안정적으로 24시간 운영하는 완벽한 가이드입니다.

---

## 🔧 필수 준비물

- ✅ Android 7.0 이상 스마트폰
- ✅ USB 전원 케이블 (24시간 충전)
- ✅ WiFi 또는 모바일 데이터
- ✅ Termux 앱 (Google Play Store)
- ✅ GitHub 저장소: `https://github.com/KO-HAN0905/discord-bot-server`

---

## 🚀 빠른 시작 (15분)

### Step 1: Termux 설치 (2분)

1. **Google Play Store** 열기
2. **"Termux"** 검색
3. **개발자**: `Fredrik Fornwall` 확인
4. **설치** 클릭

### Step 2: 초기 설정 (3분)

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip git nano
```

### Step 3: 코드 다운로드 (2분)

```bash
cd ~
git clone https://github.com/KO-HAN0905/discord-bot-server.git
cd discord-bot-server
```

### Step 4: 의존성 설치 (5분)

```bash
pip install discord.py requests python-dotenv APScheduler gspread google-auth gtts
```

### Step 5: 환경 설정 (2분)

```bash
nano .env
```

입력:
```
DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
ADMIN_PASSWORD=8458aa
```

저장: `Ctrl + X` → `Y` → `Enter`

### Step 6: 테스트 (1분)

```bash
python3 main.py
```

확인 후 `Ctrl + C`로 종료

### Step 7: 백그라운드 실행

```bash
apt install -y screen
screen -S bot -d -m python3 main.py
screen -ls
```

---

## 🔋 스마트폰 설정

1. **배터리 절약 모드** → 끄기
2. **Termux 배터리 최적화** → 비활성화
3. **WiFi 절전 모드** → 꺼짐
4. **USB 전원에 계속 연결**

---

## 📊 관리 명령어

```bash
# 상태 확인
screen -ls

# 로그 보기
tail -50 bot_run.log

# 봇 중지
pkill -f "python3 main.py"

# 봇 재시작
screen -S bot -d -m python3 main.py
```

---

[자세한 가이드는 SMARTPHONE_QUICK_START.md 참고]
