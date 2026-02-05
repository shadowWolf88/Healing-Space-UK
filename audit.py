import sqlite3
from datetime import datetime

DB = "therapist_app.db"

def log_event(username, actor, action, details=None):
    try:
        conn = sqlite3.connect(DB)
        conn.execute("INSERT INTO audit_logs (username, actor, action, details, timestamp) VALUES (%s,%s,%s,%s,%s)",
                     (username, actor, action, details or "", datetime.now()))
        conn.commit()
        conn.close()
    except Exception:
        # Best-effort logging; avoid crashing app if audit fails
        pass
