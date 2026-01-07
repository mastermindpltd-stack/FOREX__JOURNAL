import sqlite3

DB_NAME = "trades.db"

# -------------------------------------------------
# CONNECTION
# -------------------------------------------------
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# -------------------------------------------------
# CREATE TABLE
# -------------------------------------------------
def create_table():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,

        pair TEXT,
        direction TEXT,

        entry REAL,
        stoploss REAL,
        takeprofit REAL,
        lot REAL,

        screenshot TEXT,
        notes TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
