import sqlite3
from datetime import datetime

# Создаём базу данных и таблицу
def init_db():
    conn = sqlite3.connect('signals.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS active_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            direction TEXT NOT NULL,
            entry_price REAL NOT NULL,
            sl REAL NOT NULL,
            tp REAL NOT NULL,
            leverage INTEGER NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Добавить новый сигнал
def add_signal(symbol, direction, entry_price, sl, tp, leverage):
    conn = sqlite3.connect('signals.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO active_signals 
        (symbol, direction, entry_price, sl, tp, leverage)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (symbol, direction, entry_price, sl, tp, leverage))
    conn.commit()
    signal_id = c.lastrowid
    conn.close()
    return signal_id

# Получить все активные сигналы
def get_active_signals():
    conn = sqlite3.connect('signals.db')
    c = conn.cursor()
    c.execute("SELECT id, symbol, direction, entry_price, sl, tp, leverage FROM active_signals WHERE status = 'ACTIVE'")
    rows = c.fetchall()
    conn.close()
    return rows

# Закрыть сигнал (например, по SL или TP)
def close_signal(signal_id, reason):
    conn = sqlite3.connect('signals.db')
    c = conn.cursor()
    c.execute("UPDATE active_signals SET status = ? WHERE id = ?", (reason, signal_id))
    conn.commit()
    conn.close()

# Создаём базу сразу при первом запуске
init_db()