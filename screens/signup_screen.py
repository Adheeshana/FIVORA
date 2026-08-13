"""
Signup Screen - FIVORA Fabric Inspection System
Modern signup screen with navbar
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCheckBox, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from database.db_manager import DatabaseManager
from utils.validators import validate_email, validate_password, hash_password
from components.navbar import Navbar


class SignupScreen(QWidget):
    signup_successful = pyqtSignal()  # Emit when signup successful
    back_to_login = pyqtSignal()  # Emit when back to login clicked
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize signup screen UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add navbar
        navbar = Navbar(user_name="Guest")
        main_layout.addWidget(navbar)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 40, 0, 40)
        content_layout.setSpacing(0)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Main title
        title = QLabel("FIVORA")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333;")
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Industrial Fabric Inspection System")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #00bcd4; font-weight: bold; text-transform: uppercase;")
        header_layout.addWidget(subtitle)
        
        # Create Account heading
        create_heading = QLabel("Create Account")
        create_heading.setFont(QFont("Segoe UI", 22, QFont.Bold))
        create_heading.setAlignment(Qt.AlignCenter)
        create_heading.setStyleSheet("color: #333; margin-top: 10px;")
        header_layout.addWidget(create_heading)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(30)
        
        # Card container
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(12)
        
        # Full Name field
        name_label = QLabel("FULL NAME")
        name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        name_label.setStyleSheet("color: #777;")
        card_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Sahan Perera")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
                background-color: white;
            }
        """)
        self.name_input.setFixedHeight(40)
        card_layout.addWidget(self.name_input)
        card_layout.addSpacing(5)
        
        # Email field
        email_label = QLabel("EMAIL ADDRESS")
        email_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        email_label.setStyleSheet("color: #777;")
        card_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("inspector@fivora.com")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
                background-color: white;
            }
        """)
        self.email_input.setFixedHeight(40)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(5)
        
        # Password field
        password_label = QLabel("PASSWORD")
        password_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        password_label.setStyleSheet("color: #777;")
        card_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
                background-color: white;
            }
        """)
        self.password_input.setFixedHeight(40)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(5)
        
        # Confirm Password field
        confirm_label = QLabel("CONFIRM PASSWORD")
        confirm_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        confirm_label.setStyleSheet("color: #777;")
        card_layout.addWidget(confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("••••••••")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
                background-color: white;
            }
        """)
        self.confirm_input.setFixedHeight(40)
        card_layout.addWidget(self.confirm_input)
        card_layout.addSpacing(15)
        
        # Terms checkbox
        terms_layout = QHBoxLayout()
        self.terms_checkbox = QCheckBox("I agree to the Terms & Privacy Policy")
        self.terms_checkbox.setStyleSheet("""
            QCheckBox {
                color: #666;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #00bcd4;
                border: 1px solid #00bcd4;
                border-radius: 3px;
            }
        """)
        terms_layout.addWidget(self.terms_checkbox)
        terms_layout.addStretch()
        card_layout.addLayout(terms_layout)
        card_layout.addSpacing(15)
        
        # Create Account Button
        create_button = QPushButton("CREATE ACCOUNT")
        create_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        create_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                           stop:0 #00bcd4, stop:1 #007bff);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                           stop:0 #00acc1, stop:1 #0056b3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                           stop:0 #009fb7, stop:1 #003d82);
            }
        """)
        create_button.setFixedHeight(45)
        create_button.clicked.connect(self.on_create_account)
        card_layout.addWidget(create_button)
        
        # Footer link
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 15, 0, 0)
        footer_text = QLabel("Already have an account?")
        footer_text.setStyleSheet("color: #666; font-size: 13px;")
        signin_link = QPushButton("Sign In")
        signin_link.setFlat(True)
        signin_link.setStyleSheet("""
            QPushButton {
                color: #00bcd4;
                background: transparent;
                border: none;
                font-weight: bold;
                text-decoration: underline;
                font-size: 13px;
                padding: 0;
            }
            QPushButton:hover {
                color: #007bff;
            }
        """)
        signin_link.clicked.connect(self.on_back_login)
        footer_layout.addWidget(footer_text)
        footer_layout.addWidget(signin_link)
        footer_layout.addStretch()
        card_layout.addLayout(footer_layout)
        
        # Card wrapper
        card_widget = QWidget()
        card_widget.setLayout(card_layout)
        card_widget.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 12px;
            }
        """)
        card_widget.setFixedWidth(450)
        
        # Center the card
        card_container = QHBoxLayout()
        card_container.addStretch()
        card_container.addWidget(card_widget)
        card_container.addStretch()
        
        content_layout.addLayout(card_container)
        content_layout.addStretch()
        
        # Wrap content
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        content_widget.setStyleSheet("background-color: #f4f7f9;")
        
        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #f4f7f9;")
    
    def on_create_account(self):
        """Handle create account button click"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Validate inputs
        if not name or not email or not password or not confirm:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if not validate_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        if not validate_password(password):
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if not self.terms_checkbox.isChecked():
            QMessageBox.warning(self, "Error", "Please agree to Terms & Privacy Policy")
            return
        
        # Try to create account
        hashed_password = hash_password(password)
        success = self.db_manager.create_user(name, email, hashed_password)
        
        if success:
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.clear_fields()
            self.signup_successful.emit()
        else:
            QMessageBox.warning(self, "Error", "Email already registered or database error")
    
    def clear_fields(self):
        """Clear all input fields"""
        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_input.clear()
        self.terms_checkbox.setChecked(False)
    
    def on_back_login(self):
        """Emit back to login signal"""
        self.clear_fields()
        self.back_to_login.emit()

