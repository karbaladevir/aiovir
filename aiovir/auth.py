"""
Authentication module for Virasty API.
"""

import json
import time
from pathlib import Path
from typing import Optional


class VirastyAuth:
    """
    Manages authentication and session persistence.
    
    Session stored in .vir format.
    """

    DEFAULT_SESSION_FILE = Path.home() / ".aiovir" / "session.vir"

    def __init__(self, session_file: Optional[str] = None):
        self.session_file = Path(session_file or self.DEFAULT_SESSION_FILE)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.token: Optional[str] = None
        self.s_token: Optional[str] = None
        self.username: Optional[str] = None
        self.user_id: Optional[str] = None
        self.display_name: Optional[str] = None
        
        self._load()

    @property
    def is_logged_in(self) -> bool:
        return self.token is not None

    def _load(self) -> None:
        if not self.session_file.exists():
            return
        
        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                self.token = data.get("token")
                self.s_token = data.get("s_token")
                self.username = data.get("username")
                self.user_id = data.get("user_id")
                self.display_name = data.get("display_name")
        except (json.JSONDecodeError, IOError):
            pass

    def save(self, token: str = "", s_token: str = "",
             username: str = "", user_id: str = "",
             display_name: str = "") -> None:
        if token:
            self.token = token
        if s_token:
            self.s_token = s_token
        if username:
            self.username = username
        if user_id:
            self.user_id = user_id
        if display_name:
            self.display_name = display_name
        
        with open(self.session_file, 'w') as f:
            json.dump({
                "token": self.token,
                "s_token": self.s_token,
                "username": self.username,
                "user_id": self.user_id,
                "display_name": self.display_name,
                "saved_at": int(time.time())
            }, f, indent=2)

    def clear(self) -> None:
        self.token = None
        self.s_token = None
        self.username = None
        self.user_id = None
        self.display_name = None
        
        if self.session_file.exists():
            self.session_file.unlink()

    def __repr__(self) -> str:
        if self.is_logged_in:
            return f"VirastyAuth(@{self.username})"
        return "VirastyAuth(not logged in)"