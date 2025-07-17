"""
セッション管理モジュール
セッションの作成、取得、更新、削除を管理
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SessionManager:
    """セッション管理クラス"""
    
    def __init__(self, session_timeout_hours: int = 24):
        """
        初期化
        
        Args:
            session_timeout_hours: セッションタイムアウト時間（時間）
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.cleanup_interval = 3600  # 1時間ごとにクリーンアップ
        self.last_cleanup = time.time()
        
        logger.info(f"SessionManager initialized with {session_timeout_hours}h timeout")
    
    def create_session(self) -> str:
        """
        新しいセッションを作成
        
        Returns:
            str: セッションID
        """
        session_id = str(uuid.uuid4())
        
        # 初期セッションデータ
        session_data = {
            "session_id": session_id,
            "created_at": self.get_current_timestamp(),
            "last_accessed": self.get_current_timestamp(),
            "conversation_history": [],
            "user_preferences": {},
            "search_history": [],
            "favorites": [],
            "settings": {
                "language": "ja",
                "theme": "light",
                "notifications": True
            }
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def create_session_data(self, session_id: str) -> Dict[str, Any]:
        """
        セッションデータを作成
        
        Args:
            session_id: セッションID
            
        Returns:
            Dict[str, Any]: セッションデータ
        """
        session_data = {
            "session_id": session_id,
            "created_at": self.get_current_timestamp(),
            "last_accessed": self.get_current_timestamp(),
            "conversation_history": [],
            "user_preferences": {},
            "search_history": [],
            "favorites": [],
            "settings": {
                "language": "ja",
                "theme": "light",
                "notifications": True
            }
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"Created session data for: {session_id}")
        
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        セッションデータを取得
        
        Args:
            session_id: セッションID
            
        Returns:
            Optional[Dict[str, Any]]: セッションデータ（存在しない場合はNone）
        """
        if session_id not in self.sessions:
            return None
        
        session_data = self.sessions[session_id]
        
        # セッションタイムアウトチェック
        if self._is_session_expired(session_data):
            logger.info(f"Session expired: {session_id}")
            self.delete_session(session_id)
            return None
        
        # 最終アクセス時刻を更新
        session_data["last_accessed"] = self.get_current_timestamp()
        
        return session_data
    
    def update_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        セッションデータを更新
        
        Args:
            session_id: セッションID
            session_data: 更新するセッションデータ
            
        Returns:
            bool: 更新成功時True
        """
        if session_id not in self.sessions:
            logger.warning(f"Attempted to update non-existent session: {session_id}")
            return False
        
        # 最終アクセス時刻を更新
        session_data["last_accessed"] = self.get_current_timestamp()
        
        self.sessions[session_id] = session_data
        logger.debug(f"Updated session: {session_id}")
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        セッションを削除
        
        Args:
            session_id: セッションID
            
        Returns:
            bool: 削除成功時True
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        
        return False
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        全てのアクティブセッションを取得
        
        Returns:
            List[Dict[str, Any]]: セッション情報のリスト
        """
        self._cleanup_expired_sessions()
        
        sessions = []
        for session_id, session_data in self.sessions.items():
            sessions.append({
                "session_id": session_id,
                "created_at": session_data.get("created_at"),
                "last_accessed": session_data.get("last_accessed"),
                "conversation_count": len(session_data.get("conversation_history", [])),
                "favorites_count": len(session_data.get("favorites", []))
            })
        
        return sessions
    
    def get_session_count(self) -> int:
        """
        アクティブセッション数を取得
        
        Returns:
            int: セッション数
        """
        self._cleanup_expired_sessions()
        return len(self.sessions)
    
    def add_conversation_message(self, session_id: str, role: str, content: str) -> bool:
        """
        会話履歴にメッセージを追加
        
        Args:
            session_id: セッションID
            role: メッセージの役割（user/assistant）
            content: メッセージ内容
            
        Returns:
            bool: 追加成功時True
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": self.get_current_timestamp()
        }
        
        session_data["conversation_history"].append(message)
        
        # 会話履歴が長すぎる場合は古いものを削除
        max_history = 100
        if len(session_data["conversation_history"]) > max_history:
            session_data["conversation_history"] = session_data["conversation_history"][-max_history:]
        
        return self.update_session(session_id, session_data)
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        会話履歴を取得
        
        Args:
            session_id: セッションID
            limit: 取得する履歴の最大数
            
        Returns:
            List[Dict[str, Any]]: 会話履歴
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return []
        
        history = session_data.get("conversation_history", [])
        return history[-limit:] if limit > 0 else history
    
    def update_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """
        ユーザー希望を更新
        
        Args:
            session_id: セッションID
            preferences: ユーザー希望データ
            
        Returns:
            bool: 更新成功時True
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        session_data["user_preferences"].update(preferences)
        return self.update_session(session_id, session_data)
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """
        ユーザー希望を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            Dict[str, Any]: ユーザー希望データ
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return {}
        
        return session_data.get("user_preferences", {})
    
    def add_search_history(self, session_id: str, search_query: str, results_count: int) -> bool:
        """
        検索履歴を追加
        
        Args:
            session_id: セッションID
            search_query: 検索クエリ
            results_count: 検索結果数
            
        Returns:
            bool: 追加成功時True
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        search_record = {
            "query": search_query,
            "results_count": results_count,
            "timestamp": self.get_current_timestamp()
        }
        
        session_data["search_history"].append(search_record)
        
        # 検索履歴が長すぎる場合は古いものを削除
        max_history = 50
        if len(session_data["search_history"]) > max_history:
            session_data["search_history"] = session_data["search_history"][-max_history:]
        
        return self.update_session(session_id, session_data)
    
    def get_search_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        検索履歴を取得
        
        Args:
            session_id: セッションID
            limit: 取得する履歴の最大数
            
        Returns:
            List[Dict[str, Any]]: 検索履歴
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return []
        
        history = session_data.get("search_history", [])
        return history[-limit:] if limit > 0 else history
    
    def add_favorite(self, session_id: str, product_data: Dict[str, Any]) -> bool:
        """
        お気に入りに商品を追加
        
        Args:
            session_id: セッションID
            product_data: 商品データ
            
        Returns:
            bool: 追加成功時True
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        # 重複チェック
        product_id = product_data.get("id")
        favorites = session_data.get("favorites", [])
        
        if not any(fav.get("id") == product_id for fav in favorites):
            favorites.append(product_data)
            session_data["favorites"] = favorites
            return self.update_session(session_id, session_data)
        
        return True  # 既に存在する場合は成功として扱う
    
    def remove_favorite(self, session_id: str, product_id: str) -> bool:
        """
        お気に入りから商品を削除
        
        Args:
            session_id: セッションID
            product_id: 商品ID
            
        Returns:
            bool: 削除成功時True
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        favorites = session_data.get("favorites", [])
        original_count = len(favorites)
        
        session_data["favorites"] = [fav for fav in favorites if fav.get("id") != product_id]
        
        if len(session_data["favorites"]) < original_count:
            return self.update_session(session_id, session_data)
        
        return False
    
    def get_favorites(self, session_id: str) -> List[Dict[str, Any]]:
        """
        お気に入りリストを取得
        
        Args:
            session_id: セッションID
            
        Returns:
            List[Dict[str, Any]]: お気に入りリスト
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return []
        
        return session_data.get("favorites", [])
    
    def update_settings(self, session_id: str, settings: Dict[str, Any]) -> bool:
        """
        セッション設定を更新
        
        Args:
            session_id: セッションID
            settings: 設定データ
            
        Returns:
            bool: 更新成功時True
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        session_data["settings"].update(settings)
        return self.update_session(session_id, session_data)
    
    def get_settings(self, session_id: str) -> Dict[str, Any]:
        """
        セッション設定を取得
        
        Args:
            session_id: セッションID
            
        Returns:
            Dict[str, Any]: 設定データ
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return {}
        
        return session_data.get("settings", {})
    
    def get_current_timestamp(self) -> str:
        """
        現在のタイムスタンプを取得
        
        Returns:
            str: ISO形式のタイムスタンプ
        """
        return datetime.now().isoformat()
    
    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """
        セッションが期限切れかチェック
        
        Args:
            session_data: セッションデータ
            
        Returns:
            bool: 期限切れの場合True
        """
        last_accessed = session_data.get("last_accessed")
        if not last_accessed:
            return True
        
        try:
            last_accessed_dt = datetime.fromisoformat(last_accessed)
            return datetime.now() - last_accessed_dt > self.session_timeout
        except (ValueError, TypeError):
            return True
    
    def _cleanup_expired_sessions(self) -> int:
        """
        期限切れセッションをクリーンアップ
        
        Returns:
            int: 削除されたセッション数
        """
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return 0
        
        expired_sessions = []
        for session_id, session_data in self.sessions.items():
            if self._is_session_expired(session_data):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        self.last_cleanup = current_time
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        セッション統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        self._cleanup_expired_sessions()
        
        total_sessions = len(self.sessions)
        total_conversations = sum(
            len(session.get("conversation_history", [])) 
            for session in self.sessions.values()
        )
        total_favorites = sum(
            len(session.get("favorites", [])) 
            for session in self.sessions.values()
        )
        
        return {
            "total_sessions": total_sessions,
            "total_conversations": total_conversations,
            "total_favorites": total_favorites,
            "average_conversations_per_session": total_conversations / total_sessions if total_sessions > 0 else 0,
            "average_favorites_per_session": total_favorites / total_sessions if total_sessions > 0 else 0
        } 