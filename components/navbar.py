"""
Navbar Component - FIVORA Fabric Inspection System
Modern navigation bar with top bar and main navigation
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor


class Navbar(QWidget):
    """Main navbar component with top bar and navigation"""
    
    logout_clicked = pyqtSignal()
    nav_clicked = pyqtSignal(str)  # Emit navigation action
    
    def __init__(self, user_name="Inspector Perera"):
        super().__init__()
        self.user_name = user_name
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())
    
    def init_ui(self):
        """Initialize navbar UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top Bar
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Main Navigation
        main_nav = self.create_main_nav()
        main_layout.addWidget(main_nav)
        
        self.setLayout(main_layout)
    
    def create_top_bar(self):
        """Create top bar with quick actions"""
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #f8f9fa; border-bottom: 1px solid #e0e0e0;")
        top_bar.setFixedHeight(40)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(4)
        
        # Left actions
        self.theme_btn = self.create_action_button("🌙", "Toggle Theme")
        layout.addWidget(self.theme_btn)
        
        self.login_btn = self.create_action_button("Login", "Login")
        layout.addWidget(self.login_btn)
        
        self.signup_btn = self.create_action_button("Signup", "Signup")
        layout.addWidget(self.signup_btn)
        
        self.dashboard_btn = self.create_action_button("Dashboard", "Dashboard", active=True)
        layout.addWidget(self.dashboard_btn)
        
        self.upload_btn = self.create_action_button("Upload Image", "Upload")
        layout.addWidget(self.upload_btn)
        
        self.results_btn = self.create_action_button("Results", "Results")
        layout.addWidget(self.results_btn)
        
        self.report_btn = self.create_action_button("Report", "Report")
        layout.addWidget(self.report_btn)
        
        layout.addStretch()
        
        return top_bar
    
    def create_main_nav(self):
        """Create main navigation bar"""
        main_nav = QWidget()
        main_nav.setStyleSheet("background-color: white; border-bottom: 1px solid #e0e0e0;")
        main_nav.setFixedHeight(50)
        
        layout = QHBoxLayout(main_nav)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)
        
        # Brand section (left side)
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(12)
        
        # Logo
        logo = QLabel("F")
        logo.setStyleSheet("""
            QLabel {
                background-color: #007a8c;
                color: white;
                width: 24px;
                height: 24px;
                border-radius: 4px;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
            }
        """)
        logo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(28, 28)
        brand_layout.addWidget(logo)
        
        # Brand name
        brand_name = QLabel("FIVORA")
        brand_name.setFont(QFont("Segoe UI", 16, QFont.Bold))
        brand_name.setStyleSheet("color: #333;")
        brand_layout.addWidget(brand_name)
        
        # Navigation links
        nav_link_layout = QHBoxLayout()
        nav_link_layout.setSpacing(20)
        nav_link_layout.setContentsMargins(20, 0, 0, 0)
        
        self.monitor_btn = self.create_nav_link("Monitor", active=True)
        nav_link_layout.addWidget(self.monitor_btn)
        
        self.reports_nav_btn = self.create_nav_link("Reports")
        nav_link_layout.addWidget(self.reports_nav_btn)
        
        self.history_btn = self.create_nav_link("History")
        nav_link_layout.addWidget(self.history_btn)
        
        brand_layout.addLayout(nav_link_layout)
        layout.addLayout(brand_layout)
        
        # Status section (right side)
        layout.addStretch()
        
        # Online status pill
        status_bubble = QWidget()
        status_bubble.setFixedHeight(24)
        status_layout = QHBoxLayout(status_bubble)
        status_layout.setContentsMargins(10, 4, 10, 4)
        status_layout.setSpacing(5)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet("color: #22c55e; font-size: 10px;")
        status_layout.addWidget(status_dot)
        
        status_text = QLabel("SYSTEM: ONLINE")
        status_text.setFont(QFont("Segoe UI", 10, QFont.Bold))
        status_text.setStyleSheet("color: #22c55e;")
        status_layout.addWidget(status_text)
        
        status_bubble.setStyleSheet("""
            QWidget {
                background-color: #f0fdf4;
                border: 1px solid #dcfce7;
                border-radius: 12px;
            }
        """)
        layout.addWidget(status_bubble)
        
        # Notification bell
        bell = QLabel("🔔")
        bell.setFont(QFont("Segoe UI", 14))
        layout.addWidget(bell)
        layout.addSpacing(15)
        
        # User info
        user_info = QLabel(f"👤 {self.user_name}")
        user_info.setFont(QFont("Segoe UI", 11))
        user_info.setStyleSheet("color: #666; border-left: 1px solid #ddd; padding-left: 15px;")
        layout.addWidget(user_info)
        
        return main_nav
    
    def create_action_button(self, text, tooltip, active=False):
        """Create action button (top bar)"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 11))
        btn.setCursor(Qt.PointingHandCursor)
        
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #00bcd4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00acc1;
                }
                QPushButton:pressed {
                    background-color: #009fb7;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #eee;
                    color: #555;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #ddd;
                }
                QPushButton:pressed {
                    background-color: #ccc;
                }
            """)
        
        btn.setFixedHeight(30)
        btn.setToolTip(tooltip)
        return btn
    
    def create_nav_link(self, text, active=False):
        """Create navigation link button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 13))
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                color: #666;
                border: none;
                background: transparent;
                padding: 5px 0;
                border-bottom: 2px solid transparent;
            }
            QPushButton:hover {
                color: #00bcd4;
            }
        """)
        
        if active:
            btn.setStyleSheet("""
                QPushButton {
                    color: #00bcd4;
                    border: none;
                    background: transparent;
                    padding: 5px 0;
                    border-bottom: 2px solid #00bcd4;
                    font-weight: bold;
                }
            """)
        
        return btn
    
    def get_stylesheet(self):
        """Return navbar stylesheet"""
        return """
            QWidget {
                background-color: white;
            }
            QLabel {
                color: #333;
            }
        """
    
    def set_user_name(self, name):
        """Update user name in navbar"""
        self.user_name = name
