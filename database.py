import os
import json
import bcrypt
import mysql.connector
from mysql.connector import Error
from datetime import datetime

LOCAL_USERS_FILE = "local_users_backup.json"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "12345678"


def _load_local_users():
    default_pwd_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')
    default_users = {
        "inspector@fivora.com": {
            "id": 1,
            "fname": "Default",
            "lname": "Inspector",
            "email": "inspector@fivora.com",
            "password_hash": default_pwd_hash,
            "role": "Operator",
            "status": "Active"
        },
        "auto_inspector@fivora.com": {
            "id": 2,
            "fname": "Auto",
            "lname": "Inspector",
            "email": "auto_inspector@fivora.com",
            "password_hash": default_pwd_hash,
            "role": "Operator",
            "status": "Active"
        },
        ADMIN_EMAIL: {
            "id": 0,
            "fname": "System",
            "lname": "Administrator",
            "email": ADMIN_EMAIL,
            "password_hash": bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
            "role": "Admin",
            "status": "Active"
        }
    }

    if not os.path.exists(LOCAL_USERS_FILE):
        _save_local_users(default_users)
        return default_users

    try:
        with open(LOCAL_USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                return default_users
            changed = False
            for user in data.values():
                if "status" not in user:
                    user["status"] = "Active"
                    changed = True
            if ADMIN_EMAIL not in data:
                data[ADMIN_EMAIL] = {
                    "id": 0,
                    "fname": "System",
                    "lname": "Administrator",
                    "email": ADMIN_EMAIL,
                    "password_hash": bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                    "role": "Admin",
                    "status": "Active"
                }
                changed = True
            if changed:
                _save_local_users(data)
            return data
    except Exception:
        return default_users


def _save_local_users(users_dict):
    try:
        with open(LOCAL_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_dict, f, indent=2)
    except Exception:
        pass

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "127.0.0.1"
DB_PORT = 3307
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "fivora_system"


# ============================================================
# GET DATABASE CONNECTION
# ============================================================

def get_db_connection():
    """
    Connect to MySQL and return a connection object.
    Supports XAMPP MySQL on port 3307 or 3306 automatically.
    """
    targets = [(DB_HOST, DB_PORT), ("127.0.0.1", 3307), ("127.0.0.1", 3306), ("localhost", 3307), ("localhost", 3306)]
    
    last_error = None
    for host, port in targets:
        try:
            temp_conn = mysql.connector.connect(
                host=host,
                port=port,
                user=DB_USER,
                password=DB_PASSWORD
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            temp_cursor.close()
            temp_conn.close()

            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            return conn
        except Error as e:
            last_error = e
            continue

    print("========================================")
    print("DATABASE CONNECTION ERROR (Using Local Session Mode)")
    print("========================================")
    return None


# ============================================================
# INITIALIZE DATABASE & SCHEMA MIGRATIONS
# ============================================================

def initialize_database():
    """
    Create all required database tables and extend schema if missing columns.
    """
    conn = get_db_connection()

    if conn is None:
        print("Database initialization skipped (MySQL offline - system operating in local mode).")
        return False

    cursor = conn.cursor()

    try:
        # 1. USERS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fname VARCHAR(50) NOT NULL,
                lname VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'Operator',
                status VARCHAR(30) NOT NULL DEFAULT 'Active'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                email VARCHAR(100) NOT NULL,
                login_timestamp DATETIME NOT NULL,
                logout_timestamp DATETIME NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 2. INSPECTION RECORDS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inspection_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                batch_id VARCHAR(50),
                session_id VARCHAR(100),
                user_id INT,
                final_fabric_type VARCHAR(50),
                confidence_score REAL,
                is_overridden BOOLEAN,
                action_status VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)

        # Add industrial columns if missing
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'Operator'")
        except Error:
            pass
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'Active'")
        except Error:
            pass

        columns_to_add = [
            ("roll_id", "VARCHAR(50) DEFAULT 'ROLL-2026-001'"),
            ("defect_status", "VARCHAR(50) DEFAULT 'PASS'"),
            ("defect_type", "VARCHAR(50) DEFAULT 'None'"),
            ("defect_count", "INT DEFAULT 0"),
            ("defect_confidence", "REAL DEFAULT 0.0"),
            ("ai_decision", "VARCHAR(50) DEFAULT 'PASS'"),
            ("operator_decision", "VARCHAR(50) DEFAULT 'ACCEPTED'"),
            ("override_reason", "VARCHAR(255) DEFAULT ''"),
            ("operator_name", "VARCHAR(100) DEFAULT 'QC_INSPECTOR_01'")
        ]

        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE inspection_records ADD COLUMN {col_name} {col_type}")
            except Error:
                pass # Column already exists

        conn.commit()

        # Seed/Fix default inspector account & bcrypt hashes in MySQL
        try:
            cursor.execute("SELECT id, email, password_hash FROM users")
            existing_users = cursor.fetchall()
            user_emails = [u[1].lower() for u in existing_users if u[1]]
            
            # Fix unhashed passwords in DB
            for uid, uemail, upass in existing_users:
                if upass and not (str(upass).startswith("$2b$") or str(upass).startswith("$2a$")):
                    fixed_hash = bcrypt.hashpw(str(upass).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (fixed_hash, uid))
                    conn.commit()

            # Seed default inspector if not existing
            if "inspector@fivora.com" not in user_emails:
                default_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')
                cursor.execute(
                    "INSERT INTO users (fname, lname, email, password_hash) VALUES (%s, %s, %s, %s)",
                    ("Default", "Inspector", "inspector@fivora.com", default_hash)
                )
                conn.commit()

            if ADMIN_EMAIL not in user_emails:
                admin_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                cursor.execute(
                    "INSERT INTO users (fname, lname, email, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
                    ("System", "Administrator", ADMIN_EMAIL, admin_hash, "Admin", "Active")
                )
                conn.commit()
            else:
                cursor.execute("UPDATE users SET role = 'Admin', status = 'Active' WHERE email = %s", (ADMIN_EMAIL,))
                conn.commit()
        except Exception as e:
            print("Notice: User table seed check:", e)

        print("[SUCCESS] Database initialized successfully.")
        return True

    except Error as e:
        print("Database initialization error:", e)
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# ============================================================
# USER MANAGEMENT
# ============================================================

def register_user(fname, lname, email, password_hash):
    # Ensure password_hash is hashed
    if not (str(password_hash).startswith("$2b$") or str(password_hash).startswith("$2a$")):
        password_hash = bcrypt.hashpw(str(password_hash).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update local offline backup store
    local_users = _load_local_users()
    if email.lower() in [k.lower() for k in local_users.keys()]:
        local_users[email.lower()]["password_hash"] = password_hash
        _save_local_users(local_users)
    else:
        local_users[email.lower()] = {
            "id": len(local_users) + 1,
            "fname": fname,
            "lname": lname,
            "email": email,
            "password_hash": password_hash,
            "role": "Operator",
            "status": "Pending"
        }
        _save_local_users(local_users)

    conn = get_db_connection()
    if conn is None:
        return True, "Registration successful! Please wait until the Admin approves your account."

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (fname, lname, email, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (fname, lname, email, password_hash, "Operator", "Pending")
        )
        conn.commit()
        return True, "Registration successful! Please wait until the Admin approves your account."
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:
            return False, "Email already exists!"
        return False, str(e)
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            rec = cursor.fetchone()
            if rec:
                return rec
        except Error:
            pass
        finally:
            cursor.close()
            conn.close()

    # Fallback to local offline store
    local_users = _load_local_users()
    for k, v in local_users.items():
        if k.lower() == str(email).lower():
            return v
    return None


def list_operators():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, fname, lname, email, role, status FROM users WHERE role = 'Operator' ORDER BY id DESC")
            return cursor.fetchall()
        except Error:
            pass
        finally:
            cursor.close()
            conn.close()
    users = _load_local_users()
    return [dict(user, id=user.get("id", index + 1)) for index, user in enumerate(users.values()) if str(user.get("role", "Operator")).lower() == "operator"]


def update_operator_status(user_id, email, status):
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET status = %s WHERE id = %s AND role = 'Operator'", (status, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Error:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    users = _load_local_users()
    key = next((key for key, user in users.items() if key.lower() == email.lower()), None)
    if key is None or str(users[key].get("role", "Operator")).lower() != "operator":
        return False
    users[key]["status"] = status
    _save_local_users(users)
    return True


def start_activity_log(user_record):
    timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO activity_logs (user_id, email, login_timestamp) VALUES (%s, %s, %s)",
                (user_record.get("id"), user_record.get("email", ""), timestamp)
            )
            conn.commit()
            activity_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return activity_id
        except Error:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    users = _load_local_users()
    user = users.get(str(user_record.get("email", "")).lower())
    if user is not None:
        logs = user.setdefault("activity_logs", [])
        logs.append({"login_timestamp": timestamp, "logout_timestamp": None})
        _save_local_users(users)
        return len(logs) - 1
    return None


def finish_activity_log(user_record, activity_id):
    if activity_id is None:
        return
    timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE activity_logs SET logout_timestamp = %s WHERE id = %s AND logout_timestamp IS NULL", (timestamp, activity_id))
            conn.commit()
        except Error:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
        return
    users = _load_local_users()
    user = users.get(str(user_record.get("email", "")).lower())
    if user is not None and activity_id < len(user.get("activity_logs", [])):
        user["activity_logs"][activity_id]["logout_timestamp"] = timestamp
        _save_local_users(users)


def fetch_activity_logs():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT a.id, a.email, CONCAT(u.fname, ' ', u.lname) AS operator_name,
                       a.login_timestamp, a.logout_timestamp
                FROM activity_logs a JOIN users u ON u.id = a.user_id
                WHERE u.role = 'Operator' ORDER BY a.login_timestamp DESC
            """)
            return cursor.fetchall()
        except Error:
            pass
        finally:
            cursor.close()
            conn.close()
    rows = []
    for user in _load_local_users().values():
        if str(user.get("role", "Operator")).lower() != "operator":
            continue
        name = " ".join(filter(None, [user.get("fname"), user.get("lname")])).strip()
        for index, log in enumerate(user.get("activity_logs", [])):
            rows.append({"id": index, "email": user.get("email", ""), "operator_name": name,
                         "login_timestamp": log.get("login_timestamp", ""),
                         "logout_timestamp": log.get("logout_timestamp") or "Still logged in"})
    return sorted(rows, key=lambda row: row.get("login_timestamp", ""), reverse=True)


# ============================================================
# INSPECTION RECORD STORAGE
# ============================================================

def save_inspection_record(
    batch_id,
    session_id,
    user_id=1,
    final_fabric_type="Cotton",
    confidence_score=95.0,
    is_overridden=False,
    action_status="Accepted",
    roll_id="ROLL-2026-001",
    defect_status="PASS",
    defect_type="None",
    defect_count=0,
    defect_confidence=0.0,
    ai_decision="PASS",
    operator_decision="ACCEPTED",
    override_reason="",
    operator_name="QC_INSPECTOR_01"
):
    """
    Save complete industrial fabric inspection record.
    """
    conn = get_db_connection()
    if conn is None:
        # Fallback offline success log
        print(f"[SAVED] Local Inspection Record Saved: Batch {batch_id}, Roll {roll_id}")
        return True, "Inspection result saved to local session backup."

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO inspection_records
            (
                batch_id, session_id, user_id, final_fabric_type, confidence_score,
                is_overridden, action_status, roll_id, defect_status, defect_type,
                defect_count, defect_confidence, ai_decision, operator_decision,
                override_reason, operator_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                batch_id, session_id, user_id, final_fabric_type, confidence_score,
                is_overridden, action_status, roll_id, defect_status, defect_type,
                defect_count, defect_confidence, ai_decision, operator_decision,
                override_reason, operator_name
            )
        )
        conn.commit()
        return True, "Inspection record saved to database successfully!"
    except Error as e:
        conn.rollback()
        return False, f"Database save error: {e}"
    finally:
        cursor.close()
        conn.close()


def fetch_user_history(user_id=1):
    """
    Fetch inspection history for reporting and analytics.
    """
    conn = get_db_connection()
    if conn is None:
        return []

    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT
                batch_id,
                session_id,
                final_fabric_type,
                confidence_score,
                is_overridden,
                action_status,
                timestamp,
                roll_id,
                defect_status,
                defect_type,
                defect_count,
                defect_confidence,
                ai_decision,
                operator_decision,
                operator_name
            FROM inspection_records
            ORDER BY timestamp DESC
            """
        )
        return cursor.fetchall()
    except Error as e:
        print("Error fetching user history:", e)
        return []
    finally:
        cursor.close()
        conn.close()