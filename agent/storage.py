import sqlite3, os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "data/agent.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            status    TEXT    NOT NULL,
            category  TEXT    DEFAULT 'finance',
            articles  INTEGER DEFAULT 0,
            analysis  TEXT    DEFAULT '',
            error     TEXT    DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def save_run(status, category="finance", articles=0, analysis="", error=""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO runs (timestamp,status,category,articles,analysis,error) "
        "VALUES (?,?,?,?,?,?)",
        (datetime.now().isoformat(), status, category, articles, analysis, error)
    )
    conn.commit()
    conn.close()

def get_runs(limit=20, category=None):
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    if category:
        cur = conn.execute(
            "SELECT id,timestamp,status,category,articles,analysis,error "
            "FROM runs WHERE category=? ORDER BY id DESC LIMIT ?",
            (category, limit)
        )
    else:
        cur = conn.execute(
            "SELECT id,timestamp,status,category,articles,analysis,error "
            "FROM runs ORDER BY id DESC LIMIT ?", (limit,)
        )
    rows = cur.fetchall()
    conn.close()
    keys = ["id", "timestamp", "status", "category", "articles", "analysis", "error"]
    return [dict(zip(keys, r)) for r in rows]