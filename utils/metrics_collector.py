import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from config.settings import settings


class MetricsCollector:
    """指标收集"""
    
    def __init__(self, db_path: Path = Path(".metrics.db")):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS llm_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    step TEXT,
                    model TEXT,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    latency_ms INTEGER,
                    success BOOLEAN,
                    error_type TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT,
                    hit BOOLEAN,
                    timestamp TEXT
                )
            """)
    
    def record_llm_call(self, session_id: str, step: str, model: str,
                        input_tokens: int, output_tokens: int, latency_ms: int,
                        success: bool, error_type: Optional[str] = None):
        """记录LLM调用"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO llm_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (None, session_id, step, model, input_tokens, output_tokens,
                 latency_ms, success, error_type, datetime.now().isoformat())
            )
    
    def record_cache_hit(self, key: str, hit: bool):
        """记录缓存命中"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO cache_stats VALUES (?, ?, ?, ?)",
                (None, key, hit, datetime.now().isoformat())
            )
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """获取每日统计"""
        yesterday = datetime.now() - timedelta(days=1)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """SELECT COUNT(*), AVG(latency_ms), SUM(input_tokens + output_tokens)
                   FROM llm_calls WHERE timestamp > ? AND success = 1""",
                (yesterday.isoformat(),)
            )
            llm_row = cursor.fetchone()
            
            cursor = conn.execute(
                """SELECT SUM(CASE WHEN hit = 1 THEN 1 ELSE 0 END) as hits,
                   COUNT(*) as total FROM cache_stats WHERE timestamp > ?""",
                (yesterday.isoformat(),)
            )
            cache_row = cursor.fetchone()
        
        return {
            "llm_calls": llm_row[0] if llm_row else 0,
            "avg_latency_ms": llm_row[1] if llm_row else 0,
            "total_tokens": llm_row[2] if llm_row else 0,
            "cache_hit_rate": cache_row[0] / cache_row[1] if cache_row and cache_row[1] > 0 else 0,
        }


# 全局指标收集实例
metrics = MetricsCollector()


def cached_analysis_with_metrics(func_name: str, inputs: Dict, llm_call: Callable) -> Any:
    """带指标记录的缓存调用"""
    from core.cache_manager import cache
    
    key = cache._build_key(func_name, inputs)
    
    cached = cache.get(key)
    if cached:
        metrics.record_cache_hit(key, True)
        return cached
    
    metrics.record_cache_hit(key, False)
    
    start_time = time.time()
    result = llm_call()
    latency_ms = int((time.time() - start_time) * 1000)
    
    # 假设结果中包含token数
    input_tokens = result.get("usage", {}).get("prompt_tokens", 0) if isinstance(result, dict) else 0
    output_tokens = result.get("usage", {}).get("completion_tokens", 0) if isinstance(result, dict) else 0
    
    metrics.record_llm_call(
        session_id="unknown", step=func_name, model=settings.DEEPSEEK_MODEL,
        input_tokens=input_tokens, output_tokens=output_tokens,
        latency_ms=latency_ms, success=True
    )
    
    cache.set(key, result)
    return result