"""
공통 헬퍼 함수
"""

def create_progress_bar(progress: int, length: int = 10) -> str:
    """진행도 바 생성"""
    filled = int((progress / 100) * length)
    empty = length - filled
    return "█" * filled + "░" * empty

def format_time(seconds: int) -> str:
    """초를 시간:분:초 형식으로 변환"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def clamp(value: int, min_val: int, max_val: int) -> int:
    """값을 최소값과 최대값 사이로 제한"""
    return max(min_val, min(value, max_val))
