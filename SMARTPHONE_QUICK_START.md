# 📱 스마트폰 봇 구동 - 빠른 시작 가이드

**소요 시간: 15분**

---

## 🚀 1단계: Termux 설치 (2분)

1. **Google Play Store** 열기
2. **"Termux"** 검색
3. **개발자**: `Fredrik Fornwall` 확인 후 **설치**
4. **앱 열기**

---

## 💻 2단계: Termux 초기화 (5분)

```bash
apt update && apt upgrade -y
```

```bash
apt install -y python3 python3-pip git nano
```

```bash
python3 --version
```

---

## 📥 3단계: 코드 다운로드 (2분)

```bash
cd ~
git clone https://github.com/KO-HAN0905/discord-bot-server.git
cd discord-bot-server
```

---

## 📦 4단계: 의존성 설치 (5분)

```bash
pip install discord.py requests python-dotenv APScheduler gspread google-auth gtts
```

---

## 🔑 5단계: 환경 설정 (2분)

```bash
nano .env
```

다음 입력:
```
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
ADMIN_PASSWORD=8458aa
```

**저장**: `Ctrl + X` → `Y` → `Enter`

---

## ✅ 6단계: 테스트 (1분)

```bash
python3 main.py
```

**확인할 것:**
```
✅ 환경 변수 로드 완료
[INFO] 봇 준비 완료!
```

**중지**: `Ctrl + C`

---

## 🔄 7단계: 백그라운드 실행

```bash
apt install -y screen
screen -S bot -d -m python3 main.py
screen -ls
```

---

## 📊 운영 명령어

```bash
# 상태 확인
screen -ls

# 봇 중지
pkill -f "python3 main.py"

# 봇 재시작
screen -S bot -d -m python3 main.py
```

---

## 🎯 완료!

✅ 스마트폰이 이제 Discord 봇 서버입니다!
