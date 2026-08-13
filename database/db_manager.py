"""
Database Manager - FIVORA Fabric Inspection System
Handles database operations and user management
"""

import sqlite3
from pathlib import Path
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path="fivora_app.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create scan logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    roll_id TEXT NOT NULL,
                    scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    defects_count INTEGER,
                    confidence REAL,
                    quality_score INTEGER,
                    status TEXT,
                    details TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # Create defect logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS defect_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER NOT NULL,
                    defect_type TEXT,
                    location_x REAL,
                    location_y REAL,
                    severity TEXT,
                    FOREIGN KEY (scan_id) REFERENCES scan_logs(id)
                )
            ''')
            
            self.connection.commit()
            
            # Create default test user if it doesn't exist
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", ("test@fivora.com",))
            if cursor.fetchone()[0] == 0:
                # Import validators here to avoid circular imports
                from utils.validators import hash_password
                hashed_pwd = hash_password("password123")
                cursor.execute(
                    "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
                    ("Test User", "test@fivora.com", hashed_pwd)
                )
                self.connection.commit()
                print("Default test user created: test@fivora.com / password123")
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
    
    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            result = cursor.fetchone()
            return result
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
    
    def create_user(self, full_name, email, hashed_password):
        """Create new user"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO users (full_name, email, password) VALUES (?, ?, ?)",
                (full_name, email, hashed_password)
            )
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return False
    
    def update_user(self, user_id, **kwargs):
        """Update user information"""
        try:
            cursor = self.connection.cursor()
            updates = []
            values = []
            for key, value in kwargs.items():
                updates.append(f"{key} = ?")
                values.append(value)
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating user: {e}")
            return False
    
    def add_scan_log(self, user_id, roll_id, defects_count, confidence, quality_score, status):
        """Add fabric scan log"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO scan_logs (user_id, roll_id, defects_count, confidence, quality_score, status) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, roll_id, defects_count, confidence, quality_score, status)
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding scan log: {e}")
            return None
    
    def get_scan_logs(self, user_id, limit=100):
        """Get scan logs for a user"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM scan_logs WHERE user_id = ? ORDER BY scan_date DESC LIMIT ?",
                (user_id, limit)
            )
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error getting scan logs: {e}")
            return []
    
    def add_defect_log(self, scan_id, defect_type, location_x, location_y, severity):
        """Add defect log"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO defect_logs (scan_id, defect_type, location_x, location_y, severity) VALUES (?, ?, ?, ?, ?)",
                (scan_id, defect_type, location_x, location_y, severity)
            )
            self.connection.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding defect log: {e}")
            return None
    
    def get_defect_logs(self, scan_id):
        """Get defect logs for a scan"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM defect_logs WHERE scan_id = ?", (scan_id,))
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"Error getting defect logs: {e}")
            return []
    
    def get_statistics(self, user_id):
        """Get user statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Total scans
            cursor.execute("SELECT COUNT(*) as count FROM scan_logs WHERE user_id = ?", (user_id,))
            total_scans = cursor.fetchone()['count']
            
            # Quality score average
            cursor.execute("SELECT AVG(quality_score) as avg FROM scan_logs WHERE user_id = ?", (user_id,))
            avg_quality = cursor.fetchone()['avg'] or 0
            
            return {
                'total_scans': total_scans,
                'avg_quality': round(avg_quality, 2)
            }
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {'total_scans': 0, 'avg_quality': 0}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
