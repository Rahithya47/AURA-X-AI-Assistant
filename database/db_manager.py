import sqlite3
import os
import uuid

DATABASE = 'aura_database.db'

def get_db():
    """Connects to the database and returns a connection object with Row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database using the schema.sql file."""
    # Looks for schema.sql inside the database folder
    db_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    conn = get_db()
    try:
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            print("✅ Database initialized successfully.")
        else:
            print(f"❌ Error: {db_path} not found. Please ensure schema.sql is in the database folder.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        conn.close()

def create_chat_session(title="New Chat"):
    """Creates a new unique session ID and entry in the database."""
    session_id = str(uuid.uuid4())
    conn = get_db()
    try:
        conn.execute("INSERT INTO chat_sessions (session_id, title) VALUES (?, ?)", (session_id, title))
        conn.commit()
        return session_id
    except Exception as e:
        print(f"Error creating session: {e}")
        return None
    finally:
        conn.close()

def save_message(session_id, role, content):
    """Saves a single message and updates the session's activity timestamp."""
    conn = get_db()
    try:
        conn.execute("INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
        conn.execute("UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?", (session_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving message: {e}")
        return False
    finally:
        conn.close()

def get_messages(session_id, limit=50):
    """Retrieves messages for a session. Supports the 'limit' argument from app.py."""
    conn = get_db()
    try:
        cursor = conn.execute(
            """SELECT role, content 
               FROM chat_messages 
               WHERE session_id = ? 
               ORDER BY timestamp ASC 
               LIMIT ?""", 
            (session_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []
    finally:
        conn.close()

def get_message_count(session_id):
    """Counts messages in a session. Required by app.py for session logic."""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT COUNT(*) as count FROM chat_messages WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        return row['count'] if row else 0
    except Exception as e:
        print(f"Error counting messages: {e}")
        return 0
    finally:
        conn.close()

def get_chat_sessions(limit=20):
    """Returns a list of the most recent chat sessions."""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT session_id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Error getting sessions: {e}")
        return []
    finally:
        conn.close()

def update_session_title(session_id, title):
    """Updates the display title of a chat session."""
    conn = get_db()
    try:
        title = title[:50] + "..." if len(title) > 50 else title
        conn.execute("UPDATE chat_sessions SET title = ? WHERE session_id = ?", (title, session_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating title: {e}")
        return False
    finally:
        conn.close()

def clear_session_messages(session_id):
    """Deletes all messages for a specific session (Reset Chat)."""
    conn = get_db()
    try:
        conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error clearing messages: {e}")
        return False
    finally:
        conn.close()
