# core/memory_manager.py
# Manages conversation history per session
# Reads and writes to SQLite database

import uuid
from database.db_manager import (
    create_chat_session,
    save_message,
    get_messages,
    clear_session_messages
)
from config import config


def create_new_session():
    """
    Create a brand new chat session
    Returns: session_id (string)
    """
    session_id = "session_" + str(uuid.uuid4()).replace("-", "")[:16]
    create_chat_session(session_id)
    print(f"✅ New session created: {session_id}")
    return session_id


def ensure_session_exists(session_id):
    """
    Make sure session exists in database
    Creates it if it doesn't exist
    Returns: session_id
    """
    if not session_id:
        return create_new_session()
    
    # Create session (will be ignored if already exists)
    create_chat_session(session_id)
    return session_id


def add_user_message(session_id, content):
    """
    Save a user message to history
    
    Args:
        session_id: which conversation
        content: what the user said
    
    Returns: True/False
    """
    session_id = ensure_session_exists(session_id)
    return save_message(session_id, "user", content)


def add_assistant_message(session_id, content):
    """
    Save AURA's response to history
    
    Args:
        session_id: which conversation
        content: what AURA replied
    
    Returns: True/False
    """
    session_id = ensure_session_exists(session_id)
    return save_message(session_id, "assistant", content)


def get_conversation_history(session_id, limit=None):
    """
    Get conversation history for a session
    
    Args:
        session_id: which conversation to retrieve
        limit: max messages to return
               defaults to config.CHAT_HISTORY_LIMIT
    
    Returns:
        list of message dicts:
        [{"role": "user", "content": "...", "timestamp": "..."},
         {"role": "assistant", "content": "...", "timestamp": "..."}]
    """
    if not session_id:
        return []
    
    max_messages = limit or config.CHAT_HISTORY_LIMIT
    messages = get_messages(session_id, max_messages)
    return messages


def clear_conversation(session_id):
    """
    Clear all messages for a session
    
    Args:
        session_id: which session to clear
    
    Returns: True/False
    """
    if not session_id:
        return False
    
    result = clear_session_messages(session_id)
    if result:
        print(f"✅ Session cleared: {session_id}")
    return result


def get_history_for_llm(session_id, limit=None):
    """
    Get conversation history formatted for LM Studio
    Returns only role and content (no timestamps)
    
    Returns:
        [{"role": "user", "content": "..."},
         {"role": "assistant", "content": "..."}]
    """
    messages = get_conversation_history(session_id, limit)
    
    return [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in messages
        if msg.get("role") in ["user", "assistant"]
    ]