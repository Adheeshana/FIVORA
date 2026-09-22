from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from database import list_operators, update_operator_status, fetch_activity_logs
from custom_dialog import show_message_dialog


class OperatorsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.table = QTableWidget()
        self.activity_table = QTableWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 28, 34, 28)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)
        title_block = QVBoxLayout()
        title_block.setSpacing(3)
        title = QLabel("Operator Management")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Review access requests, manage operator accounts, and monitor sign-in activity.")
        subtitle.setObjectName("pageSubtitle")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        header.addLayout(title_block)
        header.addStretch()

        self.operator_count = QLabel("")
        self.operator_count.setObjectName("countBadge")
        header.addWidget(self.operator_count, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(header)

        self.operator_panel = QFrame()
        self.operator_panel.setObjectName("contentPanel")
        operator_panel_layout = QVBoxLayout(self.operator_panel)
        operator_panel_layout.setContentsMargins(14, 14, 14, 14)
        operator_panel_layout.setSpacing(10)

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Operator", "Email", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 280)
        self.table.setColumnWidth(2, 160)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(230)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        operator_panel_layout.addWidget(self.table)
        layout.addWidget(self.operator_panel)

        activity_header = QHBoxLayout()
        activity_title = QLabel("Session activity")
        activity_title.setObjectName("sectionTitle")
        activity_header.addWidget(activity_title)
        activity_header.addStretch()
        activity_hint = QLabel("Login and logout history")
        activity_hint.setObjectName("sectionHint")
        activity_header.addWidget(activity_hint)
        layout.addLayout(activity_header)

        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Operator", "Email", "Log-in timestamp", "Log-out timestamp"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.activity_table.verticalHeader().setDefaultSectionSize(42)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setShowGrid(False)
        self.activity_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        layout.addWidget(self.activity_table, 1)
        self.apply_theme(True)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("""
                QWidget { background-color: #0b0f19; color: #f8fafc; }
                QLabel#pageTitle { color: #f8fafc; font-size: 24px; font-weight: 800; }
                QLabel#pageSubtitle, QLabel#sectionHint { color: #64748b; font-size: 12px; }
                QLabel#sectionTitle { color: #e2e8f0; font-size: 15px; font-weight: 700; }
                QLabel#countBadge { background-color: #12283a; color: #7dd3fc; border: 1px solid #1e5b7a; border-radius: 14px; padding: 7px 13px; font-size: 12px; font-weight: 700; }
                QFrame#contentPanel { background-color: #111827; border: 1px solid #1e293b; border-radius: 10px; }
            """)
            table_style = "QTableWidget { background-color: #111827; color: #e2e8f0; border: none; outline: none; alternate-background-color: #152033; } QTableWidget::item { padding: 8px 10px; border-bottom: 1px solid #1e293b; }"
            header_style = "QHeaderView::section { background-color: #182235; color: #94a3b8; border: none; border-bottom: 1px solid #334155; padding: 11px 10px; font-size: 10px; font-weight: 800; text-transform: uppercase; }"
        else:
            self.setStyleSheet("""
                QWidget { background-color: #f4f6f9; color: #0f172a; }
                QLabel#pageTitle { color: #0f172a; font-size: 24px; font-weight: 800; }
                QLabel#pageSubtitle, QLabel#sectionHint { color: #64748b; font-size: 12px; }
                QLabel#sectionTitle { color: #334155; font-size: 15px; font-weight: 700; }
                QLabel#countBadge { background-color: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; border-radius: 14px; padding: 7px 13px; font-size: 12px; font-weight: 700; }
                QFrame#contentPanel { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; }
            """)
            table_style = "QTableWidget { background-color: #ffffff; color: #0f172a; border: none; outline: none; alternate-background-color: #f8fafc; } QTableWidget::item { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; }"
            header_style = "QHeaderView::section { background-color: #f1f5f9; color: #64748b; border: none; border-bottom: 1px solid #cbd5e1; padding: 11px 10px; font-size: 10px; font-weight: 800; text-transform: uppercase; }"
        for table in (self.table, self.activity_table):
            table.setStyleSheet(table_style)
            table.horizontalHeader().setStyleSheet(header_style)

    def refresh_data(self):
        operators = list_operators()
        self.operator_count.setText(f"{len(operators)} registered operator(s)")
        self.table.setRowCount(len(operators))
        for row, operator in enumerate(operators):
            name = " ".join(filter(None, [operator.get("fname"), operator.get("lname")])).strip()
            for column, value in enumerate([name, str(operator.get("email", ""))]):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, column, item)

            status = str(operator.get("status", "Pending"))
            status_badge = QLabel("Pending Approval" if status.lower() == "pending" else status)
            status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_badge.setStyleSheet(self.status_badge_style(status))
            self.table.setCellWidget(row, 2, status_badge)

            action_panel = QWidget()
            action_layout = QHBoxLayout(action_panel)
            action_layout.setContentsMargins(10, 7, 10, 7)
            action_layout.setSpacing(10)
            action_layout.addStretch()
            approve = QPushButton("Approve")
            approve.setCursor(Qt.CursorShape.PointingHandCursor)
            approve.setMinimumHeight(32)
            approve.setStyleSheet(self.action_button_style("approve"))
            approve.clicked.connect(lambda _, item=operator: self.change_status(item, "Active"))
            reject = QPushButton("Reject / Deactivate")
            reject.setCursor(Qt.CursorShape.PointingHandCursor)
            reject.setMinimumHeight(32)
            reject.setMinimumWidth(145)
            reject.setStyleSheet(self.action_button_style("reject"))
            reject.clicked.connect(lambda _, item=operator: self.change_status(item, "Deactivated"))
            action_layout.addWidget(approve)
            action_layout.addWidget(reject)
            action_layout.addStretch()
            self.table.setCellWidget(row, 3, action_panel)

        logs = fetch_activity_logs()
        self.activity_table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            values = [log.get("operator_name", ""), log.get("email", ""),
                      str(log.get("login_timestamp", "")), str(log.get("logout_timestamp", "Still logged in"))]
            for column, value in enumerate(values):
                self.activity_table.setItem(row, column, QTableWidgetItem(value))

    def change_status(self, operator, status):
        if update_operator_status(operator.get("id"), operator.get("email", ""), status):
            self.refresh_data()
            return
        show_message_dialog(self, "Update Failed", "The operator status could not be updated.", "error", "OK", self.parent.is_dark_mode)

    @staticmethod
    def status_badge_style(status):
        normalized = status.lower()
        if normalized == "active":
            return "QLabel { background-color: #064e3b; color: #6ee7b7; border: 1px solid #10b981; border-radius: 12px; padding: 6px 12px; font-weight: bold; }"
        if normalized in {"deactivated", "rejected"}:
            return "QLabel { background-color: #3f1d24; color: #fca5a5; border: 1px solid #ef4444; border-radius: 12px; padding: 6px 12px; font-weight: bold; }"
        return "QLabel { background-color: #4a3410; color: #fcd34d; border: 1px solid #f59e0b; border-radius: 12px; padding: 6px 12px; font-weight: bold; }"

    @staticmethod
    def action_button_style(action):
        if action == "approve":
            return "QPushButton { background-color: #059669; color: white; border: 1px solid #10b981; border-radius: 6px; padding: 6px 14px; font-weight: bold; } QPushButton:hover { background-color: #10b981; }"
        return "QPushButton { background-color: #b91c1c; color: white; border: 1px solid #ef4444; border-radius: 6px; padding: 6px 12px; font-weight: bold; } QPushButton:hover { background-color: #ef4444; }"
