"""
Validation and Security Utilities - FIVORA Fabric Inspection System
"""

import re
import hashlib
import secrets


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password requirements"""
    # Minimum 6 characters
    if len(password) < 6:
        return False
    return True


def hash_password(password):
    """Hash password using PBKDF2"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                    salt.encode('utf-8'), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password, hashed):
    """Verify password against hash"""
    try:
        salt, pwd_hash = hashed.split('$')
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                           salt.encode('utf-8'), 100000).hex()
        return computed_hash == pwd_hash
    except:
        return False


def generate_roll_id():
    """Generate unique roll ID"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = secrets.token_hex(3)
    return f"ROLL_{timestamp}_{random_suffix}"


def format_timestamp(timestamp):
    """Format timestamp for display"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp
