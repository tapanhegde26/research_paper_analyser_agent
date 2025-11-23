"""
Session Manager

Manages user sessions for the research analysis system.
Implements InMemorySessionService pattern from ADK.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from observability.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """
    Manages sessions for research analysis.
    
    Implements in-memory session storage with state management.
    Sessions persist conversation state, analyzed papers, and user preferences.
    """
    
    def __init__(self):
        """Initialize session manager"""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_data: Dict[str, Dict[str, Any]] = defaultdict(dict)
        logger.info("Session Manager initialized")
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session
        
        Args:
            user_id: Optional user identifier
            metadata: Optional session metadata
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        self._sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": metadata or {},
            "state": "active"
        }
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session dictionary or None
        """
        session = self._sessions.get(session_id)
        if session:
            # Update last accessed time
            session["last_accessed"] = datetime.now().isoformat()
        return session
    
    def resume_session(self, session_id: str) -> bool:
        """
        Resume an existing session
        
        Args:
            session_id: Session to resume
        
        Returns:
            True if session exists and was resumed
        """
        session = self.get_session(session_id)
        if session:
            session["state"] = "active"
            session["last_accessed"] = datetime.now().isoformat()
            logger.info(f"Resumed session: {session_id}")
            return True
        
        logger.warning(f"Session not found: {session_id}")
        return False
    
    def pause_session(self, session_id: str) -> bool:
        """
        Pause a session (long-running operations support)
        
        Args:
            session_id: Session to pause
        
        Returns:
            True if successfully paused
        """
        session = self.get_session(session_id)
        if session:
            session["state"] = "paused"
            session["paused_at"] = datetime.now().isoformat()
            logger.info(f"Paused session: {session_id}")
            return True
        return False
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session
        
        Args:
            session_id: Session to end
        
        Returns:
            True if successfully ended
        """
        session = self.get_session(session_id)
        if session:
            session["state"] = "ended"
            session["ended_at"] = datetime.now().isoformat()
            logger.info(f"Ended session: {session_id}")
            return True
        return False
    
    def store_data(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> bool:
        """
        Store data in session
        
        Args:
            session_id: Session identifier
            key: Data key
            value: Data value
        
        Returns:
            True if stored successfully
        """
        if session_id not in self._sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        self._session_data[session_id][key] = value
        logger.debug(f"Stored data in session {session_id}: {key}")
        return True
    
    def get_data(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Retrieve data from session
        
        Args:
            session_id: Session identifier
            key: Data key
            default: Default value if key not found
        
        Returns:
            Stored value or default
        """
        return self._session_data.get(session_id, {}).get(key, default)
    
    def get_all_data(self, session_id: str) -> Dict[str, Any]:
        """
        Get all data for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            All session data
        """
        return self._session_data.get(session_id, {})
    
    def delete_data(self, session_id: str, key: str) -> bool:
        """
        Delete data from session
        
        Args:
            session_id: Session identifier
            key: Data key to delete
        
        Returns:
            True if deleted
        """
        if session_id in self._session_data and key in self._session_data[session_id]:
            del self._session_data[session_id][key]
            logger.debug(f"Deleted data from session {session_id}: {key}")
            return True
        return False
    
    def clear_session_data(self, session_id: str) -> bool:
        """
        Clear all data for a session
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if cleared
        """
        if session_id in self._session_data:
            self._session_data[session_id].clear()
            logger.info(f"Cleared data for session: {session_id}")
            return True
        return False
    
    def list_sessions(
        self,
        user_id: Optional[str] = None,
        state: Optional[str] = None
    ) -> list:
        """
        List sessions with optional filtering
        
        Args:
            user_id: Filter by user ID
            state: Filter by state
        
        Returns:
            List of session dictionaries
        """
        sessions = list(self._sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if s.get("user_id") == user_id]
        
        if state:
            sessions = [s for s in sessions if s.get("state") == state]
        
        return sessions
    
    def get_session_time(self, session_id: str) -> str:
        """
        Get session creation time
        
        Args:
            session_id: Session identifier
        
        Returns:
            ISO format timestamp
        """
        session = self.get_session(session_id)
        return session.get("created_at", "") if session else ""
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """
        Clean up old sessions (maintenance)
        
        Args:
            max_age_hours: Maximum age in hours
        """
        now = datetime.now()
        to_delete = []
        
        for session_id, session in self._sessions.items():
            created = datetime.fromisoformat(session["created_at"])
            age_hours = (now - created).total_seconds() / 3600
            
            if age_hours > max_age_hours and session["state"] == "ended":
                to_delete.append(session_id)
        
        for session_id in to_delete:
            del self._sessions[session_id]
            if session_id in self._session_data:
                del self._session_data[session_id]
            logger.info(f"Cleaned up old session: {session_id}")
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old sessions")

