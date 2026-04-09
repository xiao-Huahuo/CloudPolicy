import sqlite3
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional

from app.agent_plugin.agent.config import AgentConfig


# --- 1. 独立会话结构体 (Data Class 思想) ---
class SessionRecord:
    """
    会话结构体，用于在应用层传递标准的会话信息。 
    """
    def __init__(self, session_id: str, user_id: str, session_name: str, create_time: float):
        self.session_id = session_id
        self.user_id = user_id
        self.session_name = session_name
        self.created_time = create_time

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，方便前端或微服务接口调用 """
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_name": self.session_name,
            "create_time": self.created_time
        }


# --- 2. 定义会话存储抽象基类 ---
class ConversationStore(ABC):
    """
    会话存储基类，定义完整的增删改查标准接口。 
    """

    @abstractmethod
    def create_session(self, user_id: str, session_name: str = "新对话") -> SessionRecord:
        """增：根据用户信息生成并存储新会话"""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """删：删除指定的会话记录"""
        pass

    @abstractmethod
    def update_session_name(self, session_id: str, new_name: str) -> bool:
        """改：修改会话展示名称"""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """查：获取单条会话详情"""
        pass

    @abstractmethod
    def get_user_sessions(self, user_id: str) -> List[SessionRecord]:
        """查：获取指定用户的所有历史会话列表"""
        pass

    @abstractmethod
    def close(self):
        """释放数据库资源"""
        pass


# --- 3. SQLite 完整接口实现 ---
class SQLiteConversationStore(ConversationStore):
    """
    基于 SQLite 的会话管理插件，提供完整的持久化增删改查功能。
    """

    def __init__(self):
        self.db_path = AgentConfig.RELATIONAL_DB_PATH
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._prepare_table()

    def _prepare_table(self):
        """确保会话记录表结构完整"""
        cursor = self.conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS session_history
                       (
                           session_id TEXT PRIMARY KEY,
                           user_id TEXT,
                           session_name TEXT,
                           create_time REAL
                       )
                       """)
        self.conn.commit()

    def create_session(self, user_id: str, session_name: str = "新对话") -> SessionRecord:
        """
        实现“增”：加密生成并入库。
        """
        current_time = time.time()
        # 构造原始哈希字符串
        raw_str = f"{user_id}_{current_time}"
        session_hash = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
        session_id = f"sess_{session_hash[:16]}"

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO session_history (session_id, user_id, session_name, create_time) VALUES (?, ?, ?, ?)",
            (session_id, user_id, session_name, current_time)
        )
        self.conn.commit()

        return SessionRecord(session_id, user_id, session_name, current_time)

    def delete_session(self, session_id: str) -> bool:
        """
        实现“删”：从数据库物理删除。 
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM session_history WHERE session_id = ?", (session_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def update_session_name(self, session_id: str, new_name: str) -> bool:
        """
        实现“改”：更新会话标题。 
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE session_history SET session_name = ? WHERE session_id = ?",
            (new_name, session_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """
        实现“查”：获取单条详细记录。 
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT session_id, user_id, session_name, create_time FROM session_history WHERE session_id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        if row:
            return SessionRecord(row[0], row[1], row[2], row[3])
        return None

    def get_user_sessions(self, user_id: str) -> List[SessionRecord]:
        """
        实现“查”：拉取列表。
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT session_id, user_id, session_name, create_time FROM session_history WHERE user_id = ? ORDER BY create_time DESC",
            (user_id,)
        )
        rows = cursor.fetchall()

        session_list = []
        for row in rows:
            session_list.append(SessionRecord(row[0], row[1], row[2], row[3]))
        return session_list

    def close(self):
        """释放资源 """
        if self.conn:
            self.conn.close()