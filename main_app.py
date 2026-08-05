import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QStackedWidget, QMessageBox)
from PyQt6.QtCore import Qt

from login import LoginPage
from signup import SignupPage
from dashboard import DashboardPage
from upload_page import UploadPage
from results_page import ResultsPage
from history_page import HistoryPage
from database import initialize_database

class FivoraMainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FIVORA - Industrial Fabric Inspection System")
        self.resize(1200, 800)

        self.is_logged_in = False
        self.is_dark_mode = True  

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.nav_bar = QWidget()
        self.nav_layout = QHBoxLayout(self.nav_bar)
        self.nav_layout.setContentsMargins(15, 8, 15, 8)

        # Dark mode එකේදී Light mode එකට මාරු වීමට "ඉර" (Sun) අයිකන් එක පෙන්වීම
        self.btn_theme = QPushButton("☀")
        self.btn_theme.setFixedSize(35, 35)
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.nav_layout.addWidget(self.btn_theme)

        self.btn_signin = QPushButton("Sign In")
        self.btn_signup = QPushButton("Sign Up")
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_upload = QPushButton("Upload / Capture")
        self.btn_results = QPushButton("Results")
        self.btn_report = QPushButton("Reports")
        
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setStyleSheet("color: #ef4444; font-weight: bold;")

        self.nav_buttons = [
            (self.btn_signin, 0), 
            (self.btn_signup, 1), 
            (self.btn_dashboard, 2), 
            (self.btn_upload, 3), 
            (self.btn_results, 4),
            (self.btn_report, 5)
        ]

        for btn, idx in self.nav_buttons:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            self.nav_layout.addWidget(btn)

        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.clicked.connect(lambda: self.set_login_state(False))
        
        self.nav_layout.addStretch()
        self.nav_layout.addWidget(self.btn_logout)
        self.main_layout.addWidget(self.nav_bar)

        self.pages = QStackedWidget()
        self.pages.addWidget(LoginPage(self))       
        self.pages.addWidget(SignupPage(self))      
        self.pages.addWidget(DashboardPage(self))   
        self.pages.addWidget(UploadPage(self))      
        self.pages.addWidget(ResultsPage(self))     
        self.pages.addWidget(HistoryPage(self))     

        self.main_layout.addWidget(self.pages)
        self.setCentralWidget(self.main_widget)

        self.apply_global_theme()
        
        self.set_login_state(False)
        self.switch_page(2) 

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.btn_theme.setText("☀" if self.is_dark_mode else "🌙")
        self.apply_global_theme()

    def apply_global_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet("QMainWindow { background-color: #0b0f19; }")
            self.nav_bar.setStyleSheet("background-color: #161b22; border-bottom: 1px solid #30363d;")
            self.btn_theme.setStyleSheet("background-color: transparent; border: 1px solid #30363d; color: #8b949e; border-radius: 4px;")
        else:
            self.setStyleSheet("QMainWindow { background-color: #f4f6f9; }")
            self.nav_bar.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #dee2e6;")
            self.btn_theme.setStyleSheet("background-color: transparent; border: 1px solid #dee2e6; color: #495057; border-radius: 4px;")
        
        self.update_nav_styles(self.pages.currentIndex())
        
        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            if hasattr(page, 'apply_theme'):
                page.apply_theme(self.is_dark_mode)

    def switch_page(self, index):
        if index in [3, 4, 5] and not self.is_logged_in:
            QMessageBox.warning(self, "Access Denied", "Please Sign In to access this feature!")
            self.switch_page(0)
            return

        if index == 0 and hasattr(self.pages.widget(0), 'clear_fields'):
            self.pages.widget(0).clear_fields()
        elif index == 1 and hasattr(self.pages.widget(1), 'clear_fields'):
            self.pages.widget(1).clear_fields()

        self.pages.setCurrentIndex(index if index < self.pages.count() else 2)
        self.update_nav_styles(index)
        
        if index == 4:
            self.pages.widget(4).refresh_results()
        elif index == 5:
            self.pages.widget(5).refresh_data()

    def update_nav_styles(self, active_index):
        active_style = "background-color: #00A3FF; color: white; font-weight: bold; border-radius: 4px; padding: 8px 16px; border: none;"
        if self.is_dark_mode:
            normal_style = "background-color: transparent; border: none; padding: 8px 16px; font-weight: bold; color: #8b949e;"
        else:
            normal_style = "background-color: transparent; border: none; padding: 8px 16px; font-weight: bold; color: #495057;"

        for btn, idx in self.nav_buttons:
            if idx == active_index:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(normal_style)

    def set_login_state(self, state: bool):
        self.is_logged_in = state
        if state:
            self.btn_signin.hide()
            self.btn_signup.hide()
            self.btn_logout.show()
        else:
            self.btn_signin.show()
            self.btn_signup.show()
            self.btn_logout.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    initialize_database()
    window = FivoraMainApp()
    window.show()
    sys.exit(app.exec())