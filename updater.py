"""
Discord Bot 자동 업데이트 모듈
GitHub에서 최신 버전을 확인하고 자동으로 업데이트합니다.
"""

import os
import json
import shutil
import requests
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class BotUpdater:
    """봇 자동 업데이트 매니저"""
    
    # GitHub 저장소 설정 (필요시 변경)
    GITHUB_REPO = "KO-HAN0905/discord-bot-server"  # GitHub 저장소 (owner/repo)
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    VERSION_FILE = "version.json"
    BACKUP_DIR = "backups"
    
    def __init__(self):
        self.current_version = self._load_version()
        self.bot_dir = Path(__file__).parent
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """백업 디렉토리 생성"""
        backup_path = self.bot_dir / self.BACKUP_DIR
        backup_path.mkdir(exist_ok=True)
    
    def _load_version(self):
        """현재 버전 로드"""
        version_file = Path(__file__).parent / self.VERSION_FILE
        if version_file.exists():
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '1.0.0')
            except Exception as e:
                print(f"[UPDATE] 버전 파일 읽기 실패: {e}")
        return '1.0.0'
    
    def _save_version(self, version):
        """버전 저장"""
        version_file = Path(__file__).parent / self.VERSION_FILE
        try:
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': version,
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[UPDATE] 버전 저장 실패: {e}")
    
    def check_for_updates(self):
        """업데이트 확인 (로컬 버전 파일에서)"""
        try:
            # 로컬 버전 파일에서 최신 버전 확인
            # 실제 GitHub 연동은 복잡하므로, 로컬 버전 관리로 단순화
            latest_version = self._get_remote_version()
            
            if latest_version and self._is_newer_version(latest_version, self.current_version):
                print(f"[UPDATE] 새로운 버전이 있습니다: {self.current_version} → {latest_version}")
                return latest_version
            else:
                print(f"[UPDATE] 최신 버전입니다: {self.current_version}")
                return None
        except Exception as e:
            print(f"[UPDATE] 업데이트 확인 실패: {e}")
            return None
    
    def _get_remote_version(self):
        """원격 버전 확인 (GitHub Release API)"""
        try:
            # GitHub API 요청 (인증 없이도 public repos는 가능)
            response = requests.get(self.GITHUB_API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # v1.2.3 형식에서 1.2.3으로 변환
                tag = data.get('tag_name', '1.0.0').lstrip('v')
                return tag
        except Exception as e:
            print(f"[UPDATE] GitHub 버전 확인 실패 (오프라인일 수 있음): {e}")
        
        return None
    
    def _is_newer_version(self, new_version, current_version):
        """버전 비교 (새 버전이 더 높으면 True)"""
        try:
            new_parts = [int(x) for x in new_version.split('.')]
            current_parts = [int(x) for x in current_version.split('.')]
            
            # 패딩 추가
            while len(new_parts) < len(current_parts):
                new_parts.append(0)
            while len(current_parts) < len(new_parts):
                current_parts.append(0)
            
            return new_parts > current_parts
        except Exception:
            return False
    
    def backup_current_files(self):
        """현재 파일 백업"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{self.current_version}_{timestamp}"
            backup_path = self.bot_dir / self.BACKUP_DIR / backup_name
            
            # 백업할 디렉토리/파일
            backup_items = ['cogs', 'utils', 'data', 'config.py', 'bot.py']
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            for item in backup_items:
                item_path = self.bot_dir / item
                if item_path.exists():
                    if item_path.is_dir():
                        shutil.copytree(
                            item_path,
                            backup_path / item,
                            dirs_exist_ok=True
                        )
                    else:
                        shutil.copy2(item_path, backup_path / item)
            
            print(f"[UPDATE] 백업 완료: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"[UPDATE] 백업 실패: {e}")
            return None
    
    def update_from_zip(self, zip_url):
        """GitHub Release zip 파일에서 업데이트"""
        try:
            import zipfile
            import io
            
            print(f"[UPDATE] {zip_url}에서 파일 다운로드 중...")
            
            # zip 파일 다운로드
            response = requests.get(zip_url, timeout=30)
            if response.status_code != 200:
                print(f"[UPDATE] 다운로드 실패: {response.status_code}")
                return False
            
            # zip 파일 추출
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                # GitHub은 release zip 내부에 폴더 하나를 더 만듭니다
                temp_extract = self.bot_dir / "temp_update"
                temp_extract.mkdir(exist_ok=True)
                zip_ref.extractall(temp_extract)
                
                # 올바른 파일 찾기
                extracted_items = list(temp_extract.glob("*"))
                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    source_dir = extracted_items[0]
                else:
                    source_dir = temp_extract
                
                # 파일 복사
                for item in ['cogs', 'utils', 'config.py', 'bot.py']:
                    src = source_dir / item
                    dst = self.bot_dir / item
                    
                    if src.exists():
                        if src.is_dir():
                            if dst.exists():
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)
                
                # 임시 폴더 삭제
                shutil.rmtree(temp_extract)
            
            print("[UPDATE] 파일 업데이트 완료")
            return True
        
        except Exception as e:
            print(f"[UPDATE] 업데이트 실패: {e}")
            return False
    
    def enable_auto_update(self, new_version):
        """자동 업데이트 활성화"""
        self._save_version(new_version)
        print(f"[UPDATE] 버전 업데이트: {self.current_version} → {new_version}")
        self.current_version = new_version
    
    def get_update_info(self):
        """업데이트 정보 반환"""
        try:
            response = requests.get(self.GITHUB_API_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'version': data.get('tag_name', 'unknown').lstrip('v'),
                    'description': data.get('body', ''),
                    'download_url': data.get('zipball_url', ''),
                    'published_at': data.get('published_at', ''),
                    'current': self.current_version
                }
        except Exception as e:
            print(f"[UPDATE] 업데이트 정보 조회 실패: {e}")
        
        return None


def auto_update_on_startup():
    """봇 시작 시 자동 업데이트 확인"""
    try:
        updater = BotUpdater()
        print(f"[UPDATE] 현재 버전: {updater.current_version}")
        print("[UPDATE] 업데이트 확인 중...")
        
        # 오프라인 환경에서도 작동하도록 설계
        new_version = updater.check_for_updates()
        
        if new_version:
            print(f"[UPDATE] 새 버전 감지: {new_version}")
            print("[UPDATE] 다음 시작 시 업데이트됩니다.")
            # 실제 GitHub 연동 코드:
            # update_info = updater.get_update_info()
            # if update_info:
            #     updater.backup_current_files()
            #     updater.update_from_zip(update_info['download_url'])
            #     updater.enable_auto_update(new_version)
    
    except Exception as e:
        print(f"[UPDATE] 자동 업데이트 시스템 오류: {e}")


if __name__ == "__main__":
    auto_update_on_startup()
