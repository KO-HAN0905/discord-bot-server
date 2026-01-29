; Discord Bot 설치 프로그램 - Inno Setup Script
; 이 파일을 Inno Setup에서 열어서 설치 파일을 생성합니다.

[Setup]
AppName=Discord Bot
AppVersion=1.0.0
AppPublisher=Bot Developer
AppPublisherURL=https://github.com/user/discord-bot
AppSupportURL=https://github.com/user/discord-bot/issues
DefaultDirName={localappdata}\DiscordBot
DefaultGroupName=Discord Bot
OutputDir=F:\A\dist\Installer
OutputBaseFilename=Discord-Bot-Setup-1.0.0
Compression=lz4
SolidCompression=yes
PrivilegesRequired=lowest
SetupIconFile=
WizardStyle=modern
WizardSizePercent=100
ShowLanguageDialog=no
LanguageDetectionMethod=locale
UninstallDisplayIcon={app}\Discord-Bot-Dashboard.exe
SetupLogging=yes
CreateUninstallRegKey=yes

; 언어 설정
[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; 파일 설정
[Files]
; 메인 파일들
Source: "F:\A\dist\Discord-Bot\Discord-Bot.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\A\dist\Discord-Bot-Dashboard\Discord-Bot-Dashboard.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\A\credentials.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\A\.env"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\A\version.json"; DestDir: "{app}"; Flags: ignoreversion

; README 파일
Source: "F:\A\dist\Discord-Bot-Ready\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "F:\A\dist\Discord-Bot-Ready\UPDATE_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

; 데이터 폴더
Source: "F:\A\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\data"
Name: "{app}\backups"

; 프로그램 그룹 및 바로가기
[Icons]
Name: "{group}\Discord Bot 대시보드"; Filename: "{app}\Discord-Bot-Dashboard.exe"; IconIndex: 0; Comment: "봇 관리 대시보드를 엽니다"
Name: "{group}\Discord Bot 실행"; Filename: "{app}\Discord-Bot.exe"; IconIndex: 0; Comment: "봇을 직접 실행합니다"
Name: "{group}\폴더 열기"; Filename: "{app}"; Comment: "설치 폴더를 엽니다"
Name: "{group}\{cm:UninstallProgram,Discord Bot}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Discord Bot 대시보드"; Filename: "{app}\Discord-Bot-Dashboard.exe"; IconIndex: 0; Comment: "봇 관리 대시보드"
Name: "{commonstartup}\Discord Bot"; Filename: "{app}\Discord-Bot-Dashboard.exe"; Parameters: "--auto-start"; Comment: "Windows 시작 시 자동 실행"

; 설치 후 실행
[Run]
Filename: "{app}\Discord-Bot-Dashboard.exe"; Description: "지금 대시보드 실행"; Flags: nowait postinstall skipifsilent; Comment: "설치 후 대시보드를 실행합니다"

; 메시지
[Messages]
korean.SetupWindowTitle=Discord Bot 설치 - 버전 1.0.0
korean.WelcomeLabel1=Discord Bot 설치 마법사에 오신 것을 환영합니다
korean.WelcomeLabel2=이 마법사는 당신의 컴퓨터에 Discord Bot을 설치합니다.%n%n설치를 계속하기 전에 모든 다른 응용 프로그램을 종료하는 것을 권장합니다.
korean.ClickNext=계속하려면 '다음'을 클릭하십시오.
korean.SelectDirLabel3=설치할 폴더를 선택하십시오.
korean.SelectDirBrowseLabel=폴더를 선택하려면 찾아보기를 클릭하십시오.
korean.DiskSpaceWarningTitle=충분한 디스크 공간 없음
korean.DiskSpaceWarning1=Discord Bot을 설치하려면 최소 500MB의 여유 디스크 공간이 필요합니다.
korean.SelectComponentsLabel2=설치할 구성 요소를 선택하십시오.
korean.FinishedHeadingLabel=Discord Bot 설치 완료
korean.FinishedLabelNoIcons=Discord Bot이 다음 위치에 성공적으로 설치되었습니다:
korean.FinishedLabel=설치가 완료되었습니다. Discord Bot을 시작하려면 설치된 바로가기를 클릭하십시오.
korean.FinishedRestartLabel=Discord Bot을 완전히 설치하려면 컴퓨터를 다시 시작해야 합니다. 지금 다시 시작하시겠습니까?
korean.UninstallProgram=제거 %1
korean.UninstallMessage=정말로 %1을(를) 제거하시겠습니까?

english.SetupWindowTitle=Discord Bot Setup - Version 1.0.0
english.WelcomeLabel1=Welcome to the Discord Bot Setup Wizard
english.WelcomeLabel2=This will install Discord Bot on your computer.%n%nIt is recommended that you close all other applications before continuing.
english.ClickNext=Click Next to continue.
english.SelectDirLabel3=Please select the folder in which to install Discord Bot.
english.SelectDirBrowseLabel=To continue, click Next. To select a different folder, click Browse.
english.DiskSpaceWarningTitle=Insufficient Disk Space
english.DiskSpaceWarning1=Discord Bot requires at least 500 MB of free disk space.
english.SelectComponentsLabel2=Select the components you want to install.
english.FinishedHeadingLabel=Completing the Discord Bot Setup Wizard
english.FinishedLabelNoIcons=Discord Bot has been successfully installed to:
english.FinishedLabel=Setup has completed. To launch Discord Bot, click Finish.
english.FinishedRestartLabel=To complete the installation of Discord Bot, Windows must be restarted. Would you like to restart now?
english.UninstallProgram=Uninstall %1
english.UninstallMessage=Are you sure you want to completely remove %1?

; 코드 섹션 (자동 실행 옵션)
[Code]
var
  AutoStartCheckbox: TNewCheckBox;

procedure CreateCustomPages;
var
  Page: TWizardPage;
begin
  Page := CreateCustomPage(wpSelectDir, '추가 옵션', '설정을 선택하세요');
  
  AutoStartCheckbox := TNewCheckBox.Create(Page);
  AutoStartCheckbox.Width := Page.SurfaceWidth;
  AutoStartCheckbox.Height := ScaleY(17);
  AutoStartCheckbox.Left := ScaleX(0);
  AutoStartCheckBox.Top := ScaleY(0);
  AutoStartCheckbox.Caption := 'Windows 시작 시 자동 실행 (선택사항)';
  AutoStartCheckbox.Checked := True;
  AutoStartCheckbox.Parent := Page.Surface;
end;

procedure InitializeWizard;
begin
  CreateCustomPages;
end;

function GetAutoStartValue: string;
begin
  if AutoStartCheckbox.Checked then
    Result := '--auto-start'
  else
    Result := '';
end;
