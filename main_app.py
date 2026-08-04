import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel, QMessageBox)
from PyQt6.QtCore import Qt

# Import Views directly from root folder
from login import LoginPage
from signup import SignupPage
from dashboard import DashboardPage
from upload_page import UploadPage

# Import Database Initializer
from database import initialize_database

class FivoraMainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FIVORA - Industrial Fabric Inspection System")
        self.resize(1200, 800)

        # Global Session State (FR 09, FR 10)
        self.is_logged_in = False
        
        # UI Theme State (True = Dark Mode, False = Light Mode)
        self.is_dark_mode = True  

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Top Navigation Bar ---
        self.nav_bar = QWidget()
        self.nav_layout = QHBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(15, 8, 15, 8)

        # Theme Toggle Button
        self.btn_theme = QPushButton("☀")
        self.btn_theme.setFixedSize(35, 35)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.nav_layout.addWidget(self.btn_theme)

        # Navigation Buttons
        self.btn_login = QPushButton("Login")
        self.btn_signup = QPushButton("Signup")
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_upload = QPushButton("Upload Image")
        self.btn_results = QPushButton("Results")
        self.btn_report = QPushButton("Report")

        self.nav_buttons = [self.btn_login, self.btn_signup, self.btn_dashboard, 
                            self.btn_upload, self.btn_results, self.btn_report]

        for idx, btn in enumerate(self.nav_buttons):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            self.nav_layout.addWidget(btn)

        self.nav_layout.addStretch()
        self.main_layout.addWidget(self.nav_bar)

        # --- Pages Stack (Router) ---
        self.pages = QStackedWidget()
        self.pages.addWidget(LoginPage(self))      # Index 0
        self.pages.addWidget(SignupPage(self))     # Index 1
        self.pages.addWidget(DashboardPage(self))  # Index 2
        self.pages.addWidget(UploadPage(self))     # Index 3

        self.main_layout.addWidget(self.pages)
        self.setCentralWidget(self.main_widget)

        # Initialize Default State
        self.apply_global_theme()
        self.switch_page(2) # Default landing page

    def toggle_theme(self):
        """Toggles between Dark and Light UI themes."""
        self.is_dark_mode = not self.is_dark_mode
        self.btn_theme.setText("☀" if self.is_dark_mode else "🌙")
        self.apply_global_theme()

        # Update Theme in child views if supported
        dashboard_page = self.pages.widget(2)
        if hasattr(dashboard_page, 'apply_theme'):
            dashboard_page.apply_theme(self.is_dark_mode)

    def apply_global_theme(self):
        """Applies styles based on current theme state."""
        if self.is_dark_mode:
            self.setStyleSheet("QMainWindow { background-color: #0b0f19; }")
            self.nav_bar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
            self.btn_theme.setStyleSheet("background-color: transparent; border: 1px solid #30363d; color: #8b949e; border-radius: 4px;")
        else:
            self.setStyleSheet("QMainWindow { background-color: #f4f6f9; }")
            self.nav_bar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #dee2e6;")
            self.btn_theme.setStyleSheet("background-color: transparent; border: 1px solid #dee2e6; color: #495057; border-radius: 4px;")
        
        self.update_nav_styles(self.pages.currentIndex())

    def switch_page(self, index):
        """Handles page routing and authentication checks."""
        # Restrict access to authenticated features
        if index in [3, 4, 5] and not self.is_logged_in:
            QMessageBox.warning(self, "Access Denied", "Please Sign In to access this feature!")
            self.switch_page(0) # Redirect to Login
            return

        self.pages.setCurrentIndex(index if index < self.pages.count() else 2)
        self.update_nav_styles(index)

    def update_nav_styles(self, active_index):
        """Updates navigation button styles based on active page and theme."""
        if self.is_dark_mode:
            active_style = "background-color: #00A3FF; color: white; font-weight: bold; border-radius: 4px; padding: 8px 16px; border: none;"
            normal_style = "background-color: transparent; border: none; padding: 8px 16px; font-weight: bold; color: #8b949e;"
            disabled_style = "background-color: transparent; border: none; padding: 8px 16px; font-weight: bold; color: #484f58;"
        else:
            active_style = "background-color: #00A3FF; color: white; font-weight: bold; border-radius: 4px; padding: 8px 16px; border: none;"
            normal_style = "background-color: transparent; border: none; padding: 8px 16px; font-weight: bold; color: #495057;"
            disabled_style = "background-color: transparent; border: none; padding: 8px 16px; font-weight: bold; color: #adb5bd;"

        for idx, btn in enumerate(self.nav_buttons):
            if idx in [3, 4, 5] and not self.is_logged_in:
                btn.setStyleSheet(disabled_style)
            elif idx == active_index:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(normal_style)

    def set_login_state(self, state: bool):
        """
        FR 09: Create User Session on Success
        FR 10: Terminate Session on Logout
        """
        self.is_logged_in = state
        self.btn_login.setText("Logout" if state else "Login")
        # Route based on login status
        self.switch_page(2 if state else 0) 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize the MySQL database and tables on startup
    initialize_database()
    
    window = FivoraMainApp()
    window.show()
    sys.exit(app.exec())