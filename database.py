import sqlite3
import os
from datetime import datetime

DB_FILE = "fivora_system.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database Connection Error: {e}")
        return None

def initialize_database():
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Added batch_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inspection_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                final_fabric_type TEXT NOT NULL,
                confidence_score REAL,
                is_overridden BOOLEAN NOT NULL,
                action_status TEXT NOT NULL, 
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Initialization Error: {e}")
    finally:
        conn.close()

def register_user(first_name, last_name, email, password_hash):
    conn = get_connection()
    if not conn: return False, "Database connection failed."
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?)",
                       (first_name, last_name, email, password_hash))
        conn.commit()
        return True, "Registration successful."
    except sqlite3.IntegrityError:
        return False, "Email address already exists."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    if not conn: return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()
    finally:
        conn.close()

def save_inspection_record(batch_id, session_id, user_id, final_fabric_type, confidence_score, is_overridden, action_status="Pending"):
    conn = get_connection()
    if not conn: return False, "Database connection failed."
    try:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """INSERT INTO inspection_records 
               (batch_id, session_id, user_id, final_fabric_type, confidence_score, is_overridden, action_status, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (batch_id, session_id, user_id, final_fabric_type, confidence_score, int(is_overridden), action_status, timestamp)
        )
        conn.commit()
        return True, "Saved successfully."
    except sqlite3.Error as e:
        return False, f"Failed to save: {e}"
    finally:
        conn.close()

def fetch_user_history(user_id):
    conn = get_connection()
    if not conn: return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT batch_id, session_id, final_fabric_type, confidence_score, is_overridden, action_status, timestamp FROM inspection_records WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()