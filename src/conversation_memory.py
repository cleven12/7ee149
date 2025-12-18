"""
Conversation memory management for WhatsApp chatbot
Stores conversation history per phone number (user ID) in JSON files
"""

import json
import logging
import os
from typing import Dict, List
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class ConversationMemory:
    def __init__(self, max_pairs: int = 4, session_timeout_hours: int = 24, storage_dir: str = "data/conversations"):
        """
        Initialize conversation memory storage with JSON persistence.

        Args:
            max_pairs: How many (user, assistant) turns to keep per user
            session_timeout_hours: Hours after which to clear old conversations
            storage_dir: Directory to store conversation JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[MEMORY] Storage directory: {self.storage_dir}")
        
        self.conversations: Dict[str, List[Dict]] = {}
        self.last_activity: Dict[str, datetime] = {}
        self.max_pairs = max_pairs
        self.session_timeout = timedelta(hours=session_timeout_hours)
        
        # Load existing conversations from disk
        self._load_all_conversations()
        logger.info(f"[MEMORY] Initialized with max_pairs={max_pairs}, timeout={session_timeout_hours}h")
    
    def get_history(self, phone_number: str) -> List[Dict]:
        """
        Get conversation history for a phone number
        
        Args:
            phone_number: User's phone number (e.g., "+1234567890")
        
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        self._cleanup_old_sessions()

        # Load from file if not in memory
        if phone_number not in self.conversations:
            logger.debug(f"[MEMORY] Loading conversation for {phone_number} from disk")
            if not self._load_conversation(phone_number):
                self.conversations[phone_number] = []
                logger.info(f"[MEMORY] New conversation started for {phone_number}")

        self._trim_history(phone_number)
        return self.conversations[phone_number]
    
    def add_message(self, phone_number: str, role: str, content: str):
        """
        Add a message to conversation history and save to disk
        
        Args:
            phone_number: User's phone number
            role: 'user' or 'assistant' or 'system'
            content: Message content
        """
        if phone_number not in self.conversations:
            self.conversations[phone_number] = []

        self.conversations[phone_number].append({
            "role": role,
            "content": content
        })
        logger.debug(f"[MEMORY] Added {role} message for {phone_number}")

        self._trim_history(phone_number)
        self.last_activity[phone_number] = datetime.now()
        self._save_conversation(phone_number)
    
    def clear_history(self, phone_number: str):
        """Clear conversation history for a specific phone number and delete file"""
        logger.info(f"[MEMORY] Clearing history for {phone_number}")
        if phone_number in self.conversations:
            del self.conversations[phone_number]
        if phone_number in self.last_activity:
            del self.last_activity[phone_number]
        self._delete_conversation_file(phone_number)
    
    def _cleanup_old_sessions(self):
        """Remove conversations that haven't been active recently and delete their files"""
        current_time = datetime.now()
        expired_numbers = [
            phone for phone, last_time in self.last_activity.items()
            if current_time - last_time > self.session_timeout
        ]
        
        if expired_numbers:
            logger.info(f"[MEMORY] Cleaning up {len(expired_numbers)} expired sessions")
        
        for phone in expired_numbers:
            self.clear_history(phone)
    
    def set_system_message(self, phone_number: str, system_message: str):
        """
        Set or update system message for a user and save to disk
        
        Args:
            phone_number: User's phone number
            system_message: System prompt/instructions
        """
        if phone_number not in self.conversations:
            self.conversations[phone_number] = []

        # Remove existing system message if any
        self.conversations[phone_number] = [
            msg for msg in self.conversations[phone_number]
            if msg["role"] != "system"
        ]

        # Add new system message at the beginning
        self.conversations[phone_number].insert(0, {
            "role": "system",
            "content": system_message
        })
        logger.debug(f"[MEMORY] Set system message for {phone_number}")

        self._trim_history(phone_number)
        self.last_activity[phone_number] = datetime.now()
        self._save_conversation(phone_number)

    def _trim_history(self, phone_number: str):
        """Keep only the system message and the last N user/assistant turns."""
        if phone_number not in self.conversations:
            return

        messages = self.conversations[phone_number]
        system_msgs = [msg for msg in messages if msg["role"] == "system"]
        other_msgs = [msg for msg in messages if msg["role"] != "system"]

        limit = self.max_pairs * 2 if self.max_pairs else len(other_msgs)
        trimmed_other = other_msgs[-limit:]

        self.conversations[phone_number] = system_msgs + trimmed_other

    def _get_file_path(self, phone_number: str) -> Path:
        """Get JSON file path for a phone number."""
        # Sanitize phone number for filename
        safe_name = phone_number.replace("+", "").replace(" ", "_").replace("@", "_at_")
        return self.storage_dir / f"{safe_name}.json"

    def _save_conversation(self, phone_number: str):
        """Save conversation to JSON file."""
        try:
            file_path = self._get_file_path(phone_number)
            data = {
                "phone_number": phone_number,
                "last_activity": self.last_activity.get(phone_number, datetime.now()).isoformat(),
                "messages": self.conversations.get(phone_number, [])
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"[MEMORY] Saved conversation for {phone_number} to {file_path}")
        except Exception as e:
            logger.error(f"[MEMORY] Error saving conversation for {phone_number}: {e}")

    def _load_conversation(self, phone_number: str) -> bool:
        """Load conversation from JSON file. Returns True if loaded."""
        try:
            file_path = self._get_file_path(phone_number)
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.conversations[phone_number] = data.get("messages", [])
            last_activity_str = data.get("last_activity")
            if last_activity_str:
                self.last_activity[phone_number] = datetime.fromisoformat(last_activity_str)
            
            logger.debug(f"[MEMORY] Loaded conversation for {phone_number} from {file_path}")
            return True
        except Exception as e:
            logger.error(f"[MEMORY] Error loading conversation for {phone_number}: {e}")
            return False

    def _load_all_conversations(self):
        """Load all conversation files on startup."""
        try:
            json_files = list(self.storage_dir.glob("*.json"))
            logger.info(f"[MEMORY] Found {len(json_files)} conversation files")
            
            for file_path in json_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    phone_number = data.get("phone_number")
                    if phone_number:
                        self.conversations[phone_number] = data.get("messages", [])
                        last_activity_str = data.get("last_activity")
                        if last_activity_str:
                            self.last_activity[phone_number] = datetime.fromisoformat(last_activity_str)
                        logger.debug(f"[MEMORY] Loaded {phone_number} from disk")
                except Exception as e:
                    logger.warning(f"[MEMORY] Could not load {file_path}: {e}")
        except Exception as e:
            logger.error(f"[MEMORY] Error loading conversations: {e}")

    def _delete_conversation_file(self, phone_number: str):
        """Delete conversation JSON file."""
        try:
            file_path = self._get_file_path(phone_number)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"[MEMORY] Deleted conversation file for {phone_number}")
        except Exception as e:
            logger.error(f"[MEMORY] Error deleting conversation file for {phone_number}: {e}")
