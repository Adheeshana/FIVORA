"""
FIVORA - Industrial Fabric Inspection System
Main application entry point
"""

import sys
import json
import sqlite3
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from screens.login_screen import LoginScreen
from screens.signup_screen import SignupScreen
from screens.dashboard_screen import DashboardScreen
from database.db_manager import DatabaseManager
from utils.styles import apply_stylesheet


class FivoraApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FIVORA - Industrial Fabric Inspection System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.db_manager.init_database()
        
        # Apply global stylesheet
        apply_stylesheet(self)
        
        # Create stacked widget for screen management
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create screens
        self.login_screen = LoginScreen()
        self.signup_screen = SignupScreen()
        self.dashboard_screen = None
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.signup_screen)
        
        # Connect signals
        self.login_screen.login_successful.connect(self.on_login_success)
        self.login_screen.signup_clicked.connect(self.show_signup)
        self.signup_screen.signup_successful.connect(self.on_signup_success)
        self.signup_screen.back_to_login.connect(self.show_login)
        
        # Show login screen first
        self.show_login()
        
        # Set window icon (optional)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def show_login(self):
        """Show login screen"""
        self.stacked_widget.setCurrentWidget(self.login_screen)
    
    def show_signup(self):
        """Show signup screen"""
        self.stacked_widget.setCurrentWidget(self.signup_screen)
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        if self.dashboard_screen is not None:
            self.stacked_widget.removeWidget(self.dashboard_screen)
        
        self.dashboard_screen = DashboardScreen(user_data)
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.dashboard_screen.logout_clicked.connect(self.on_logout)
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
    
    def on_signup_success(self):
        """Handle successful signup"""
        self.login_screen.email_input.clear()
        self.login_screen.password_input.clear()
        QMessageBox.information(self, "Success", "Account created successfully! Please log in.")
        self.show_login()
    
    def on_logout(self):
        """Handle logout"""
        self.login_screen.email_input.clear()
        self.login_screen.password_input.clear()
        self.show_login()


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = FivoraApplication()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
