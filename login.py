import bcrypt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from database import get_user_by_email, ADMIN_EMAIL, ADMIN_PASSWORD, start_activity_log
from custom_dialog import show_message_dialog

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.is_dark_mode = True
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.brand = QLabel("Fivora")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.sub_brand = QLabel("INDUSTRIAL FABRIC INSPECTION SYSTEM")
        self.sub_brand.setStyleSheet("font-size: 10px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")
        self.sub_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_title = QLabel("Sign In")
        self.page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.brand)
        main_layout.addWidget(self.sub_brand)
        main_layout.addWidget(self.page_title)

        self.card = QFrame()
        self.card.setFixedWidth(420)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        self.lbl_email = QLabel("EMAIL ADDRESS")
        self.lbl_email.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none;")
        self.email = QLineEdit()
        self.email.setPlaceholderText("inspector@fivora.com")

        self.lbl_pwd = QLabel("PASSWORD")
        self.lbl_pwd.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none; margin-top: 5px;")
        self.password = QLineEdit()
        self.password.setPlaceholderText("••••••••")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_signin = QPushButton("SIGN IN")
        self.btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signin.clicked.connect(self.on_login_clicked)

        card_layout.addWidget(self.lbl_email)
        card_layout.addWidget(self.email)
        card_layout.addWidget(self.lbl_pwd)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.btn_signin)
        main_layout.addWidget(self.card)
        
        self.apply_theme(True)

    def apply_theme(self, is_dark):
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19;")
            self.brand.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-top: 15px; margin-bottom: 20px;")
            self.card.setStyleSheet("QFrame { background-color: #111827; border-radius: 12px; border: 1px solid #1e293b; }")
            input_style = "QLineEdit { padding: 12px; background: #1e293b; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }"
            self.email.setStyleSheet(input_style)
            self.password.setStyleSheet(input_style)
            self.btn_signin.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 14px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; margin-top: 10px; } QPushButton:hover { background-color: #0284c7; }")
        else:
            self.setStyleSheet("background-color: #f4f6f9;")
            self.brand.setStyleSheet("font-size: 32px; font-weight: bold; color: #0f172a;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 15px; margin-bottom: 20px;")
            self.card.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }")
            input_style = "QLineEdit { padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #0f172a; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }"
            self.email.setStyleSheet(input_style)
            self.password.setStyleSheet(input_style)
            self.btn_signin.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 14px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; margin-top: 10px; } QPushButton:hover { background-color: #0284c7; }")

    def clear_fields(self):
        self.email.clear()
        self.password.clear()

    def on_login_clicked(self):
        email = self.email.text().strip()
        password = self.password.text().strip()
        is_dark = getattr(self.parent, 'is_dark_mode', self.is_dark_mode) if self.parent else self.is_dark_mode

        if not email or not password:
            show_message_dialog(
                parent=self.window(),
                title="Credentials Required",
                message="Please enter both your email address and password to sign in.",
                dialog_type="warning",
                button_text="OK",
                is_dark=is_dark
            )
            return

        user_record = get_user_by_email(email)

        if email.lower() == ADMIN_EMAIL and password == ADMIN_PASSWORD and not user_record:
            user_record = {
                "id": 0, "fname": "System", "lname": "Administrator",
                "email": ADMIN_EMAIL, "role": "Admin", "status": "Active",
                "password_hash": ""
            }
        
        if user_record:
            status = str(user_record.get("status", "Active")).strip().lower()
            if status == "pending":
                show_message_dialog(self.window(), "Approval Required", "Your account is pending Admin approval.", "warning", "OK", is_dark)
                return
            if status in {"deactivated", "rejected"}:
                show_message_dialog(self.window(), "Account Deactivated", "Your account has been deactivated by the Admin.", "error", "OK", is_dark)
                return
            stored_hash = user_record.get("password_hash", "")
            if isinstance(stored_hash, bytes):
                stored_hash_str = stored_hash.decode('utf-8', errors='ignore')
            else:
                stored_hash_str = str(stored_hash)

            is_valid = False
            try:
                if stored_hash_str and bcrypt.checkpw(password.encode('utf-8'), stored_hash_str.encode('utf-8')):
                    is_valid = True
            except Exception:
                pass

            if not is_valid and password == stored_hash_str:
                is_valid = True

            if is_valid:
                user_record["activity_log_id"] = start_activity_log(user_record)
                self.parent.set_login_state(True, user_record)
                return
                
        show_message_dialog(
            parent=self.window(),
            title="Authentication Failed",
            message="Invalid email or password. Please check your credentials and try again.",
            dialog_type="error",
            button_text="RETRY",
            is_dark=is_dark
        )