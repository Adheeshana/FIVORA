import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        temp_conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute("CREATE DATABASE IF NOT EXISTS fivora_system")
        temp_conn.close()

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="fivora_system"
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def initialize_database():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        # Create Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fname VARCHAR(50) NOT NULL,
                lname VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            )
        """)
        
        # Create Inspection Records Table
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
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()

def register_user(fname, lname, email, password_hash):
    conn = get_db_connection()
    if conn is None: return False, "Database connection failed"
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (fname, lname, email, password_hash) VALUES (%s, %s, %s, %s)",
            (fname, lname, email, password_hash)
        )
        conn.commit()
        return True, "Success"
    except mysql.connector.IntegrityError:
        return False, "Email already exists!"
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    if conn is None: return None
    
    cursor = conn.cursor(dictionary=True) # Returns results as a dictionary
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_inspection_record(batch_id, session_id, user_id, final_fabric_type, confidence_score, is_overridden, action_status):
    conn = get_db_connection()
    if conn is None: return False, "Database connection failed"
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO inspection_records 
            (batch_id, session_id, user_id, final_fabric_type, confidence_score, is_overridden, action_status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (batch_id, session_id, user_id, final_fabric_type, confidence_score, is_overridden, action_status))
        conn.commit()
        return True, "Success"
    except Error as e:
        return False, str(e)
    finally:
        conn.close()

def fetch_user_history(user_id):
    conn = get_db_connection()
    if conn is None: return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT batch_id, session_id, final_fabric_type, confidence_score, is_overridden, action_status, timestamp 
        FROM inspection_records 
        WHERE user_id = %s 
        ORDER BY timestamp DESC
    """, (user_id,))
    
    records = cursor.fetchall()
    conn.close()
    return records