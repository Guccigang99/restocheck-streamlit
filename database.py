
import sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path("restocheck.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            address TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS crew (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birthdate TEXT NOT NULL,
            status TEXT NOT NULL,
            contract_hours REAL,
            function TEXT,
            department TEXT,
            notes TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        )
    """)

    conn.commit()
    conn.close()

def add_restaurant(name, address="", active=True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO restaurants (name, address, active) VALUES (?, ?, ?)",
        (name.strip(), address.strip(), 1 if active else 0),
    )
    conn.commit()
    conn.close()

def update_restaurant(restaurant_id, name, address="", active=True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE restaurants SET name=?, address=?, active=? WHERE id=?",
        (name.strip(), address.strip(), 1 if active else 0, restaurant_id),
    )
    conn.commit()
    conn.close()

def delete_restaurant(restaurant_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM crew WHERE restaurant_id=?", (restaurant_id,))
    cur.execute("DELETE FROM restaurants WHERE id=?", (restaurant_id,))
    conn.commit()
    conn.close()

def get_restaurants():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, address, active FROM restaurants ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_restaurant(restaurant_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, address, active FROM restaurants WHERE id=?", (restaurant_id,))
    row = cur.fetchone()
    conn.close()
    return row

def add_crew(restaurant_id, first_name, last_name, birthdate, status, contract_hours,
             function, department, notes, active=True):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO crew (
            restaurant_id, first_name, last_name, birthdate, status,
            contract_hours, function, department, notes, active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        restaurant_id, first_name.strip(), last_name.strip(), birthdate, status,
        contract_hours, function.strip(), department.strip(), notes.strip(),
        1 if active else 0,
    ))
    conn.commit()
    conn.close()

def get_crew(restaurant_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, last_name, birthdate, status, contract_hours,
               function, department, notes, active
        FROM crew
        WHERE restaurant_id=?
        ORDER BY last_name, first_name
    """, (restaurant_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_crew(crew_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM crew WHERE id=?", (crew_id,))
    conn.commit()
    conn.close()

def calculate_age(birthdate_text, today=None):
    if today is None:
        today = date.today()
    birth = date.fromisoformat(birthdate_text)
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
