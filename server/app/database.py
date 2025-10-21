import sqlite3
import os
from contextlib import contextmanager

# Get the server directory (one level up from app)
SERVER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(SERVER_DIR, 'Database')
os.makedirs(DB_FOLDER, exist_ok=True)
DB_PATH = os.path.join(DB_FOLDER, 'server.db')

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    if not os.path.exists(DB_PATH):
        with get_db() as conn:
            schema_path = os.path.join(SERVER_DIR, 'schema.sql')
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
            conn.commit()