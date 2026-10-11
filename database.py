import os
import json
import bcrypt
import mysql.connector
from mysql.connector import Error
from datetime import datetime

LOCAL_USERS_FILE = "local_users_backup.json"
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "12345678"

# ============================================================
# GET DATABASE CONNECTION (Clever Cloud MySQL)
# ============================================================

def get_db_connection():
    """
    Connect to Clever Cloud MySQL Database securely.
    """
    try:
        conn = mysql.connector.connect(
            host="bkdyxookic8ufpl13ica-mysql.services.clever-cloud.com",
            user="uomjytfwprogp0uh",
            password="rV3js5AbiA5iag2Psqda",
            database="bkdyxookic8ufpl13ica",
            port=3306,
            use_pure=True  
        )
        return conn
    except Error as e:
        print("========================================")
        print("DATABASE CONNECTION ERROR:", e)
        print("========================================")
        return None

def get_all_users():
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, fname, lname, email, role, status FROM users")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_user_status(user_id, status):
    conn = get_db_connection()
    if conn is None: return False
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET status = %s WHERE id = %s", (status, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_session_logs():
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.fname, u.lname, u.email, a.login_timestamp, a.logout_timestamp 
            FROM activity_logs a 
            JOIN users u ON a.user_id = u.id
            ORDER BY a.id DESC
        """)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

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
            return json.load(f)
    except Exception:
        return default_users

def _save_local_users(users_dict):
    try:
        with open(LOCAL_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_dict, f, indent=2)
    except Exception:
        pass


# ============================================================
# INITIALIZE DATABASE & SCHEMA MIGRATIONS
# ============================================================

def initialize_database():
    """
    Create all required database tables in Clever Cloud.
    """
    conn = get_db_connection()
    if conn is None:
        print("Database initialization failed (Cloud offline).")
        return False

    cursor = conn.cursor()

    try:
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
                roll_id VARCHAR(50) DEFAULT 'ROLL-2026-001',
                defect_status VARCHAR(50) DEFAULT 'PASS',
                defect_type VARCHAR(50) DEFAULT 'None',
                defect_count INT DEFAULT 0,
                defect_confidence REAL DEFAULT 0.0,
                ai_decision VARCHAR(50) DEFAULT 'PASS',
                operator_decision VARCHAR(50) DEFAULT 'ACCEPTED',
                override_reason VARCHAR(255) DEFAULT '',
                operator_name VARCHAR(100) DEFAULT 'QC_INSPECTOR_01',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)

        conn.commit()

        # Seed default admin and inspector accounts if not existing
        cursor.execute("SELECT email FROM users")
        existing_emails = [row[0].lower() for row in cursor.fetchall() if row[0]]

        if "inspector@fivora.com" not in existing_emails:
            default_hash = bcrypt.hashpw(b"Password123!", bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO users (fname, lname, email, password_hash) VALUES (%s, %s, %s, %s)",
                ("Default", "Inspector", "inspector@fivora.com", default_hash)
            )
            conn.commit()

        if ADMIN_EMAIL not in existing_emails:
            admin_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cursor.execute(
                "INSERT INTO users (fname, lname, email, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, %s)",
                ("System", "Administrator", ADMIN_EMAIL, admin_hash, "Admin", "Active")
            )
            conn.commit()

        print("[SUCCESS] Cloud Database initialized successfully.")
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
    if not (str(password_hash).startswith("$2b$") or str(password_hash).startswith("$2a$")):
        password_hash = bcrypt.hashpw(str(password_hash).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    if conn is None:
        return False, "Cloud database connection failed."

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
    return []


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
    return False


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
            return activity_id
        except Error:
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
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
    return []


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
    conn = get_db_connection()
    if conn is None:
        return False, "Cloud database connection failed."

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
        return True, "Inspection record saved to cloud database successfully!"
    except Error as e:
        conn.rollback()
        return False, f"Database save error: {e}"
    finally:
        cursor.close()
        conn.close()


def fetch_user_history(user_id=1):
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