"""
⚡ 캐싱 및 성능 최적화 매니저
- 데이터 캐싱으로 API 호출 최소화
- 비동기 처리 최적화
- 메모리 관리
"""

import time
import asyncio
import json
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
import aiofiles
import os

class CacheManager:
    """메모리 기반 캐시 관리자"""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expiry']:
                self.hits += 1
                return entry['value']
            else:
                del self.cache[key]
                self.misses += 1
                return None
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """캐시에 값 저장"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expiry': datetime.now() + timedelta(seconds=ttl),
            'created_at': datetime.now()
        }
    
    def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """모든 캐시 삭제"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'total': total,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_items': len(self.cache),
            'size_estimate_mb': sum(
                len(json.dumps(v['value'])) 
                for v in self.cache.values()
            ) / (1024 * 1024)
        }


class AsyncBatcher:
    """비동기 배치 처리 최적화"""
    
    def __init__(self, batch_size: int = 10, timeout: float = 5.0):
        self.batch_size = batch_size
        self.timeout = timeout
        self.queue: asyncio.Queue = None
    
    async def process_batch(
        self, 
        items: list, 
        handler: Callable,
        batch_size: Optional[int] = None
    ) -> list:
        """배치 단위로 항목 처리"""
        batch_size = batch_size or self.batch_size
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            try:
                # 배치 항목들을 병렬로 처리
                batch_results = await asyncio.gather(
                    *[handler(item) for item in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)
            except Exception as e:
                print(f"❌ 배치 처리 오류: {e}")
        
        return results


class PersistentCache:
    """파일 기반 지속적 캐시"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_file(self, key: str) -> str:
        """캐시 파일 경로"""
        # 파일명에 사용 불가능한 문자 제거
        safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    async def get(self, key: str) -> Optional[Any]:
        """파일에서 캐시 읽기"""
        try:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.loads(await f.read())
                    if datetime.fromisoformat(data['expiry']) > datetime.now():
                        return data['value']
                    else:
                        os.remove(cache_file)
                        return None
        except Exception as e:
            print(f"❌ 캐시 읽기 오류: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """파일에 캐시 저장"""
        try:
            cache_file = self._get_cache_file(key)
            data = {
                'value': value,
                'expiry': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
                'created_at': datetime.now().isoformat()
            }
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"❌ 캐시 저장 오류: {e}")
    
    async def delete(self, key: str) -> bool:
        """캐시 파일 삭제"""
        try:
            cache_file = self._get_cache_file(key)
            if os.path.exists(cache_file):
                os.remove(cache_file)
                return True
        except Exception as e:
            print(f"❌ 캐시 삭제 오류: {e}")
        return False


# 전역 캐시 인스턴스
memory_cache = CacheManager(default_ttl=1800)  # 30분
persistent_cache = PersistentCache()
async_batcher = AsyncBatcher(batch_size=15, timeout=5.0)
