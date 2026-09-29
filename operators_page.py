import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt
from database import get_all_users, update_user_status, get_session_logs
from custom_dialog import show_message_dialog

class OperatorsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.is_dark_mode = True

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Scroll area එකක් දැම්මා සම්පූර්ණ පිටුවම ලස්සනට Scroll වෙන්න
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        container = QWidget()
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)

        # Header Title
        title_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        self.page_title = QLabel("Operator Management")
        self.page_subtitle = QLabel("Review access requests, manage operator accounts, and monitor sign-in activity.")
        title_box.addWidget(self.page_title)
        title_box.addWidget(self.page_subtitle)
        
        self.badge_count = QLabel("0 registered operator(s)")
        title_layout.addLayout(title_box)
        title_layout.addStretch()
        title_layout.addWidget(self.badge_count)
        self.content_layout.addLayout(title_layout)

        # 1. Operators Table Section
        self.table_operators = QTableWidget()
        self.table_operators.setColumnCount(4)
        self.table_operators.setHorizontalHeaderLabels(["OPERATOR", "EMAIL", "STATUS", "ACTION"])
        self.table_operators.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_operators.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_operators.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table_operators.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table_operators.setColumnWidth(2, 140)
        self.table_operators.setColumnWidth(3, 180)
        self.table_operators.setFixedHeight(220)
        self.content_layout.addWidget(self.table_operators)

        # 2. Session Activity Section
        self.session_title = QLabel("Session activity")
        self.content_layout.addWidget(self.session_title)

        self.table_sessions = QTableWidget()
        self.table_sessions.setColumnCount(4)
        self.table_sessions.setHorizontalHeaderLabels(["OPERATOR", "EMAIL", "LOG-IN TIMESTAMP", "LOG-OUT TIMESTAMP"])
        self.table_sessions.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_sessions.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_sessions.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_sessions.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table_sessions.setFixedHeight(250)
        self.content_layout.addWidget(self.table_sessions)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self.apply_theme(True)
        self.refresh_data()

    def refresh_data(self):
        self.load_operators()
        self.load_sessions()

    def load_operators(self):
        users = get_all_users()
        self.table_operators.setRowCount(0)
        self.badge_count.setText(f"{len(users)} registered operator(s)")

        for row_idx, user in enumerate(users):
            self.table_operators.insertRow(row_idx)
            self.table_operators.setRowHeight(row_idx, 45)

            name = f"{user.get('fname', '')} {user.get('lname', '')}".strip() or "N/A"
            email = user.get('email', 'N/A')
            status = str(user.get('status', 'Active')).strip().title()
            user_id = user.get('id')

            item_name = QTableWidgetItem(name)
            item_email = QTableWidgetItem(email)
            item_status = QTableWidgetItem(status)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table_operators.setItem(row_idx, 0, item_name)
            self.table_operators.setItem(row_idx, 1, item_email)
            self.table_operators.setItem(row_idx, 2, item_status)

            # Action Button එක Status එක අනුව වෙනස් කිරීම
            btn_action = QPushButton()
            btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_action.setFixedHeight(30)

            if status.lower() == "active":
                btn_action.setText("Deactivate")
                btn_action.setStyleSheet("QPushButton { background-color: #dc2626; color: white; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; } QPushButton:hover { background-color: #b91c1c; }")
                btn_action.clicked.connect(lambda _, uid=user_id: self.change_status(uid, "Deactivated"))
            else:
                btn_action.setText("Approve")
                btn_action.setStyleSheet("QPushButton { background-color: #059669; color: white; font-weight: bold; border-radius: 4px; border: none; font-size: 11px; } QPushButton:hover { background-color: #047857; }")
                btn_action.clicked.connect(lambda _, uid=user_id: self.change_status(uid, "Active"))

            self.table_operators.setCellWidget(row_idx, 3, btn_action)

    def change_status(self, user_id, new_status):
        success = update_user_status(user_id, new_status)
        if success:
            self.load_operators()
        else:
            show_message_dialog(self, "Error", "Could not update operator status.", "error", "OK", self.is_dark_mode)

    def load_sessions(self):
        logs = get_session_logs() if 'get_session_logs' in globals() or 'get_session_logs' in dir() else []
        try:
            from database import get_session_logs as fetch_logs
            logs = fetch_logs()
        except Exception:
            logs = []

        self.table_sessions.setRowCount(0)
        for row_idx, log in enumerate(logs):
            self.table_sessions.insertRow(row_idx)
            self.table_sessions.setRowHeight(row_idx, 40)

            name = f"{log.get('fname', '')} {log.get('lname', '')}".strip() or log.get('name', 'N/A')
            email = log.get('email', 'N/A')
            login_time = str(log.get('login_time', log.get('signin_time', 'N/A')))
            logout_time = str(log.get('logout_time', log.get('signout_time', 'None')))

            self.table_sessions.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table_sessions.setItem(row_idx, 1, QTableWidgetItem(email))
            self.table_sessions.setItem(row_idx, 2, QTableWidgetItem(login_time))
            self.table_sessions.setItem(row_idx, 3, QTableWidgetItem(logout_time))

    def apply_theme(self, is_dark):
        self.is_dark_mode = is_dark
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: #f8fafc;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #f8fafc;")
            self.page_subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
            self.session_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc; margin-top: 10px;")
            self.badge_count.setStyleSheet("font-size: 12px; font-weight: bold; color: #38bdf8; background: #1e293b; padding: 6px 12px; border-radius: 6px; border: 1px solid #334155;")
            
            table_style = (
                "QTableWidget { background-color: #111827; gridline-color: #1e293b; color: #f8fafc; border: 1px solid #1e293b; border-radius: 8px; }"
                "QHeaderView::section { background-color: #1f2937; color: #94a3b8; font-weight: bold; border: none; padding: 6px; font-size: 11px; }"
                "QTableWidget::item { padding: 5px; border-bottom: 1px solid #1e293b; }"
            )
            self.table_operators.setStyleSheet(table_style)
            self.table_sessions.setStyleSheet(table_style)
        else:
            self.setStyleSheet("background-color: #f4f6f9; color: #0f172a;")
            self.page_title.setStyleSheet("font-size: 22px; font-weight: 900; color: #0f172a;")
            self.page_subtitle.setStyleSheet("font-size: 12px; color: #64748b;")
            self.session_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a; margin-top: 10px;")
            self.badge_count.setStyleSheet("font-size: 12px; font-weight: bold; color: #0369a1; background: #e0f2fe; padding: 6px 12px; border-radius: 6px; border: 1px solid #bae6fd;")
            
            table_style = (
                "QTableWidget { background-color: #ffffff; gridline-color: #e2e8f0; color: #0f172a; border: 1px solid #e2e8f0; border-radius: 8px; }"
                "QHeaderView::section { background-color: #f1f5f9; color: #475569; font-weight: bold; border: none; padding: 6px; font-size: 11px; }"
                "QTableWidget::item { padding: 5px; border-bottom: 1px solid #e2e8f0; }"
            )
            self.table_operators.setStyleSheet(table_style)
            self.table_sessions.setStyleSheet(table_style)