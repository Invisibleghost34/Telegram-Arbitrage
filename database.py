import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("polymarket.db")
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS markets (
            id TEXT PRIMARY KEY,
            question TEXT,
            category TEXT,
            clob_token_yes TEXT,
            clob_token_no TEXT
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT,
            timestamp TEXT,
            yes_ask REAL,
            no_ask REAL,
            total REAL,
            spread REAL,
            arb_detected INTEGER
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            market_id TEXT,
            timestamp TEXT,
            yes_shares INTEGER,
            no_shares INTEGER,
            yes_price REAL,
            no_price REAL,
            cost REAL,
            expected_profit REAL
        );
    """)
    conn.commit()
    return conn

def insert_market(conn, market):
    cursor = conn.cursor()
    events = market.get("events", [])
    category = events[0].get("slug", "unknown") if events else "unknown"
    tokens = market.get("clobTokenIds", [])
    yes_token = tokens[0] if len(tokens) > 0 else None
    no_token = tokens[1] if len(tokens) > 1 else None
    cursor.execute("""
        INSERT OR IGNORE INTO markets (id, question, category, clob_token_yes, clob_token_no)
        VALUES (?, ?, ?, ?, ?)
    """, (market["id"], market["question"], category, yes_token, no_token))
    conn.commit()

def insert_snapshot(conn, market_id, yes_ask, no_ask):
    cursor = conn.cursor()
    total = yes_ask + no_ask
    spread = 1 - total
    arb_detected = 1 if total < 0.99 else 0
    cursor.execute("""
        INSERT INTO snapshots (market_id, timestamp, yes_ask, no_ask, total, spread, arb_detected)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (market_id, datetime.now().isoformat(), yes_ask, no_ask, total, spread, arb_detected))
    conn.commit()

def insert_trade(conn, market_id, yes_shares, no_shares, yes_price, no_price, cost, expected_profit):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trades (market_id, timestamp, yes_shares, no_shares, yes_price, no_price, cost, expected_profit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (market_id, datetime.now().isoformat(), yes_shares, no_shares, yes_price, no_price, cost, expected_profit))
    conn.commit()