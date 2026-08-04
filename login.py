
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFrame, QCheckBox, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from database import get_db_connection

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # FR 05 - Display Sign In Form
        brand = QLabel("Fivora")
        brand.setStyleSheet("font-size: 32px; font-weight: bold; color: #0f172a;")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        sub_brand = QLabel("INDUSTRIAL FABRIC INSPECTION SYSTEM")
        sub_brand.setStyleSheet("font-size: 10px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")
        sub_brand.setAlignment(Qt.AlignmentFlag.AlignCenter)

        page_title = QLabel("Sign In")
        page_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a; margin-top: 15px; margin-bottom: 20px;")
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(brand)
        main_layout.addWidget(sub_brand)
        main_layout.addWidget(page_title)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; }")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        lbl_email = QLabel("EMAIL ADDRESS")
        lbl_email.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none;")
        self.email = QLineEdit()
        self.email.setPlaceholderText("inspector@fivora.com")
        self.email.setStyleSheet("QLineEdit { padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #0f172a; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }")

        lbl_pwd = QLabel("PASSWORD")
        lbl_pwd.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; border: none; margin-top: 5px;")
        self.password = QLineEdit()
        self.password.setPlaceholderText("••••••••")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet("QLineEdit { padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #0f172a; font-size: 13px; } QLineEdit:focus { border: 1px solid #0ea5e9; }")

        btn_signin = QPushButton("SIGN IN")
        btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_signin.setStyleSheet("QPushButton { background-color: #0ea5e9; color: white; padding: 14px; font-weight: bold; border-radius: 6px; font-size: 14px; border: none; margin-top: 10px; } QPushButton:hover { background-color: #0284c7; }")
        btn_signin.clicked.connect(self.on_login_clicked)

        card_layout.addWidget(lbl_email)
        card_layout.addWidget(self.email)
        card_layout.addWidget(lbl_pwd)
        card_layout.addWidget(self.password)
        card_layout.addWidget(btn_signin)
        main_layout.addWidget(card)

    def on_login_clicked(self):
        """Handles FR 06 (Validation), FR 07 (Retrieve by Email), FR 08 (Verify Password), and FR 09 (Session)."""
        email = self.email.text().strip()
        password = self.password.text().strip()

        # FR 06 - Validate Sign In Input Fields
        if not email or not password:
            QMessageBox.warning(self, "Validation Error", "Please fill in all fields!")
            return

        # FR 07 - Retrieve User by Email & FR 08 - Verify Password
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM USER WHERE Email = %s AND Password = %s", (email, password))
            user_record = cursor.fetchone()
            cursor.close()
            db.close()
            
            if user_record:
                # FR 09 - Create User Session on Success
                self.parent.set_login_state(True)
            else:
                QMessageBox.warning(self, "Error", "Invalid Email or Password!")
        else:
            # Fallback for offline testing
            self.parent.set_login_state(True)