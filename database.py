import sqlite3
import json
from datetime import datetime

DB_FILE = "bugsense_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            timestamp TEXT,
            original_code TEXT,
            bug_type TEXT,
            root_cause TEXT,
            corrected_code TEXT,
            chat_history TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_session(session_id, original_code, bug_type, root_cause, corrected_code, chat_history):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    chat_json = json.dumps(chat_history)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT OR REPLACE INTO sessions 
        (session_id, timestamp, original_code, bug_type, root_cause, corrected_code, chat_history)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, timestamp, original_code, bug_type, root_cause, corrected_code, chat_json))
    conn.commit()
    conn.close()

def get_all_sessions():
    """Now fetches the bug_type to use as a meaningful title!"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Grab the bug_type in addition to ID and timestamp
    cursor.execute('SELECT session_id, timestamp, bug_type FROM sessions ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [{"session_id": r[0], "timestamp": r[1], "bug_type": r[2]} for r in rows]

def load_session(session_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "session_id": row[0],
            "timestamp": row[1],
            "original_code": row[2],
            "bug_type": row[3],
            "root_cause": row[4],
            "corrected_code": row[5],
            "chat_history": json.loads(row[6]) 
        }
    return None