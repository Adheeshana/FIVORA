# FIVORA Quick Start Guide - 5 Minutes Setup

## ⚡ Fastest Way to Get Running

### 1. Copy All Files
Copy the files in the exact folder structure shown below:

```
YourProjectFolder/
├── main.py
├── requirements.txt
├── SETUP_GUIDE.md
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

### 2. Install Python (if not already installed)
- Download from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

### 3. Open Terminal/Command Prompt
- Windows: Press `Win + R`, type `cmd`
- macOS: Press `Cmd + Space`, search for `Terminal`
- Linux: Open terminal application

### 4. Navigate to Your Project Folder
```bash
cd path/to/YourProjectFolder
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Application
```bash
python main.py
```

---

## 📝 Creating an Account

1. Click **"Create Account"** button
2. Fill in:
   - Full Name: Your name
   - Email: Your email
   - Password: At least 6 characters
   - Confirm Password: same as above
3. Check the checkbox for Terms & Privacy
4. Click **"CREATE ACCOUNT"**

---

## 🔐 Logging In

1. Enter your email
2. Enter your password
3. Click **"SIGN IN"**

---

## 🔍 Using the Dashboard

### Start Scanning
1. Click **"▶ START SCAN"** button
2. Watch the progress bar fill up
3. Monitor these metrics:
   - **Defects**: Number of fabric defects found
   - **Confidence**: Accuracy of detection
   - **Quality Score**: Overall quality (0-100)

### Accept or Reject Roll
After scan completes:
- Click **"✓ ACCEPT ROLL"** to accept the fabric roll
- Click **"✕ REJECT ROLL"** to reject the fabric roll

---

## ⚙️ File Renaming Cheat Sheet

If you're confused about file names, here's what to do:

| Given Filename | Rename To | Folder |
|---|---|---|
| `screens_login_screen.py` | `login_screen.py` | `screens/` |
| `screens_signup_screen.py` | `signup_screen.py` | `screens/` |
| `screens_dashboard_screen.py` | `dashboard_screen.py` | `screens/` |
| `screens___init__.py` | `__init__.py` | `screens/` |
| `database_db_manager.py` | `db_manager.py` | `database/` |
| `database___init__.py` | `__init__.py` | `database/` |
| `utils_validators.py` | `validators.py` | `utils/` |
| `utils_styles.py` | `styles.py` | `utils/` |
| `utils___init__.py` | `__init__.py` | `utils/` |

---

## 🆘 Common Issues

### "Module not found" Error
**Fix:** Make sure all folders exist and have `__init__.py` files

### "PyQt6 not installed" Error
**Fix:** Run this:
```bash
pip install PyQt6==6.6.1 PyQt6-Charts==6.6.0
```

### Application won't start
**Fix:** Delete `fivora_app.db` file and try again

### Can't login after signup
**Fix:** Make sure you spelled email and password correctly

---

## 📚 Next Steps

1. **Read SETUP_GUIDE.md** for detailed information
2. **Customize colors** in `utils/styles.py`
3. **Add your ML model** to replace the simulation
4. **Expand features** like reports, history, etc.

---

## 🎯 Test Scenario

Try this flow to test the app:

1. Click "Create Account"
   - Name: Test User
   - Email: test@fivora.com
   - Password: test123456
   - Agree to terms

2. Click "Sign In"
   - Use test@fivora.com / test123456

3. On Dashboard:
   - Click "START SCAN"
   - Watch progress for ~3 seconds
   - Click "ACCEPT ROLL"

4. Click "Logout" to return to login

---

## 🚀 Ready to Add ML Model?

When you have your fabric detection model ready:

1. Open `screens/dashboard_screen.py`
2. Find the `update_scan_progress()` method
3. Replace the `random.randint()` calls with your model's predictions
4. Update the metrics with actual results

---

## 💡 Pro Tips

- Use **light theme** for better visibility during fabric inspection
- **Save frequently** when modifying code
- Keep a **backup** of your database file
