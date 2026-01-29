# 🎉 Discord Bot - 최종 배포 가이드

Discord Bot을 3가지 형태로 배포할 수 있습니다!

---

## 📦 배포 옵션 비교

| 형태 | 파일 | 사용 대상 | 장점 |
|------|------|---------|------|
| **1. exe 파일** | `Discord-Bot.exe` | 개발자/테스터 | 가볍고 빠름 |
| **2. 대시보드** | `Discord-Bot-Dashboard.exe` | 관리자 | GUI로 쉬운 관리 |
| **3. 설치 프로그램** | `Discord-Bot-Setup-1.0.0.exe` | 일반 사용자 | 자동 설치/제거 |

---

## 1️⃣ exe 파일 배포 (즉시 사용)

### 📂 배포 폴더 구조

```
Discord-Bot-Ready/
├── Discord-Bot.exe          # 봇 실행 파일
├── Discord-Bot-Dashboard.exe # 대시보드 (옵션)
├── credentials.json         # Google API 인증
├── .env                     # Discord 봇 토큰
├── version.json             # 버전 정보
├── README.md                # 사용 가이드
├── UPDATE_GUIDE.md          # 업데이트 가이드
└── data/                    # 데이터 폴더
```

### 사용 방법

1. **폴더 전체 복사** → 다른 컴퓨터로 이동
2. **Discord-Bot.exe 더블클릭** → 봇 실행
3. **Discord-Bot-Dashboard.exe 실행** → 대시보드에서 관리 (선택사항)

**장점:**
- ✅ 설치 불필요
- ✅ Python 불필요
- ✅ 빠른 실행
- ✅ 언제든 이동 가능

**단점:**
- ❌ 제어판에서 제거 불가
- ❌ 자동 시작 설정 어려움
- ❌ 바로가기 수동 생성

**배포 대상:** 개발자, 테스터, 임시 사용

---

## 2️⃣ 대시보드 GUI 앱 (관리자용)

### 특징

```
🤖 Discord Bot 관리 대시보드
├── 📊 봇 상태 표시 (실행/중지)
├── ⚙️ 봇 제어 (시작/중지/재시작)
├── 💻 시스템 정보 (CPU, 메모리)
├── 🔄 자동 업데이트 확인
├── 📋 실시간 로그 모니터링
└── 🗑️ 로그 초기화
```

### 실행 방법

```bash
# 직접 실행
Discord-Bot-Dashboard.exe

# 또는 바로가기에서 실행
```

### 화면 구성

```
┌─────────────────────────────────────┐
│ 🤖 Discord Bot 관리 대시보드 v1.0.0 │
├─────────────────────────────────────┤
│                                      │
│ 📊 봇 상태: 🟢 실행 중               │
│ 실행 시간: 01:23:45                 │
│                                      │
│ ⚙️ 제어:                            │
│ [▶️ 시작] [⏹️ 중지] [🔄 재시작]     │
│                                      │
│ 💻 시스템:                          │
│ CPU: ████████░░░░░░░░░░░░░░ 35%    │
│ 메모리: ██████░░░░░░░░░░░░░ 30%     │
│                                      │
│ 🔄 업데이트:                        │
│ [🔍 확인] 최신 상태                 │
│                                      │
│ 📋 로그:                            │
│ [14:30:45] ✅ 봇 시작 완료          │
│ [14:30:46] [OK] Tempest가 로그인   │
│ [14:30:47] 봇 준비됨: Tempest     │
│                                      │
│ [🗑️ 초기화] [❌ 종료]              │
└─────────────────────────────────────┘
```

### 설치 위치

```
F:\A\dist\Discord-Bot-Dashboard\Discord-Bot-Dashboard.exe
```

**장점:**
- ✅ GUI로 직관적 관리
- ✅ 시스템 정보 실시간 모니터링
- ✅ 로그 실시간 확인
- ✅ 업데이트 자동 확인

**단점:**
- ❌ exe 파일이 크다 (120MB)
- ❌ 추가 설치 필요

**배포 대상:** 서버 관리자, 운영팀

---

## 3️⃣ 설치 프로그램 (일반 사용자용) 🌟 추천

### 📋 필수 조건

**Inno Setup 설치** (무료)
- https://jrsoftware.org/isdl.php에서 다운로드
- 설치 후 Inno Setup Compiler 실행

### 🔨 설치 파일 생성 방법

#### 방법 1: GUI (추천)

1. **Inno Setup Compiler 실행**
   ```
   Windows 시작 메뉴 → "Inno Setup Compiler" 검색 및 실행
   ```

