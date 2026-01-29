"""
Discord Bot 관리 대시보드 GUI
봇의 상태를 모니터링하고 제어할 수 있습니다.
"""

import PySimpleGUI as sg
import subprocess
import os
import json
import psutil
import threading
import time
from pathlib import Path
from datetime import datetime
import requests

class BotDashboard:
    """Discord Bot 관리 대시보드"""
    
    def __init__(self):
        # PySimpleGUI 테마 설정
        sg.theme('Dark Blue 3')
        
        self.bot_process = None
        self.bot_running = False
        self.log_lines = []
        self.max_logs = 100
        self.bot_path = Path(__file__).parent / "Discord-Bot.exe"
        self.version_file = Path(__file__).parent / "version.json"
        self.update_thread = None
        
        self.load_version()
    
    def load_version(self):
        """버전 정보 로드"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_version = data.get('version', 'Unknown')
            else:
                self.current_version = 'Unknown'
        except Exception as e:
            self.current_version = f'Error: {e}'
    
    def get_bot_status(self):
        """봇 상태 확인"""
        if self.bot_running and self.bot_process:
            if self.bot_process.poll() is None:
                return "🟢 실행 중"
            else:
                self.bot_running = False
                return "🔴 중지됨"
        return "🔴 중지됨"
    
    def get_system_info(self):
        """시스템 정보 조회"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            return {
                'cpu': cpu_percent,
                'memory': memory_percent,
                'memory_used': memory.used / (1024**3),
                'memory_total': memory.total / (1024**3)
            }
        except Exception as e:
            return {'cpu': 0, 'memory': 0, 'memory_used': 0, 'memory_total': 0}
    
    def start_bot(self):
        """봇 시작"""
        if not self.bot_running:
            if self.bot_path.exists():
                try:
                    # 기존 .bot_running 파일 삭제
                    running_flag = Path(__file__).parent / ".bot_running"
                    if running_flag.exists():
                        running_flag.unlink()
                    
                    self.bot_process = subprocess.Popen(
                        str(self.bot_path),
                        cwd=self.bot_path.parent,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                    self.bot_running = True
                    self.add_log("✅ 봇 시작 완료")
                    self.read_bot_output()
                except Exception as e:
                    self.add_log(f"❌ 봇 시작 실패: {e}")
            else:
                self.add_log("❌ Discord-Bot.exe를 찾을 수 없습니다")
        else:
            self.add_log("⚠️ 봇이 이미 실행 중입니다")
    
    def stop_bot(self):
        """봇 중지"""
        if self.bot_running and self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
                self.bot_running = False
                self.add_log("✅ 봇 중지 완료")
            except subprocess.TimeoutExpired:
                self.bot_process.kill()
                self.bot_running = False
                self.add_log("⚠️ 봇 강제 종료")
            except Exception as e:
                self.add_log(f"❌ 봇 중지 실패: {e}")
        else:
            self.add_log("⚠️ 봇이 실행 중이 아닙니다")
    
    def restart_bot(self):
        """봇 재시작"""
        self.add_log("🔄 봇 재시작 중...")
        self.stop_bot()
        time.sleep(1)
        self.start_bot()
    
    def read_bot_output(self):
        """봇 로그 읽기"""
        def read_logs():
            try:
                if self.bot_process:
                    for line in iter(self.bot_process.stdout.readline, ''):
                        if line:
                            self.add_log(line.strip())
            except Exception as e:
                self.add_log(f"로그 읽기 오류: {e}")
        
        if not self.update_thread or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=read_logs, daemon=True)
            self.update_thread.start()
    
    def add_log(self, message):
        """로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_lines.append(log_message)
        
        # 로그 크기 제한
        if len(self.log_lines) > self.max_logs:
            self.log_lines.pop(0)
    
    def get_logs(self):
        """로그 반환"""
        return '\n'.join(self.log_lines)
    
    def check_updates(self):
        """업데이트 확인"""
        try:
            self.add_log("🔄 업데이트 확인 중...")
            
            # GitHub API를 통해 최신 버전 확인
            github_repo = "user/discord-bot"
            url = f"https://api.github.com/repos/{github_repo}/releases/latest"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('tag_name', 'unknown').lstrip('v')
                
                if latest_version != self.current_version:
                    self.add_log(f"📦 새 버전 가능: {latest_version}")
                    return latest_version
                else:
                    self.add_log(f"✅ 최신 버전입니다: {self.current_version}")
            else:
                self.add_log("⚠️ 업데이트 확인 실패")
        except Exception as e:
            self.add_log(f"⚠️ 업데이트 확인 오류: {e}")
        
        return None
    
    def create_window(self):
        """GUI 윈도우 생성"""
        
        # 윈도우 레이아웃 정의
        layout = [
            # 헤더
            [sg.Text('🤖 Discord Bot 관리 대시보드', font=('Helvetica', 16, 'bold'))],
            [sg.Text(f'버전: {self.current_version}', font=('Helvetica', 10))],
            [sg.Separator()],
            
            # 봇 상태 섹션
            [sg.Frame('📊 봇 상태', [
                [sg.Text('상태: '), sg.Text('🔴 중지됨', key='BOT_STATUS', font=('Helvetica', 12, 'bold'))],
                [sg.Text('실행 시간: '), sg.Text('00:00:00', key='UPTIME')],
            ], font=('Helvetica', 10))],
            
            # 제어 버튼
            [sg.Frame('⚙️ 제어', [
                [
                    sg.Button('▶️ 시작', key='START_BOT', size=(12, 2), button_color=('white', 'green')),
                    sg.Button('⏹️ 중지', key='STOP_BOT', size=(12, 2), button_color=('white', 'red')),
                    sg.Button('🔄 재시작', key='RESTART_BOT', size=(12, 2), button_color=('white', 'orange')),
                ]
            ], font=('Helvetica', 10))],
            
            # 시스템 정보
            [sg.Frame('💻 시스템 정보', [
                [sg.Text('CPU 사용률: '), sg.ProgressBar(100, (30, 20), key='CPU_BAR', orientation='horizontal'), sg.Text('0%', key='CPU_TEXT')],
                [sg.Text('메모리: '), sg.ProgressBar(100, (30, 20), key='MEM_BAR', orientation='horizontal'), sg.Text('0%', key='MEM_TEXT')],
            ], font=('Helvetica', 10))],
            
            # 업데이트 섹션
            [sg.Frame('🔄 업데이트', [
                [
                    sg.Button('🔍 업데이트 확인', key='CHECK_UPDATE', size=(20, 1)),
                    sg.Text('최신 상태', key='UPDATE_STATUS', font=('Helvetica', 9)),
                ]
            ], font=('Helvetica', 10))],
            
            # 로그 섹션
            [sg.Frame('📋 로그', [
                [sg.Multiline(size=(80, 15), key='LOG_OUTPUT', disabled=True, autoscroll=True)],
                [sg.Button('🗑️ 로그 초기화', key='CLEAR_LOG', size=(15, 1))]
            ], font=('Helvetica', 10))],
            
            # 하단 버튼
            [sg.Button('❌ 종료', key='EXIT', size=(10, 1), button_color=('white', 'darkred'))],
        ]
        
        window = sg.Window('Discord Bot 관리 대시보드', layout, finalize=True, size=(900, 900))
        
        return window
    
    def run(self):
        """GUI 실행"""
        window = self.create_window()
        self.add_log("🚀 대시보드 시작됨")
        
        uptime_start = time.time()
        
        while True:
            # 타임아웃을 통해 주기적으로 상태 업데이트
            event, values = window.read(timeout=1000)
            
            # 윈도우 종료
            if event == sg.WINDOW_CLOSED or event == 'EXIT':
                if self.bot_running:
                    sg.Popup('알림', '봇을 먼저 중지해주세요')
                else:
                    break
            
            # 봇 시작
            elif event == 'START_BOT':
                self.start_bot()
            
            # 봇 중지
            elif event == 'STOP_BOT':
                self.stop_bot()
            
            # 봇 재시작
            elif event == 'RESTART_BOT':
                self.restart_bot()
            
            # 로그 초기화
            elif event == 'CLEAR_LOG':
                self.log_lines = []
                self.add_log("📋 로그가 초기화되었습니다")
            
            # 업데이트 확인
            elif event == 'CHECK_UPDATE':
                new_version = self.check_updates()
                if new_version:
                    window['UPDATE_STATUS'].update(f'업데이트 가능: {new_version}', text_color='yellow')
                else:
                    window['UPDATE_STATUS'].update('최신 상태', text_color='green')
            
            # 상태 업데이트
            window['BOT_STATUS'].update(self.get_bot_status())
            
            # 실행 시간 업데이트
            if self.bot_running:
                elapsed = int(time.time() - uptime_start)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                seconds = elapsed % 60
                window['UPTIME'].update(f'{hours:02d}:{minutes:02d}:{seconds:02d}')
            else:
                window['UPTIME'].update('00:00:00')
                uptime_start = time.time()
            
            # 시스템 정보 업데이트
            sys_info = self.get_system_info()
            window['CPU_BAR'].update(int(sys_info['cpu']))
            window['CPU_TEXT'].update(f"{int(sys_info['cpu'])}%")
            window['MEM_BAR'].update(int(sys_info['memory']))
            window['MEM_TEXT'].update(f"{int(sys_info['memory'])}% ({sys_info['memory_used']:.1f}GB/{sys_info['memory_total']:.1f}GB)")
            
            # 로그 출력 업데이트
            window['LOG_OUTPUT'].update(self.get_logs())
        
        # 봇이 실행 중이면 종료
        if self.bot_running:
            self.stop_bot()
        
        window.close()
        self.add_log("👋 대시보드 종료됨")


if __name__ == "__main__":
    dashboard = BotDashboard()
    dashboard.run()
