import sqlite3

DB_NAME = "chat_history.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_reply TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_message(user_message: str, bot_reply: str):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO messages (user_message, bot_reply) VALUES (?, ?)",
        (user_message, bot_reply)
    )
    conn.commit()
    conn.close()

def get_all_messages():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM messages ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def init_documents_table():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_document(filename: str, content: str):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO documents (filename, content) VALUES (?, ?)",
        (filename, content)
    )
    conn.commit()
    conn.close()

def get_latest_document():
    conn = get_db_connection()
    row = conn.execute(
        "SELECT * FROM documents ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None
def clear_messages():
    conn = get_db_connection()
    conn.execute("DELETE FROM messages")
    conn.commit()
    conn.close()