2. **Discord-Bot-Setup.iss 파일 열기**
   ```
   File → Open → F:\A\Discord-Bot-Setup.iss 선택
   ```

3. **컴파일**
   ```
   Build → Compile (또는 Ctrl + F9)
   ```

4. **완료!**
   ```
   생성 위치: F:\A\dist\Installer\Discord-Bot-Setup-1.0.0.exe
   ```

#### 방법 2: 명령어

PowerShell에서:

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "F:\A\Discord-Bot-Setup.iss"
```

### 설치 프로그램 배포

```
Discord-Bot-Setup-1.0.0.exe  ← 이 파일을 배포합니다!
```

**사용자가 하는 일:**

1. **Discord-Bot-Setup-1.0.0.exe 다운로드**
2. **더블클릭 실행**
3. **설치 마법사 따라가기**
   - 설치 위치 선택
   - 자동 실행 옵션 선택
4. **설치 완료**
   - 바탕화면에 바로가기 생성
   - 시작 메뉴에 등록
   - 대시보드 자동 실행

**장점:**
- ✅ 전문적인 설치 경험
- ✅ 자동 바로가기 생성
- ✅ 제어판에서 제거 가능
- ✅ Windows 시작 시 자동 실행 가능
- ✅ 일반 사용자에게 최고!

**단점:**
- ❌ 크기가 크다 (250MB)
- ❌ 관리자 권한 필요할 수 있음

**배포 대상:** 일반 사용자, 최종 사용자

---

## 🚀 배포 체크리스트

### exe 파일 배포 전

- [ ] `.bot_running` 파일 삭제
- [ ] `data/` 폴더 비어있는지 확인
- [ ] `credentials.json` 최신인지 확인
- [ ] `.env` 파일에 봇 토큰 있는지 확인
- [ ] `version.json` 버전 확인

### 설치 프로그램 배포 전

**Step 1: 파일 준비**
- [ ] `Discord-Bot.exe` 생성됨
- [ ] `Discord-Bot-Dashboard.exe` 생성됨
- [ ] `credentials.json` 준비됨
- [ ] `.env` 파일 준비됨

**Step 2: 버전 업데이트**
- [ ] `version.json` 버전 번호 수정
- [ ] `Discord-Bot-Setup.iss` 버전 번호 수정
- [ ] `Discord-Bot-Setup.iss` 경로 확인

**Step 3: 설치 파일 생성**
- [ ] Inno Setup 설치됨
- [ ] Discord-Bot-Setup.iss 파일 존재
- [ ] Build → Compile 실행
- [ ] `Discord-Bot-Setup-1.0.0.exe` 생성됨

**Step 4: 테스트**
- [ ] exe 파일 직접 실행 테스트
- [ ] 대시보드 기능 테스트
- [ ] 설치 프로그램으로 설치 테스트
- [ ] 제거 테스트

---

## 📊 파일 크기

| 파일 | 크기 | 설명 |
|------|------|------|
| Discord-Bot.exe | 150MB | 봇 실행 파일 |
| Discord-Bot-Dashboard.exe | 120MB | 대시보드 |
| Discord-Bot-Setup-1.0.0.exe | 250MB | 설치 프로그램 (압축) |

---

## 🔄 업데이트 배포

새 버전 (예: v1.1.0)을 배포하려면:

### exe 배포 (간단)
```
dist/Discord-Bot-Ready/ 폴더 전체를 새 버전으로 교체
```

### 설치 프로그램 배포
```
Step 1: 버전 번호 업데이트 (v1.0.0 → v1.1.0)
Step 2: Discord-Bot-Setup.iss 수정
Step 3: Inno Setup에서 다시 컴파일
Step 4: Discord-Bot-Setup-1.1.0.exe 배포
```

---

## 🎯 추천 배포 전략

### 개발/테스트 단계
→ **exe 파일**로 빠르게 배포

### 서버/운영 환경
→ **대시보드**로 관리

### 최종 사용자 배포
→ **설치 프로그램**으로 전문적 배포

---

## 📞 사용자 지원

### 설치 관련 문제
- [INSTALLER_SETUP.md](INSTALLER_SETUP.md) 참고

### 봇 사용법
- [README.md](dist/Discord-Bot-Ready/README.md) 참고

### 자동 업데이트
- [UPDATE_GUIDE.md](dist/Discord-Bot-Ready/UPDATE_GUIDE.md) 참고

---

**축하합니다! 🎉 이제 Discord Bot을 여러 형태로 배포할 수 있습니다!**

선택한 배포 방식으로 바로 시작하세요!
