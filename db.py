import os
import sqlite3
from config import DB_PATH, DATA_DIR


def get_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rank_name TEXT NOT NULL,
            reason TEXT DEFAULT '',
            awarded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, rank_name)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            medal_name TEXT NOT NULL,
            reason TEXT DEFAULT '',
            awarded_by INTEGER,
            awarded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, medal_name)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_ranks_user ON ranks(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_medals_user ON medals(user_id)")
    conn.commit()
    conn.close()


# ---------- Звания ----------

def add_rank(user_id, rank_name, reason=""):
    """Установить звание. Новое звание заменяет предыдущее (остаётся одно)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ranks WHERE user_id = ?", (user_id,))
    cur.execute(
        "INSERT INTO ranks (user_id, rank_name, reason) VALUES (?, ?, ?)",
        (user_id, rank_name, reason),
    )
    conn.commit()
    conn.close()
    return True


def get_ranks(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT rank_name, reason, awarded_at FROM ranks WHERE user_id = ? ORDER BY awarded_at",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


# ---------- Медали ----------

def add_medal(user_id, medal_name, reason="", awarded_by=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO medals (user_id, medal_name, reason, awarded_by) VALUES (?, ?, ?, ?)",
        (user_id, medal_name, reason, awarded_by),
    )
    inserted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def get_medals(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT medal_name, reason, awarded_at FROM medals WHERE user_id = ? ORDER BY awarded_at",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def has_medal(user_id, medal_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM medals WHERE user_id = ? AND medal_name = ?",
        (user_id, medal_name),
    )
    result = cur.fetchone() is not None
    conn.close()
    return result


def get_full_book(user_id):
    """Собирает звания и медали в единую хронологическую книжку."""
    ranks = [tuple(r) + ("Звание",) for r in get_ranks(user_id)]
    medals = [tuple(m) + ("Медаль",) for m in get_medals(user_id)]
    items = ranks + medals
    items.sort(key=lambda x: x[2])  # сортировка по дате awarded_at
    return items


def get_medals_by_author(user_id):
    """Сколько медалей выдал данный пользователь (для статистики админа)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM medals WHERE awarded_by = ?",
        (user_id,),
    )
    count = cur.fetchone()[0]
    conn.close()
    return count