import re
import bcrypt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from database import register_user

class SignupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.brand = QLabel("Fivora")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.sub_brand = QLabel("INDUSTRIAL FABRIC INSPECTION SYSTEM")
        self.sub_brand.setStyleSheet("font-size: 10px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")
        self.sub_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_title = QLabel("Create Account")
        self.page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.brand)
        main_layout.addWidget(self.sub_brand)
        main_layout.addWidget(self.page_title)

        self.card = QFrame()
        self.card.setFixedWidth(460)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        name_layout = QHBoxLayout()
        self.lbl_name = QLabel("YOUR NAME")
        self.lbl_name.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none;")
        
        self.fname = QLineEdit()
        self.fname.setPlaceholderText("First Name")
        self.lname = QLineEdit()
        self.lname.setPlaceholderText("Last Name")
        name_layout.addWidget(self.fname)
        name_layout.addWidget(self.lname)

        self.lbl_email = QLabel("EMAIL ADDRESS")
        self.lbl_email.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none;")
        self.email = QLineEdit()
        self.email.setPlaceholderText("inspector@fivora.com")

        self.lbl_pwd = QLabel("PASSWORD")
        self.lbl_pwd.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none;")
        self.password = QLineEdit()
        self.password.setPlaceholderText("••••••••")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.lbl_cpwd = QLabel("CONFIRM PASSWORD")
        self.lbl_cpwd.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("••••••••")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.terms_checkbox = QCheckBox("I agree to the Terms & Privacy Policy")

        self.btn_signup = QPushButton("CREATE ACCOUNT")
        self.btn_signup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signup.clicked.connect(self.on_signup_clicked)

        card_layout.addWidget(self.lbl_name)
        card_layout.addLayout(name_layout)
        card_layout.addWidget(self.lbl_email)
        card_layout.addWidget(self.email)
        card_layout.addWidget(self.lbl_pwd)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.lbl_cpwd)
        card_layout.addWidget(self.confirm_password)
        card_layout.addWidget(self.terms_checkbox)
        card_layout.addWidget(self.btn_signup)
        
        main_layout.addWidget(self.card)
        self.apply_theme(True)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19;")
            self.brand.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-top: 15px; margin-bottom: 20px;")
            self.card.setStyleSheet("QFrame { background-color: #111827; border-radius: 12px; border: 1px solid #1e293b; }")
            input_style = "QLineEdit { padding: 12px; background: #1e293b; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }"
            self.fname.setStyleSheet(input_style)
            self.lname.setStyleSheet(input_style)
            self.email.setStyleSheet(input_style)
            self.password.setStyleSheet(input_style)
            self.confirm_password.setStyleSheet(input_style)
            self.terms_checkbox.setStyleSheet("color: #94a3b8; font-size: 12px; border: none;")
            self.btn_signup.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 14px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; margin-top: 10px; } QPushButton:hover { background-color: #0284c7; }")
        else:
            self.setStyleSheet("background-color: #f4f6f9;")
            self.brand.setStyleSheet("font-size: 32px; font-weight: bold; color: #0f172a;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 15px; margin-bottom: 20px;")
            self.card.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }")
            input_style = "QLineEdit { padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #0f172a; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }"
            self.fname.setStyleSheet(input_style)
            self.lname.setStyleSheet(input_style)
            self.email.setStyleSheet(input_style)
            self.password.setStyleSheet(input_style)
            self.confirm_password.setStyleSheet(input_style)
            self.terms_checkbox.setStyleSheet("color: #475569; font-size: 12px; border: none;")
            self.btn_signup.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 14px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; margin-top: 10px; } QPushButton:hover { background-color: #0284c7; }")

    def clear_fields(self):
        self.fname.clear()
        self.lname.clear()
        self.email.clear()
        self.password.clear()
        self.confirm_password.clear()
        self.terms_checkbox.setChecked(False)

    def on_signup_clicked(self):
        fname = self.fname.text().strip()
        lname = self.lname.text().strip()
        email = self.email.text().strip()
        pwd = self.password.text().strip()
        cpwd = self.confirm_password.text().strip()

        # 1. Check if all fields are filled
        if not all([fname, lname, email, pwd, cpwd]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        # 2. Email Validation (Regex)
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address! \n(e.g., inspector@fivora.com)")
            return

        # 3. Password Length Validation
        if len(pwd) < 8:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 8 characters long!")
            return

        # 4. Check if passwords match
        if pwd != cpwd:
            QMessageBox.warning(self, "Error", "Passwords do not match!")
            return

        # 5. Check if terms are accepted
        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "Error", "Please agree to the Terms & Privacy Policy.")
            return

        # Hash the password and save to database
        hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        success, msg = register_user(fname, lname, email, hashed_pwd)

        if success:
            QMessageBox.information(self, "Success", "Account created! Please Sign In.")
            self.parent.switch_page(0)
        else:
            QMessageBox.critical(self, "Error", msg)