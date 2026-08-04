"""
Signup View & Controller: Handles User Registration and Validations (FR 01, 02, 03, 04).
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFrame, QCheckBox, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from database import get_db_connection, is_email_registered
from validator import Validator

class SignupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header Titles (FR 01 - Display Sign Up Form)
        brand = QLabel("Fivora")
        brand.setStyleSheet("font-size: 32px; font-weight: bold; color: #0f172a;")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_brand = QLabel("INDUSTRIAL FABRIC INSPECTION SYSTEM")
        sub_brand.setStyleSheet("font-size: 10px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")
        sub_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        page_title = QLabel("Create Account")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 15px; margin-bottom: 20px;")
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(brand)
        main_layout.addWidget(sub_brand)
        main_layout.addWidget(page_title)

        # Form Card
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(12)

        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none; margin-top: 5px;")
            return lbl

        def create_input(placeholder, is_password=False):
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            if is_password:
                inp.setEchoMode(QLineEdit.EchoMode.Password)
            inp.setStyleSheet("QLineEdit { padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #0f172a; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }")
            return inp

        self.fullname = create_input("Sahan Perera")
        self.email = create_input("inspector@fivora.com")
        self.password = create_input("••••••••", is_password=True)
        self.confirm_password = create_input("••••••••", is_password=True)

        card_layout.addWidget(create_label("FULL NAME"))
        card_layout.addWidget(self.fullname)
        card_layout.addWidget(create_label("EMAIL ADDRESS"))
        card_layout.addWidget(self.email)
        card_layout.addWidget(create_label("PASSWORD"))
        card_layout.addWidget(self.password)
        card_layout.addWidget(create_label("CONFIRM PASSWORD"))
        card_layout.addWidget(self.confirm_password)

        self.terms = QCheckBox("I agree to the Terms & Privacy Policy")
        self.terms.setStyleSheet("QCheckBox { color: #64748b; font-size: 12px; border: none; margin-top: 8px; }")
        card_layout.addWidget(self.terms)

        btn_signup = QPushButton("CREATE ACCOUNT")
        btn_signup.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_signup.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 14px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; margin-top: 10px; } QPushButton:hover { background-color: #0284c7; }")
        btn_signup.clicked.connect(self.handle_signup)
        card_layout.addWidget(btn_signup)

        # Footer switch to login
        footer_layout = QHBoxLayout()
        lbl_have_acc = QLabel("Already have an account?")
        lbl_have_acc.setStyleSheet("color: #64748b; font-size: 12px; border: none;")
        btn_signin = QPushButton("Sign In")
        btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_signin.setStyleSheet("QPushButton { background: none; border: none; color: #0ea5e9; font-size: 12px; font-weight: bold; } QPushButton:hover { text-decoration: underline; }")
        btn_signin.clicked.connect(lambda: self.parent.switch_page(0) if self.parent else None)
        
        footer_layout.addStretch()
        footer_layout.addWidget(lbl_have_acc)
        footer_layout.addWidget(btn_signin)
        footer_layout.addStretch()
        card_layout.addSpacing(15)
        card_layout.addLayout(footer_layout)
        main_layout.addWidget(card)

    def handle_signup(self):
        """Handles FR 02 (Validation), FR 03 (Uniqueness), and FR 04 (Record creation)."""
        fullname = self.fullname.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()
        confirm = self.confirm_password.text().strip()

        if not fullname or not password or not confirm:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return

        # FR 02 - Validate Signup Input Fields (Email Regex)
        is_valid, msg = Validator.is_valid_email(email)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", msg)
            return

        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match!")
            return

        if not self.terms.isChecked():
            QMessageBox.warning(self, "Validation Error", "You must agree to the Terms & Privacy Policy!")
            return

        # FR 03 - Check Email Uniqueness
        if is_email_registered(email):
            QMessageBox.warning(self, "Registration Error", "This email is already registered. Please use a different one.")
            return

        # FR 04 - Create User Account Record in MySQL Database
        db = get_db_connection()
        if db:
            try:
                cursor = db.cursor()
                names = fullname.split(" ", 1)
                fname = names[0]
                lname = names[1] if len(names) > 1 else ""
                sql = "INSERT INTO USER (First_Name, Last_Name, Email, Password) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (fname, lname, email, password))
                db.commit()
                cursor.close()
                db.close()
                
                QMessageBox.information(self, "Success", "Account Created Successfully!")
                self.parent.switch_page(0) # Redirect to Login
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")