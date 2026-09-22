import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt

from login import LoginPage
from signup import SignupPage
from dashboard import DashboardPage
from upload_page import UploadPage
from results_page import ResultsPage
from history_page import HistoryPage
from operators_page import OperatorsPage
from database import initialize_database, finish_activity_log


class PagesCompatWrapper:
    """Compatibility helper to allow legacy self.parent.pages.widget(index) access."""
    def __init__(self, main_app):
        self.app = main_app

    def widget(self, index):
        mapping = {
            0: self.app.login_page,
            1: self.app.signup_page,
            2: self.app.dashboard_page,
            3: self.app.upload_page,
            4: self.app.results_page,
            5: self.app.history_page,
            6: self.app.operators_page
        }
        return mapping.get(index, None)


class FivoraMainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FIVORA - Industrial Fabric Inspection System")
        self.resize(1280, 820)
        self.setMinimumSize(1024, 700)

        self.is_logged_in = False
        self.current_user = None
        self.current_role = "Operator"
        self.is_dark_mode = True  

        # Root Stacked Widget:
        # Index 0 -> Auth View (Public mode with Top Header)
        # Index 1 -> App View (Protected mode with Left Vertical Sidebar)
        self.root_stack = QStackedWidget()

        # ==========================================
        # 1. UNAUTHENTICATED / PUBLIC VIEW
        # ==========================================
        self.auth_view = QWidget()
        auth_layout = QVBoxLayout(self.auth_view)
        auth_layout.setContentsMargins(0, 0, 0, 0)
        auth_layout.setSpacing(0)

        # Public Top Header Bar
        self.auth_header = QWidget()
        auth_header_layout = QHBoxLayout(self.auth_header)
        auth_header_layout.setContentsMargins(24, 12, 24, 12)

        self.auth_brand = QLabel("FIVORA")
        self.auth_subbrand = QLabel("INDUSTRIAL FABRIC INSPECTION SYSTEM")
        
        brand_container = QWidget()
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(2)
        brand_layout.addWidget(self.auth_brand)
        brand_layout.addWidget(self.auth_subbrand)

        self.btn_auth_theme = QPushButton("☀")
        self.btn_auth_theme.setFixedSize(38, 38)
        self.btn_auth_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_auth_theme.clicked.connect(self.toggle_theme)

        self.btn_signin = QPushButton("Sign In")
        self.btn_signup = QPushButton("Sign Up")
        self.btn_signin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_signup.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_signin.clicked.connect(lambda: self.switch_page(0))
        self.btn_signup.clicked.connect(lambda: self.switch_page(1))

        auth_header_layout.addWidget(brand_container)
        auth_header_layout.addStretch()
        auth_header_layout.addWidget(self.btn_signin)
        auth_header_layout.addWidget(self.btn_signup)
        auth_header_layout.addSpacing(10)
        auth_header_layout.addWidget(self.btn_auth_theme)

        # Public Pages Stack (Sign In & Sign Up)
        self.auth_stack = QStackedWidget()
        self.login_page = LoginPage(self)
        self.signup_page = SignupPage(self)
        self.auth_stack.addWidget(self.login_page)   # Auth Stack Index 0
        self.auth_stack.addWidget(self.signup_page)  # Auth Stack Index 1

        auth_layout.addWidget(self.auth_header)
        auth_layout.addWidget(self.auth_stack)

        # ==========================================
        # 2. AUTHENTICATED / PROTECTED VIEW
        # ==========================================
        self.app_view = QWidget()
        app_layout = QHBoxLayout(self.app_view)
        app_layout.setContentsMargins(0, 0, 0, 0)
        app_layout.setSpacing(0)

        # Left Vertical Sidebar
        self.sidebar_widget = QFrame()
        self.sidebar_widget.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(16, 24, 16, 20)
        sidebar_layout.setSpacing(8)

        # Sidebar Header Branding
        self.sidebar_brand = QLabel("FIVORA")
        self.sidebar_subbrand = QLabel("FABRIC INSPECTION SYSTEM")
        
        sidebar_layout.addWidget(self.sidebar_brand)
        sidebar_layout.addWidget(self.sidebar_subbrand)
        sidebar_layout.addSpacing(24)

        # Sidebar Navigation Buttons
        self.btn_dashboard = QPushButton("  📊   Dashboard")
        self.btn_upload = QPushButton("  📷   Upload / Capture")
        self.btn_results = QPushButton("  🔍   Results")
        self.btn_report = QPushButton("  📋   Reports")
        self.btn_operators = QPushButton("  👥   Operators")

        self.sidebar_buttons = [
            (self.btn_dashboard, 2),
            (self.btn_upload, 3),
            (self.btn_results, 4),
            (self.btn_report, 5)
        ]

        for btn, idx in self.sidebar_buttons:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(44)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)

        self.btn_operators.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_operators.setFixedHeight(44)
        self.btn_operators.clicked.connect(lambda: self.switch_page(6))
        sidebar_layout.addWidget(self.btn_operators)

        sidebar_layout.addStretch()

        # Sidebar Bottom Tools (Theme Toggle + Logout)
        self.btn_sidebar_theme = QPushButton("  ☀   Toggle Theme")
        self.btn_sidebar_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sidebar_theme.setFixedHeight(40)
        self.btn_sidebar_theme.clicked.connect(self.toggle_theme)

        self.btn_logout = QPushButton("  🚪   Logout")
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setFixedHeight(42)
        self.btn_logout.clicked.connect(lambda: self.set_login_state(False))

        sidebar_layout.addWidget(self.btn_sidebar_theme)
        sidebar_layout.addSpacing(4)
        sidebar_layout.addWidget(self.btn_logout)

        # Protected content wrapper keeps identity visible on every work page.
        protected_content = QWidget()
        protected_content_layout = QVBoxLayout(protected_content)
        protected_content_layout.setContentsMargins(0, 0, 0, 0)
        protected_content_layout.setSpacing(0)

        self.app_header = QFrame()
        app_header_layout = QHBoxLayout(self.app_header)
        app_header_layout.setContentsMargins(22, 12, 22, 12)
        self.header_title = QLabel("Inspection workspace")
        self.header_role = QLabel("Role: Operator")
        self.header_user = QLabel("")
        app_header_layout.addWidget(self.header_title)
        app_header_layout.addStretch()
        app_header_layout.addWidget(self.header_user)
        app_header_layout.addSpacing(18)
        app_header_layout.addWidget(self.header_role)

        # Protected Content Pages Stack
        self.protected_stack = QStackedWidget()
        self.dashboard_page = DashboardPage(self)
        self.upload_page = UploadPage(self)
        self.results_page = ResultsPage(self)
        self.history_page = HistoryPage(self)
        self.operators_page = OperatorsPage(self)

        self.protected_stack.addWidget(self.dashboard_page)  # Protected Stack Index 0 (Global 2)
        self.protected_stack.addWidget(self.upload_page)     # Protected Stack Index 1 (Global 3)
        self.protected_stack.addWidget(self.results_page)    # Protected Stack Index 2 (Global 4)
        self.protected_stack.addWidget(self.history_page)    # Protected Stack Index 3 (Global 5)
        self.protected_stack.addWidget(self.operators_page)  # Protected Stack Index 4 (Global 6)

        app_layout.addWidget(self.sidebar_widget)
        protected_content_layout.addWidget(self.app_header)
        protected_content_layout.addWidget(self.protected_stack)
        app_layout.addWidget(protected_content)

        # Add both root views to root_stack
        self.root_stack.addWidget(self.auth_view) # Index 0
        self.root_stack.addWidget(self.app_view)  # Index 1

        self.setCentralWidget(self.root_stack)

        # Backward compatibility wrapper for self.pages.widget(idx) calls in child pages
        self.pages = PagesCompatWrapper(self)

        # Apply global theme and set default unauthenticated state
        self.apply_global_theme()
        self.set_login_state(False)
        
        # 🔴 ඇප් එක ඕපන් වෙද්දීම Full Screen (Maximized) වෙන්න මේ පේළිය එකතු කළා
        self.showMaximized()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        theme_icon = "☀" if self.is_dark_mode else "🌙"
        self.btn_auth_theme.setText(theme_icon)
        self.btn_sidebar_theme.setText(f"  {theme_icon}   Toggle Theme")
        self.apply_global_theme()

    def apply_global_theme(self):
        if self.is_dark_mode:
            self.setStyleSheet("QMainWindow { background-color: #0b0f19; }")
            self.auth_header.setStyleSheet("background-color: #111827; border-bottom: 1px solid #1e293b;")
            self.auth_brand.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
            self.auth_subbrand.setStyleSheet("font-size: 9px; font-weight: bold; color: #0ea5e9; letter-spacing: 1.5px;")
            self.btn_auth_theme.setStyleSheet("background-color: #1e293b; border: 1px solid #334155; color: #f8fafc; border-radius: 6px; font-weight: bold;")
            
            self.sidebar_widget.setStyleSheet("QFrame { background-color: #111827; border-right: 1px solid #1e293b; }")
            self.app_header.setStyleSheet("QFrame { background-color: #111827; border-bottom: 1px solid #1e293b; }")
            self.header_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #f8fafc;")
            self.header_role.setStyleSheet("font-size: 12px; font-weight: 700; color: #38bdf8; background: #1e293b; padding: 6px 10px; border-radius: 6px;")
            self.header_user.setStyleSheet("font-size: 12px; color: #94a3b8;")
            self.sidebar_brand.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: 1px;")
            self.sidebar_subbrand.setStyleSheet("font-size: 9px; font-weight: bold; color: #0ea5e9; letter-spacing: 1.5px;")
            
            self.btn_sidebar_theme.setStyleSheet("QPushButton { background-color: #1e293b; color: #94a3b8; border: 1px solid #334155; border-radius: 6px; text-align: left; padding-left: 14px; font-weight: 600; font-size: 12px; } QPushButton:hover { background-color: #334155; color: white; }")
            self.btn_logout.setStyleSheet("QPushButton { background-color: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; text-align: left; padding-left: 14px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #ef4444; color: white; }")
        else:
            self.setStyleSheet("QMainWindow { background-color: #f4f6f9; }")
            self.auth_header.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #e2e8f0;")
            self.auth_brand.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a; letter-spacing: 1px;")
            self.auth_subbrand.setStyleSheet("font-size: 9px; font-weight: bold; color: #0284c7; letter-spacing: 1.5px;")
            self.btn_auth_theme.setStyleSheet("background-color: #f1f5f9; border: 1px solid #cbd5e1; color: #334155; border-radius: 6px; font-weight: bold;")
            
            self.sidebar_widget.setStyleSheet("QFrame { background-color: #ffffff; border-right: 1px solid #e2e8f0; }")
            self.app_header.setStyleSheet("QFrame { background-color: #ffffff; border-bottom: 1px solid #e2e8f0; }")
            self.header_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a;")
            self.header_role.setStyleSheet("font-size: 12px; font-weight: 700; color: #0369a1; background: #e0f2fe; padding: 6px 10px; border-radius: 6px;")
            self.header_user.setStyleSheet("font-size: 12px; color: #64748b;")
            self.sidebar_brand.setStyleSheet("font-size: 22px; font-weight: 800; color: #0f172a; letter-spacing: 1px;")
            self.sidebar_subbrand.setStyleSheet("font-size: 9px; font-weight: bold; color: #0284c7; letter-spacing: 1.5px;")
            
            self.btn_sidebar_theme.setStyleSheet("QPushButton { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; border-radius: 6px; text-align: left; padding-left: 14px; font-weight: 600; font-size: 12px; } QPushButton:hover { background-color: #e2e8f0; color: #0f172a; }")
            self.btn_logout.setStyleSheet("QPushButton { background-color: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; border-radius: 6px; text-align: left; padding-left: 14px; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #dc2626; color: white; }")

        current_idx = self.get_current_global_index()
        self.update_nav_styles(current_idx)

        # Notify sub-pages of theme change
        pages_to_theme = [
            self.login_page, self.signup_page, 
            self.dashboard_page, self.upload_page, 
            self.results_page, self.history_page
            , self.operators_page
        ]
        for page in pages_to_theme:
            if hasattr(page, 'apply_theme'):
                page.apply_theme(self.is_dark_mode)

    def get_current_global_index(self):
        if self.root_stack.currentIndex() == 0:
            return self.auth_stack.currentIndex()
        else:
            return self.protected_stack.currentIndex() + 2

    def switch_page(self, index: int):
        # Access control for protected routes
        if index in [2, 3, 4, 5, 6] and not self.is_logged_in:
            from custom_dialog import show_message_dialog
            show_message_dialog(self, "Sign In Required", "Please sign in to open this workspace.", "warning", "OK", self.is_dark_mode)
            self.switch_page(0)
            return

        if index in [0, 1]: # Public Auth Pages
            self.root_stack.setCurrentIndex(0)
            self.auth_stack.setCurrentIndex(index)
            if index == 0 and hasattr(self.login_page, 'clear_fields'):
                self.login_page.clear_fields()
            elif index == 1 and hasattr(self.signup_page, 'clear_fields'):
                self.signup_page.clear_fields()

        elif index in [2, 3, 4, 5, 6]: # Protected Dashboard Pages
            if index == 6 and self.current_role != "Admin":
                from custom_dialog import show_message_dialog
                show_message_dialog(self, "Admin Access Required", "Only Admins can open the Operators page.", "error", "OK", self.is_dark_mode)
                return
            self.root_stack.setCurrentIndex(1)
            protected_idx = index - 2
            self.protected_stack.setCurrentIndex(protected_idx)

            if index == 4 and hasattr(self.results_page, 'refresh_results'):
                self.results_page.refresh_results()
            elif index == 5 and hasattr(self.history_page, 'refresh_data'):
                self.history_page.refresh_data()
            elif index == 6 and hasattr(self.operators_page, 'refresh_data'):
                self.operators_page.refresh_data()

        self.update_nav_styles(index)

    def update_nav_styles(self, active_index: int):
        # Auth Top Header buttons styling
        auth_active = "background-color: #0ea5e9; color: white; font-weight: bold; border-radius: 6px; padding: 8px 20px; border: none; font-size: 13px;"
        if self.is_dark_mode:
            auth_normal = "background-color: transparent; border: none; padding: 8px 20px; font-weight: bold; color: #94a3b8; font-size: 13px;"
        else:
            auth_normal = "background-color: transparent; border: none; padding: 8px 20px; font-weight: bold; color: #64748b; font-size: 13px;"

        self.btn_signin.setStyleSheet(auth_active if active_index == 0 else auth_normal)
        self.btn_signup.setStyleSheet(auth_active if active_index == 1 else auth_normal)

        # Vertical Sidebar buttons styling
        sidebar_active = "QPushButton { background-color: #00A3FF; color: white; font-weight: bold; border-radius: 8px; text-align: left; padding-left: 16px; border: none; font-size: 13px; }"
        if self.is_dark_mode:
            sidebar_normal = "QPushButton { background-color: transparent; color: #94a3b8; border-radius: 8px; text-align: left; padding-left: 16px; border: none; font-size: 13px; font-weight: 600; } QPushButton:hover { background-color: #1e293b; color: white; }"
        else:
            sidebar_normal = "QPushButton { background-color: transparent; color: #64748b; border-radius: 8px; text-align: left; padding-left: 16px; border: none; font-size: 13px; font-weight: 600; } QPushButton:hover { background-color: #f1f5f9; color: #0f172a; }"

        for btn, idx in self.sidebar_buttons:
            if idx == active_index:
                btn.setStyleSheet(sidebar_active)
            else:
                btn.setStyleSheet(sidebar_normal)
            self.btn_operators.setStyleSheet(sidebar_active if active_index == 6 else sidebar_normal)

    def set_login_state(self, state: bool, user_record=None):
        if not state and self.current_user:
            finish_activity_log(self.current_user, self.current_user.get("activity_log_id"))
        self.is_logged_in = state
        if state:
            self.current_user = user_record or {}
            role = str(self.current_user.get("role", "Operator")).strip().title()
            self.current_role = role if role in {"Admin", "Operator"} else "Operator"
            name = " ".join(filter(None, [self.current_user.get("fname"), self.current_user.get("lname")])).strip()
            self.header_user.setText(name or self.current_user.get("email", ""))
            self.header_role.setText(f"Role: {self.current_role}")
            self.btn_report.setText("  📋   Admin Reports" if self.current_role == "Admin" else "  📋   Reports")
            self.btn_operators.setVisible(self.current_role == "Admin")
            self.root_stack.setCurrentIndex(1)
            self.switch_page(2) # Default to Dashboard post-authentication
        else:
            self.current_user = None
            self.current_role = "Operator"
            self.header_user.setText("")
            self.header_role.setText("Role: Operator")
            self.btn_report.setText("  📋   Reports")
            self.btn_operators.setVisible(False)
            self.root_stack.setCurrentIndex(0)
            self.switch_page(0) # Default to Sign In in unauthenticated state


if __name__ == "__main__":
    app = QApplication(sys.argv)
    initialize_database()
    window = FivoraMainApp()
    window.showMaximized()
    sys.exit(app.exec())