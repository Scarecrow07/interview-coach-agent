import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import redis

from config.settings import settings


class LayeredCache:
    """三层缓存：内存→Redis→SQLite"""
    
    def __init__(self, redis_url: Optional[str] = None, db_path: Path = Path(".cache.db")):
        self.memory_cache: Dict[str, Any] = {}
        self.redis_client = redis.from_url(redis_url) if redis_url else None
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化SQLite缓存"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    prompt_version TEXT,
                    model_version TEXT
                )
            """)
    
    def _build_key(self, func_name: str, inputs: Dict[str, Any],
                   prompt_version: str = "v1.0", model_version: str = "deepseek-chat") -> str:
        """构建包含版本的缓存键"""
        input_hash = hashlib.md5(
            json.dumps(inputs, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()[:16]
        return f"{func_name}:{prompt_version}:{model_version}:{input_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """三层查找"""
        # L1: 内存
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2: Redis
        if self.redis_client:
            cached = self.redis_client.get(key)
            if cached:
                data = json.loads(cached)
                self.memory_cache[key] = data
                return data
        
        # L3: SQLite
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data, expires_at FROM cache WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
        
        if row:
            expires_at = datetime.fromisoformat(row[1]) if row[1] else None
            if expires_at and datetime.now() > expires_at:
                self.delete(key)
                return None
            
            data = json.loads(row[0])
            self.memory_cache[key] = data
            if self.redis_client:
                self.redis_client.setex(key, 3600, json.dumps(data))
            return data
        
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 86400):
        """三层写入"""
        self.memory_cache[key] = value
        if self.redis_client:
            self.redis_client.setex(key, ttl_seconds, json.dumps(value))
        
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?, ?, ?)",
                (key, json.dumps(value), datetime.now().isoformat(),
                 expires_at.isoformat(), settings.PROMPT_VERSION, settings.DEEPSEEK_MODEL)
            )
    
    def delete(self, key: str):
        """删除缓存"""
        self.memory_cache.pop(key, None)
        if self.redis_client:
            self.redis_client.delete(key)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
    
    def invalidate_by_prefix(self, prefix: str):
        """批量失效"""
        # 内存
        for key in list(self.memory_cache.keys()):
            if key.startswith(prefix):
                del self.memory_cache[key]
        
        # Redis
        if self.redis_client:
            for key in self.redis_client.scan_iter(f"{prefix}*"):
                self.redis_client.delete(key)
        
        # SQLite
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key LIKE ?", (f"{prefix}%",))


# 全局缓存实例
cache = LayeredCache(redis_url=settings.REDIS_URL)


def cached_analysis(func_name: str, inputs: Dict[str, Any], llm_call: Callable) -> Any:
    """缓存装饰的LLM调用"""
    key = cache._build_key(func_name, inputs)
    
    cached = cache.get(key)
    if cached:
        return cached
    
    result = llm_call()
    cache.set(key, result)
    return result