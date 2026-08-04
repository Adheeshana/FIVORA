import mysql.connector
from mysql.connector import Error

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',         # Put your MySQL password here if any
    'database': 'fivora_db' # Ensure this database exists in your MySQL server
}

def get_db_connection():
    """
    Returns a connection to the MySQL database.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Database Connection Error: {e}")
        return None
    return None

def initialize_database():
    """
    Connects to MySQL server, creates the 'fivora_db' database if it doesn't exist,
    and initializes all 5 tables according to Section 4.6 of the SDS.
    """
    try:
        # First connect without specifying database to create it if missing
        initial_conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = initial_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']};")
        cursor.close()
        initial_conn.close()

        # Now connect to the specific database
        conn = get_db_connection()
        if conn is None:
            return

        cursor = conn.cursor()

        # 1. USER Table Definition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USER (
                User_Id INT AUTO_INCREMENT PRIMARY KEY,
                First_Name VARCHAR(50) NOT NULL,
                Last_Name VARCHAR(50) NOT NULL,
                Email VARCHAR(100) UNIQUE NOT NULL,
                Password VARCHAR(255) NOT NULL
            );
        ''')

        # 2. IMAGE Table Definition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS IMAGE (
                Image_Id INT AUTO_INCREMENT PRIMARY KEY,
                Image_source TEXT NOT NULL,
                Fabric_Type VARCHAR(50),
                Validate_Date DATE DEFAULT (CURRENT_DATE),
                Validate_time TIME DEFAULT (CURRENT_TIME),
                Resolution VARCHAR(20),
                User_Id INT,
                FOREIGN KEY (User_Id) REFERENCES USER(User_Id)
            );
        ''')

        # 3. DEFECT Table Definition (Weak Entity with ON DELETE CASCADE)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DEFECT (
                Defect_Id INT AUTO_INCREMENT PRIMARY KEY,
                Defect_Type VARCHAR(50),
                X_coordinate FLOAT,
                Y_coordinate FLOAT,
                Confidence_score FLOAT,
                Defect_Count INT,
                Image_Id INT,
                FOREIGN KEY (Image_Id) REFERENCES IMAGE(Image_Id) ON DELETE CASCADE
            );
        ''')

        # 4. ANALYSIS Table Definition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ANALYSIS (
                Analyzed_Id INT AUTO_INCREMENT PRIMARY KEY,
                Analyzed_date DATE DEFAULT (CURRENT_DATE),
                Analyzed_Time TIME DEFAULT (CURRENT_TIME),
                Image_Id INT,
                FOREIGN KEY (Image_Id) REFERENCES IMAGE(Image_Id)
            );
        ''')

        # 5. REPORT Table Definition
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS REPORT (
                Report_Id INT AUTO_INCREMENT PRIMARY KEY,
                Report_Format VARCHAR(10),
                Create_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                User_Id INT,
                Image_Id INT,
                Analyzed_Id INT,
                FOREIGN KEY (User_Id) REFERENCES USER(User_Id),
                FOREIGN KEY (Image_Id) REFERENCES IMAGE(Image_Id),
                FOREIGN KEY (Analyzed_Id) REFERENCES ANALYSIS(Analyzed_Id)
            );
        ''')

        conn.commit()
        print("MySQL Database and Tables initialized successfully based on SDS Section 4.6!")

    except Error as e:
        print(f"Database Initialization Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def is_email_registered(email):
    """
    Checks if the provided email already exists in the USER table.
    Implements FR 03: Check Email Uniqueness (Using MySQL %s placeholder).
    """
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Email FROM USER WHERE Email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    return False