# 📦 Inno Setup - Discord Bot 설치 프로그램 만들기

Discord Bot을 위한 **Windows 설치 프로그램**을 만들기 위해 Inno Setup을 사용합니다.

## 📥 Step 1: Inno Setup 다운로드 및 설치

1. **Inno Setup 다운로드**
   - https://jrsoftware.org/isdl.php 방문
   - "Inno Setup 6.x" 다운로드 (최신 버전)
   - 설치 파일 실행 및 설치

2. **설치 완료 확인**
   ```
   Inno Setup이 설치되면 "Inno Setup Compiler"가 생성됩니다
   ```

---

## 🔨 Step 2: 설치 스크립트로 설치 파일 만들기

### 방법 1: GUI에서 생성 (추천)

1. **Inno Setup Compiler 실행**
   - Windows 시작 메뉴에서 "Inno Setup Compiler" 검색
   - 클릭하여 실행

2. **Discord-Bot-Setup.iss 파일 열기**
   - 메뉴: File → Open
   - `F:\A\Discord-Bot-Setup.iss` 파일 선택

3. **설치 파일 생성**
   - 메뉴: Build → Compile
   - 또는 단축키: `Ctrl + F9`
   - 잠시 기다리면 설치 파일이 생성됨

4. **생성 완료**
   ```
   F:\A\dist\Installer\Discord-Bot-Setup-1.0.0.exe
   ```
   이 파일이 설치 프로그램입니다!

### 방법 2: 명령어에서 생성

PowerShell에서:

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "F:\A\Discord-Bot-Setup.iss"
```

---

## 🚀 설치 프로그램 배포

생성된 `Discord-Bot-Setup-1.0.0.exe` 파일은:

- ✅ 바로 배포 가능
- ✅ 사용자가 더블클릭하면 자동 설치
- ✅ 제어판에서 제거 가능
- ✅ 바탕화면 바로가기 자동 생성

---

## 📋 설치 프로그램 기능

### 설치 중
1. 설치 위치 선택 (기본: `C:\Users\{username}\AppData\Local\DiscordBot`)
2. 구성 요소 선택 (앞으로 추가 가능)
3. **Windows 시작 시 자동 실행** 옵션 선택 가능

### 설치 후
- 바탕화면에 바로가기 생성
- 시작 메뉴에 프로그램 추가
- Discord Bot 대시보드 자동 실행 (선택사항)

### 제거
- 제어판 → 프로그램 제거에서 "Discord Bot" 선택
- 자동으로 모든 파일 및 바로가기 제거

---

## 🔄 업데이트 버전 만들기

새 버전으로 설치 프로그램을 만들려면:

### Step 1: 파일 업데이트
```bash
# 봇 재빌드
cd F:\A
F:/A/.venv/Scripts/pyinstaller.exe bot.spec
F:/A/.venv/Scripts/pyinstaller.exe dashboard.spec
```

### Step 2: 버전 정보 업데이트
`version.json` 수정:
```json
{
  "version": "1.1.0",
  "last_updated": "2026-01-29T14:00:00"
}
```

### Step 3: 설치 스크립트 수정
`Discord-Bot-Setup.iss` 수정:
```ini
AppVersion=1.1.0
OutputBaseFilename=Discord-Bot-Setup-1.1.0
```

### Step 4: 새 설치 파일 생성
```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "F:\A\Discord-Bot-Setup.iss"
```

---

## 🎯 설치 구조

사용자가 설치하면 다음과 같이 배치됩니다:

```
C:\Users\{username}\AppData\Local\DiscordBot\
├── Discord-Bot.exe                    # 봇 실행 파일
├── Discord-Bot-Dashboard.exe          # 대시보드 (관리자용)
├── credentials.json                   # Google API 인증
├── .env                               # Discord 봇 토큰
├── version.json                       # 버전 정보
├── README.md                          # 사용 가이드
├── UPDATE_GUIDE.md                    # 업데이트 가이드
├── data/                              # 봇 데이터
│   ├── alarms.json
│   ├── settings.json
│   ├── tasks.json
│   └── tts_settings.json
└── backups/                           # 자동 백업
```

---

## 🆘 문제 해결

### Inno Setup이 설치되지 않음
- https://jrsoftware.org/isdl.php에서 최신 버전 다운로드
- 관리자 모드로 설치

### .iss 파일을 열 수 없음
- Inno Setup Compiler를 먼저 실행
- File → Open에서 수동 선택

### 설치 파일이 생성되지 않음
- 폴더 경로 확인 (특히 `[Files]` 섹션)
- 경로에 한글이 없는지 확인
- ISCC.exe 명령어 다시 실행

### "빌드 실패" 메시지
- 필요한 exe 파일이 모두 생성되었는지 확인
  - `F:\A\dist\Discord-Bot\Discord-Bot.exe`
  - `F:\A\dist\Discord-Bot-Dashboard\Discord-Bot-Dashboard.exe`
- 파일이 없으면 PyInstaller로 먼저 빌드

---

## 📊 파일 크기 예상

| 파일 | 크기 |
|------|------|
| Discord-Bot.exe | ~150 MB |
| Discord-Bot-Dashboard.exe | ~120 MB |
| 설치 프로그램 (압축) | ~250 MB |
| 설치 후 전체 크기 | ~600 MB |

---

## 🔐 보안 주의사항

⚠️ 설치 프로그램 배포 전 **반드시 확인하세요:**

1. **.env 파일 검토**
   - 봇 토큰이 포함되어 있음
   - 공개 배포 시 제거해야 함

2. **credentials.json 검토**
   - Google API 인증정보 포함
   - 공개 배포 시 사용자가 직접 설정하게 해야 함

3. **암호화 (선택사항)**
   - Inno Setup에서 암호화 옵션 추가 가능
   - Settings → Encryption

---

## ✨ 추가 기능 (선택사항)

### 1. 시작 시 조건부 실행
```ini
[Run]
Filename: "{app}\Discord-Bot-Dashboard.exe"; Flags: nowait postinstall skipifsilent; Check: IsComponentSelected('Dashboard')
```

### 2. 레지스트리 항목 추가
```ini
[Registry]
Root: HKCU; Subkey: "Software\DiscordBot"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: createvalueifdoesntexist
```

### 3. 파일 연결 설정
```ini
[Registry]
Root: HKCU; Subkey: "Software\Classes\.json"; ValueType: string; ValueName: ""; ValueData: "DiscordBotConfig"; Flags: createvalueifdoesntexist
```

---

**Next Step:** Inno Setup을 설치한 후 Discord-Bot-Setup.iss를 열고 "Build → Compile"을 클릭하세요!
