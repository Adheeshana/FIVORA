"""
Login Screen - FIVORA Fabric Inspection System
Modern sign in screen with navbar - Flask inspired design
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from database.db_manager import DatabaseManager
from utils.validators import validate_email, verify_password
from components.navbar import Navbar


class LoginScreen(QWidget):
    login_successful = pyqtSignal(dict)  # Emit user data on successful login
    signup_clicked = pyqtSignal()  # Emit when signup button clicked
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        """Initialize login screen UI"""
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
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Main title
        title = QLabel("FIVORA")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333;")
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Industrial Fabric Inspection System")
        subtitle.setFont(QFont("Segoe UI", 11, QFont.Bold))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #00bcd4; letter-spacing: 1px;")
        header_layout.addWidget(subtitle)
        
        # Sign In heading
        signin_heading = QLabel("Sign In")
        signin_heading.setFont(QFont("Segoe UI", 20, QFont.Bold))
        signin_heading.setAlignment(Qt.AlignCenter)
        signin_heading.setStyleSheet("color: #333; margin-top: 15px;")
        header_layout.addWidget(signin_heading)
        
        content_layout.addLayout(header_layout)
        content_layout.addSpacing(30)
        
        # Card container
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)
        
        # Email field
        email_label = QLabel("EMAIL ADDRESS")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        email_label.setStyleSheet("color: #666;")
        card_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("inspector@fivora.com")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 13px;
                selection-background-color: #00bcd4;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
                background-color: white;
                outline: none;
            }
        """)
        self.email_input.setFixedHeight(40)
        card_layout.addWidget(self.email_input)
        
        # Password field
        password_label = QLabel("PASSWORD")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        password_label.setStyleSheet("color: #666;")
        card_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                font-size: 13px;
                selection-background-color: #00bcd4;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
                background-color: white;
                outline: none;
            }
        """)
        self.password_input.setFixedHeight(40)
        card_layout.addWidget(self.password_input)
        
        # Extras row (Remember me + Forgot password)
        extras_layout = QHBoxLayout()
        extras_layout.setSpacing(0)
        
        remember_checkbox = QCheckBox("Remember me")
        remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #666;
                font-size: 12px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
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
        extras_layout.addWidget(remember_checkbox)
        extras_layout.addStretch()
        
        forgot_button = QPushButton("Forgot password?")
        forgot_button.setFlat(True)
        forgot_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00bcd4;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                color: #007bff;
            }
        """)
        forgot_button.setCursor(Qt.PointingHandCursor)
        forgot_button.clicked.connect(self.on_forgot_password)
        extras_layout.addWidget(forgot_button)
        
        card_layout.addLayout(extras_layout)
        card_layout.addSpacing(15)
        
        # Sign In Button with gradient
        signin_button = QPushButton("SIGN IN")
        signin_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        signin_button.setStyleSheet("""
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
        signin_button.setFixedHeight(45)
        signin_button.setCursor(Qt.PointingHandCursor)
        signin_button.clicked.connect(self.on_signin)
        card_layout.addWidget(signin_button)
        
        # Footer link
        footer_layout = QHBoxLayout()
        footer_text = QLabel("Don't have an account?")
        footer_text.setStyleSheet("color: #666; font-size: 13px;")
        signup_link = QPushButton("Create Account")
        signup_link.setFlat(True)
        signup_link.setStyleSheet("""
            QPushButton {
                color: #00bcd4;
                background: transparent;
                border: none;
                font-weight: bold;
                text-decoration: underline;
                font-size: 13px;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                color: #007bff;
            }
        """)
        signup_link.setCursor(Qt.PointingHandCursor)
        signup_link.clicked.connect(self.on_signup)
        footer_layout.addWidget(footer_text)
        footer_layout.addWidget(signup_link)
        footer_layout.addStretch()
        card_layout.addLayout(footer_layout)
        
        # Card wrapper
        card_widget = QWidget()
        card_widget.setLayout(card_layout)
        card_widget.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            }
        """)
        card_widget.setFixedWidth(400)
        
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
    
    def on_signin(self):
        """Handle sign in button click"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if not validate_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        # Check credentials
        user = self.db_manager.get_user_by_email(email)
        if user is None:
            QMessageBox.warning(self, "Error", "This email is not registered")
            return
        
        # Verify password
        if not verify_password(password, user['password']):
            QMessageBox.warning(self, "Error", "Incorrect password")
            return
        
        # Successful login
        user_data = {
            'id': user['id'],
            'full_name': user['full_name'],
            'email': user['email']
        }
        self.login_successful.emit(user_data)
    
    def on_signup(self):
        """Emit signup clicked signal"""
        self.signup_clicked.emit()
    
    def on_forgot_password(self):
        """Handle forgot password"""
        QMessageBox.information(self, "Info", "Please contact administrator to reset your password")


