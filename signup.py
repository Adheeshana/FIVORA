import re
import bcrypt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor
from database import register_user
from custom_dialog import show_success_dialog, show_message_dialog

class SignupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.is_dark_mode = True
        
        self.bg_pixmap = QPixmap("welcome_fabric.jfif")
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.brand = QLabel("Fivora")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.sub_brand = QLabel("INDUSTRIAL FABRIC INSPECTION SYSTEM")
        self.sub_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_title = QLabel("Create Account")
        self.page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(self.brand)
        main_layout.addWidget(self.sub_brand)
        main_layout.addWidget(self.page_title)

        self.card = QFrame()
        self.card.setFixedWidth(460)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setSpacing(8) # Space එක ප්‍රමාණයට අඩු කළා

        def create_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 10px; font-weight: bold; color: #94a3b8; border: none; background: transparent; margin-top: 4px;")
            return lbl

        name_layout = QHBoxLayout()
        self.fname = QLineEdit()
        self.fname.setPlaceholderText("First Name")
        self.lname = QLineEdit()
        self.lname.setPlaceholderText("Last Name")
        name_layout.addWidget(self.fname)
        name_layout.addWidget(self.lname)

        self.email = QLineEdit()
        self.email.setPlaceholderText("inspector@fivora.com")

        self.password = QLineEdit()
        self.password.setPlaceholderText("••••••••")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("••••••••")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.terms_checkbox = QCheckBox("I agree to the Terms & Privacy Policy")

        self.btn_signup = QPushButton("CREATE ACCOUNT")
        self.btn_signup.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signup.clicked.connect(self.on_signup_clicked)

        card_layout.addWidget(create_label("YOUR NAME"))
        card_layout.addLayout(name_layout)
        card_layout.addWidget(create_label("EMAIL ADDRESS"))
        card_layout.addWidget(self.email)
        card_layout.addWidget(create_label("PASSWORD"))
        card_layout.addWidget(self.password)
        card_layout.addWidget(create_label("CONFIRM PASSWORD"))
        card_layout.addWidget(self.confirm_password)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.terms_checkbox)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.btn_signup)
        
        main_layout.addWidget(self.card)
        self.apply_theme(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            scaled_bg = self.bg_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_bg.width()) // 2
            y = (self.height() - scaled_bg.height()) // 2
            painter.drawPixmap(x, y, scaled_bg)
            
            overlay_color = QColor(11, 15, 25, 210)
            painter.fillRect(self.rect(), overlay_color)
        else:
            painter.fillRect(self.rect(), QColor("#0b0f19"))

    def apply_theme(self, is_dark):
        self.is_dark_mode = is_dark
        self.setStyleSheet("") 
        
        if is_dark:
            self.brand.setStyleSheet("font-size: 32px; font-weight: 900; color: white; background: transparent;")
            self.sub_brand.setStyleSheet("font-size: 11px; font-weight: bold; color: #38bdf8; letter-spacing: 1.5px; background: transparent;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-top: 10px; margin-bottom: 15px; background: transparent;")
            
            self.card.setStyleSheet("QFrame { background-color: rgba(17, 24, 39, 0.88); border-radius: 12px; border: 1px solid #1e293b; }")
            
            # Text box උස ප්‍රමාණයකට (36px) සකස් කළා
            input_style = "QLineEdit { padding: 8px 12px; min-height: 36px; background: #1e293b; border: 1px solid #334155; border-radius: 6px; color: white; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }"
            self.fname.setStyleSheet(input_style)
            self.lname.setStyleSheet(input_style)
            self.email.setStyleSheet(input_style)
            self.password.setStyleSheet(input_style)
            self.confirm_password.setStyleSheet(input_style)
            
            self.terms_checkbox.setStyleSheet("color: #cbd5e1; font-size: 12px; border: none; background: transparent;")
            self.btn_signup.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 10px; min-height: 42px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; } QPushButton:hover { background-color: #0284c7; }")
        else:
            self.brand.setStyleSheet("font-size: 32px; font-weight: 900; color: #0f172a; background: transparent;")
            self.sub_brand.setStyleSheet("font-size: 11px; font-weight: bold; color: #0284c7; letter-spacing: 1.5px; background: transparent;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 10px; margin-bottom: 15px; background: transparent;")
            
            self.card.setStyleSheet("QFrame { background-color: rgba(255, 255, 255, 0.95); border-radius: 12px; border: 1px solid #e2e8f0; }")
            
            input_style = "QLineEdit { padding: 8px 12px; min-height: 36px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #0f172a; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }"
            self.fname.setStyleSheet(input_style)
            self.lname.setStyleSheet(input_style)
            self.email.setStyleSheet(input_style)
            self.password.setStyleSheet(input_style)
            self.confirm_password.setStyleSheet(input_style)
            
            self.terms_checkbox.setStyleSheet("color: #475569; font-size: 12px; border: none; background: transparent;")
            self.btn_signup.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 10px; min-height: 42px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; } QPushButton:hover { background-color: #0284c7; }")

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

        is_dark = getattr(self.parent, 'is_dark_mode', self.is_dark_mode) if self.parent else self.is_dark_mode

        if not all([fname, lname, email, pwd, cpwd]):
            show_message_dialog(
                parent=self.window(),
                title="Missing Information",
                message="All registration fields are required. Please fill in your name, email, and password.",
                dialog_type="warning",
                button_text="GOT IT",
                is_dark=is_dark
            )
            return

        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_pattern, email):
            show_message_dialog(
                parent=self.window(),
                title="Invalid Email Format",
                message="Please enter a valid work email address\n(e.g., inspector@fivora.com).",
                dialog_type="warning",
                button_text="CORRECT EMAIL",
                is_dark=is_dark
            )
            return

        if len(pwd) < 8:
            show_message_dialog(
                parent=self.window(),
                title="Weak Password",
                message="Password must contain at least 8 characters for workstation security.",
                dialog_type="warning",
                button_text="UPDATE PASSWORD",
                is_dark=is_dark
            )
            return

        if pwd != cpwd:
            show_message_dialog(
                parent=self.window(),
                title="Passwords Do Not Match",
                message="The password and confirmation password do not match. Please re-enter them.",
                dialog_type="warning",
                button_text="RETRY",
                is_dark=is_dark
            )
            return

        if not self.terms_checkbox.isChecked():
            show_message_dialog(
                parent=self.window(),
                title="Terms Agreement Required",
                message="Please agree to the Terms & Privacy Policy before creating your account.",
                dialog_type="warning",
                button_text="AGREE & PROCEED",
                is_dark=is_dark
            )
            return

        hashed_pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        success, msg = register_user(fname, lname, email, hashed_pwd)

        if success:
            show_success_dialog(
                parent=self.window(),
                title="Account Created Successfully!",
                message=msg,
                button_text="CONTINUE TO SIGN IN",
                is_dark=is_dark
            )
            self.clear_fields()
            if self.parent:
                self.parent.switch_page(0)
        else:
            show_message_dialog(
                parent=self.window(),
                title="Registration Failed",
                message=msg,
                dialog_type="error",
                button_text="TRY AGAIN",
                is_dark=is_dark
            )