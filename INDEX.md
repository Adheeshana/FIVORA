# FIVORA - Complete Index & Quick Reference

## 📚 Documentation Index

### Getting Started (Pick One)
1. **⚡ QUICK_START.md** - Start here! 5-minute setup
2. **📖 SETUP_GUIDE.md** - Detailed step-by-step guide
3. **📋 FILE_CHECKLIST.md** - File organization guide

### Advanced Topics
1. **🤖 ML_INTEGRATION_GUIDE.md** - Add your own ML model
2. **INDEX.md** - This file (quick reference)

---

## 🚀 Express Setup (Copy-Paste Ready)

### Windows Command Prompt
```bash
cd path\to\FIVORA
pip install -r requirements.txt
python main.py
```

### macOS/Linux Terminal
```bash
cd path/to/FIVORA
pip install -r requirements.txt
python main.py
```

---

## 📂 File Organization Reference

### What Gets Renamed?

| From | To | Folder |
|------|----|----|
| `main.py` | `main.py` | Root |
| `requirements.txt` | `requirements.txt` | Root |
| `screens_*.py` | `*.py` | `screens/` |
| `database_*.py` | `*.py` | `database/` |
| `utils_*.py` | `*.py` | `utils/` |
| `*___init__.py` | `__init__.py` | Respective |

### Quick Copy-Paste Template

```
C:\FIVORA\
├─ main.py
├─ requirements.txt
├─ screens/
│  ├─ __init__.py
│  ├─ login_screen.py
│  ├─ signup_screen.py
│  └─ dashboard_screen.py
├─ database/
│  ├─ __init__.py
│  └─ db_manager.py
└─ utils/
   ├─ __init__.py
   ├─ validators.py
   └─ styles.py
```

---

## 💻 System Requirements

### Minimum
- Python 3.9+
- 500MB disk space
- 2GB RAM

### Recommended
- Python 3.10+
- 1GB disk space
- 4GB RAM

### Supported Operating Systems
- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+)

---

## 🔑 Default Test Account

After first signup, you can test with:
- **Email:** test@fivora.com
- **Password:** test123456

---

## 🎮 Basic Usage Flow

```
1. Run Application
   ↓
2. Click "Create Account"
   ↓
3. Fill Form & Click "Create"
   ↓
4. Login with Credentials
   ↓
5. Click "Start Scan"
   ↓
6. Watch Progress
   ↓
7. Click "Accept Roll" or "Reject Roll"
   ↓
8. Click "Logout"
```

---

## 🔍 Feature Checklist

### Authentication
- [x] User signup
- [x] User login
- [x] Password hashing
- [x] Form validation
- [x] Logout

### Dashboard
- [x] Real-time scan simulation
- [x] Defect detection display
- [x] Confidence percentage
- [x] Quality score gauge
- [x] Accept/Reject functionality
- [x] Progress bar

### Data Management
- [x] SQLite database
- [x] User persistence
- [x] Scan logging
- [x] Defect logging
- [x] Statistics tracking

### UI/UX
- [x] Professional styling
- [x] Gradient backgrounds
- [x] Responsive layout
- [x] Button interactions
- [x] Form validation

---

## 🔧 Configuration Quick Reference

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

### Change Scan Parameters
**File:** `screens/dashboard_screen.py` (line 280-290)
```python
defects = random.randint(MIN, MAX)  # Change range
confidence = random.randint(MIN, MAX)
quality_score = random.randint(MIN, MAX)
```

---

## 🐛 Common Issues & Quick Fixes

### "Module not found" error
```bash
# Solution: Ensure all __init__.py files exist in folders
# Run this command to create them:

# Windows
type nul > screens\__init__.py
type nul > database\__init__.py
type nul > utils\__init__.py

# macOS/Linux
touch screens/__init__.py
touch database/__init__.py
touch utils/__init__.py
```

### "PyQt6 not installed" error
```bash
pip install PyQt6==6.6.1 PyQt6-Charts==6.6.0 --upgrade
```

### Database locked error
```bash
# Solution: Delete the database file and restart
# Windows
del fivora_app.db

# macOS/Linux
rm fivora_app.db

# Then run: python main.py
```

### UI elements misaligned
```bash
# Solution: Update PyQt6 to latest version
pip install --upgrade PyQt6 PyQt6-Charts
```

---

## 📊 Architecture Overview

---

## 🚀 Deployment Steps

---

## 📞 Getting Help

1. **Check documentation** - Read relevant .md file
2. **Check code comments** - Each file has detailed comments
3. **Check error messages** - Suggests solution
4. **Common issues page** - See troubleshooting section

---

## 🎯 Next Steps

### Beginner
- [ ] Run the application
- [ ] Create a test account
- [ ] Explore the dashboard
- [ ] Read QUICK_START.md

### Intermediate
- [ ] Customize colors in styles.py
- [ ] Add your own database fields
- [ ] Create additional UI screens
- [ ] Read SETUP_GUIDE.md

### Advanced
- [ ] Integrate your ML model
- [ ] Add export functionality
- [ ] Create reporting system
- [ ] Implement real-time scanning
- [ ] Read ML_INTEGRATION_GUIDE.md

---

✅ **All Setup Complete!** Ready to run FIVORA!
