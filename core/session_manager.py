import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from .state_machine import InterviewFlow, StepState, DEPENDENCY_CHAIN


class SessionStateManager:
    """会话状态持久化管理"""
    
    def __init__(self, db_path: Path = Path(".sessions.db")):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    current_step TEXT NOT NULL,
                    step_states TEXT NOT NULL,
                    user_data TEXT NOT NULL,
                    analysis_results TEXT NOT NULL,
                    data_versions TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
    
    def create_session(self, ttl_hours: int = 24) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        expires_at = now + timedelta(hours=ttl_hours)
        
        initial_step_states = {step.value: StepState.PENDING.value for step in InterviewFlow}
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, InterviewFlow.INIT.value,
                 json.dumps(initial_step_states),
                 json.dumps({}),
                 json.dumps({}),
                 json.dumps({}),
                 now.isoformat(),
                 now.isoformat(),
                 expires_at.isoformat())
            )
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
            )
            row = cursor.fetchone()
        
        if not row:
            return None
        
        expires_at = datetime.fromisoformat(row[8]) if row[8] else None
        if expires_at and datetime.now() > expires_at:
            self.delete_session(session_id)
            return None
        
        return {
            "session_id": row[0],
            "current_step": InterviewFlow(row[1]),
            "step_states": {k: StepState(v) for k, v in json.loads(row[2]).items()},
            "user_data": json.loads(row[3]),
            "analysis_results": json.loads(row[4]),
            "data_versions": json.loads(row[5]),
            "created_at": datetime.fromisoformat(row[6]),
            "updated_at": datetime.fromisoformat(row[7]),
        }
    
    def update_user_data(self, session_id: str, key: str, value: Any):
        """更新用户输入数据，自动失效相关下游结果"""
        state = self.get_session(session_id)
        if not state:
            raise ValueError(f"Session {session_id} not found")
        
        state["user_data"][key] = value
        current_version = state["data_versions"].get(key, 0)
        state["data_versions"][key] = current_version + 1
        
        # 失效下游依赖
        downstream_keys = DEPENDENCY_CHAIN.get(key, [])
        for downstream in downstream_keys:
            state["analysis_results"].pop(downstream, None)
            state["data_versions"].pop(downstream, None)
        
        self._save_session(state)
    
    def save_result(self, session_id: str, key: str, result: Any):
        """保存分析结果"""
        state = self.get_session(session_id)
        if not state:
            raise ValueError(f"Session {session_id} not found")
        
        state["analysis_results"][key] = result
        state["data_versions"][key] = state["data_versions"].get(key, 0) + 1
        self._save_session(state)
    
    def _save_session(self, state: Dict[str, Any]):
        """保存会话状态"""
        state["updated_at"] = datetime.now()
        
        step_states_json = json.dumps({k: v.value for k, v in state["step_states"].items()})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE sessions SET 
                   current_step = ?, step_states = ?, user_data = ?, 
                   analysis_results = ?, data_versions = ?, updated_at = ?
                   WHERE session_id = ?""",
                (state["current_step"].value,
                 step_states_json,
                 json.dumps(state["user_data"]),
                 json.dumps(state["analysis_results"]),
                 json.dumps(state["data_versions"]),
                 state["updated_at"].isoformat(),
                 state["session_id"])
            )
    
    def add_message(self, session_id: str, role: str, content: str):
        """记录对话消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now().isoformat())
            )
    
    def delete_session(self, session_id: str):
        """删除会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM sessions WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )