# 🚀 Replit 배포 가이드 (24시간 운영)

Discord 봇을 **Replit에서 24시간 안정적으로 운영**하는 완벽한 가이드입니다.

---

## ✅ 배포 준비 완료

- ✅ **GitHub 저장소**: `KO-HAN0905/discord-bot-server`
- ✅ **코드 준비**: bot.py, config.py, main.py
- ✅ **자동 업데이트**: updater.py + v1.0.0 Release

---

## 📋 배포 단계

### **Step 1: Replit 프로젝트 생성** (5분)

1. **https://replit.com** 접속
2. **"Create Repl"** → **"Import from GitHub"**
3. **URL**: `https://github.com/KO-HAN0905/discord-bot-server`
4. **"Create Repl"** 클릭

### **Step 2: 환경 변수 설정** (2분)

1. **🔒 Secrets** 클릭
2. **DISCORD_BOT_TOKEN** 추가
3. 저장

### **Step 3: 테스트** (1분)

1. **"Run"** 버튼 클릭
2. `[INFO] 봇 준비 완료!` 확인

### **Step 4: Always-On 활성화** (5분)

1. **Replit Pro** 구독 ($7/월)
2. **"Always on"** 체크
3. 🟢 표시 확인

---

## 🎯 자동 업데이트

GitHub Release를 생성하면 Replit의 봇이 자동으로 감지하여 업데이트됩니다!

```
GitHub Release → 봇 자동 감지 → 자동 재시작 ✅
```

---

## 📞 지원

더 자세한 가이드는 로컬에서 `SMARTPHONE_GUIDE.md` 참고
