# FIVORA - Industrial Fabric Inspection System

## Overview
FIVORA is a PyQt6-based desktop application for real-time fabric inspection with defect detection, quality scoring, and comprehensive logging.

## Features
- ✅ User authentication with secure password hashing
- ✅ Real-time fabric scan simulation
- ✅ Defect detection and confidence scoring
- ✅ Quality assessment with gauge visualization
- ✅ Scan history and statistics
- ✅ SQLite database for data persistence
- ✅ Professional UI with gradient designs
- ✅ Responsive control panel

---

## Installation Steps

### 1. Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### 2. Folder Structure
Create the following folder structure in VS Code:

```
FIVORA/
├── main.py
├── requirements.txt
├── fivora_app.db (created automatically)
├── screens/
│   ├── __init__.py
│   ├── login_screen.py
│   ├── signup_screen.py
│   └── dashboard_screen.py
├── database/
│   ├── __init__.py
│   └── db_manager.py
└── utils/
    ├── __init__.py
    ├── validators.py
    └── styles.py
```

### 3. Step-by-Step Installation

#### Step 1: Clone or Download Project
Navigate to your project directory in terminal/command prompt.

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

If you encounter issues with PyQt6-Charts, try:
```bash
pip install PyQt6==6.6.1
pip install PyQt6-Charts==6.6.0 --no-binary PyQt6-Charts
```

#### Step 4: Create Folder Structure
Create the three folders: `screens`, `database`, and `utils`

#### Step 5: Copy Files
Copy the provided Python files into their respective folders according to the structure above.

**Important File Naming Convention:**
- `screens_login_screen.py` → save as `screens/login_screen.py`
- `screens_signup_screen.py` → save as `screens/signup_screen.py`
- `screens_dashboard_screen.py` → save as `screens/dashboard_screen.py`
- `database_db_manager.py` → save as `database/db_manager.py`
- `utils_validators.py` → save as `utils/validators.py`
- `utils_styles.py` → save as `utils/styles.py`
- `screens___init__.py` → save as `screens/__init__.py`
- `database___init__.py` → save as `database/__init__.py`
- `utils___init__.py` → save as `utils/__init__.py`

---

## Running the Application

### From Command Line
```bash
# Make sure virtual environment is activated
python main.py
```

### From VS Code
1. Open the integrated terminal (Ctrl + `)
2. Make sure virtual environment is activated
3. Run: `python main.py`

---

## Default Test Credentials

The application will create a sample database. You can:

1. Create a new account by clicking "Create Account" on login screen
2. Test with the following:
   - Email: test@fivora.com
   - Password: test123456

**Note:** The first user you create will be automatically registered in the database.

---

## Usage Guide

### Login Screen
1. Enter email and password
2. Click "SIGN IN" to login
3. Or click "Create Account" to register new user

### Signup Screen
1. Fill in Full Name, Email, Password, and Confirm Password
2. Check "I agree to Terms & Privacy Policy"
3. Click "CREATE ACCOUNT"
4. You will be redirected to login screen

### Dashboard Screen
1. **Start Scan**: Click "START SCAN" button to simulate fabric scanning
2. **Monitor Progress**: Watch the progress bar and real-time metrics
3. **Review Results**: Check defect count, confidence, and quality score
4. **Action**: Click "ACCEPT ROLL" or "REJECT ROLL"
5. **Logout**: Click logout button to return to login screen

---

## File Descriptions

### Core Files

#### `main.py`
- Main application entry point
- Manages screen navigation
- Handles application lifecycle

#### `screens/login_screen.py`
- User authentication UI
- Email and password validation
- Signal emission for successful login

#### `screens/signup_screen.py`
- Account creation UI
- Form validation for email, password
- Password confirmation
- Terms acceptance checkbox

#### `screens/dashboard_screen.py`
- Main inspection dashboard
- Real-time scan simulation
- Quality gauge display
- Accept/Reject controls
- Progress tracking

#### `database/db_manager.py`
- SQLite database operations
- User management
- Scan logging
- Defect tracking
- Statistics calculation

#### `utils/validators.py`
- Email validation (regex)
- Password validation
- PBKDF2 password hashing
- Password verification
- Roll ID generation
- Timestamp formatting

#### `utils/styles.py`
- Global stylesheet
- Color definitions
- Font styles
- UI component styling

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

### Scan Logs Table
```sql
CREATE TABLE scan_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    roll_id TEXT NOT NULL,
    scan_date TIMESTAMP,
    defects_count INTEGER,
    confidence REAL,
    quality_score INTEGER,
    status TEXT,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Defect Logs Table
```sql
CREATE TABLE defect_logs (
    id INTEGER PRIMARY KEY,
    scan_id INTEGER NOT NULL,
    defect_type TEXT,
    location_x REAL,
    location_y REAL,
    severity TEXT,
    FOREIGN KEY (scan_id) REFERENCES scan_logs(id)
)
```

---

## Configuration

### Change Application Title
**File:** `main.py` (line 15)
```python
self.setWindowTitle("YOUR TITLE HERE")
```

### Change Window Size
**File:** `main.py` (line 16)
```python
self.setGeometry(100, 100, WIDTH, HEIGHT)
```

### Change Primary Color
**File:** `utils/styles.py` (line 53)
```python
'primary': '#0066cc',  # Change to your color
```

---

## Troubleshooting

### Issue: ImportError: No module named 'screens'
**Solution:** Ensure all `__init__.py` files exist in subfolders

### Issue: "PyQt6 not found"
**Solution:** 
```bash
pip install PyQt6==6.6.1 PyQt6-Charts==6.6.0
```

### Issue: Database locked error
**Solution:** Delete `fivora_app.db` and restart

### Issue: UI elements not displaying correctly
**Solution:** Update PyQt6:
```bash
pip install --upgrade PyQt6 PyQt6-Charts
```

---

## Next Steps

1. **Customize the UI** - Modify colors in `utils/styles.py`
2. **Add your ML model** - Replace mock scanning with real predictions
3. **Expand database** - Add more fields to track additional data
4. **Create reports** - Add report generation functionality
5. **Add export** - Export scan results to CSV/PDF

---

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review code comments for API details
3. Check database schema for data structure
