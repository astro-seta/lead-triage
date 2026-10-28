import sqlite3

DB = "leads.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                name TEXT, email TEXT, message TEXT,
                category TEXT, urgency TEXT,
                summary TEXT, suggested_reply TEXT,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ok',
                error TEXT
            )
        """)