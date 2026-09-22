import os
import re
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor


def clean_notification(message, fallback="Please try again."):
    """Keep notifications short and useful for non-technical users."""
    text = re.sub(r"\s+", " ", str(message or "")).strip()
    if not text:
        return fallback
    technical_markers = ("traceback", "mysql", "database error", "exception", "errno")
    if any(marker in text.lower() for marker in technical_markers):
        return fallback
    return text if len(text) <= 160 else f"{text[:157].rstrip()}..."

class ModernDialog(QDialog):
    """
    A sleek, modern, professional modal dialog matching FIVORA's dark/light theme.
    Supports success, warning, error, and info styles with custom badges and action buttons.
    """
    def __init__(self, parent=None, title="Success", message="", 
                 dialog_type="success", button_text="OK", is_dark=True):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMaximumWidth(460)

        self.dialog_type = dialog_type.lower()
        self.is_dark = is_dark
        self.drag_position = QPoint()

        # Main layout
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)

        # Card container
        self.card = QFrame()
        self.card.setObjectName("dialogCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(16)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        if self.is_dark:
            shadow.setColor(QColor(0, 0, 0, 180))
        else:
            shadow.setColor(QColor(15, 23, 42, 60))
        self.card.setGraphicsEffect(shadow)

        # Top Bar (Status Pill + Close Button)
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        # Badge pill
        self.badge_lbl = QLabel()
        self.badge_lbl.setFixedHeight(24)
        self.badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Close button (X)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(28, 28)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.reject)

        top_bar.addWidget(self.badge_lbl, alignment=Qt.AlignmentFlag.AlignLeft)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_close, alignment=Qt.AlignmentFlag.AlignRight)
        card_layout.addLayout(top_bar)

        # Icon + Title Section
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(12)

        # Icon Circle
        self.icon_lbl = QLabel()
        self.icon_lbl.setFixedSize(68, 68)
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        self.title_lbl = QLabel(title)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setWordWrap(True)
        header_layout.addWidget(self.title_lbl)

        # Message Body
        self.msg_lbl = QLabel(clean_notification(message))
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_lbl.setWordWrap(True)
        header_layout.addWidget(self.msg_lbl)

        card_layout.addLayout(header_layout)

        # Action Button
        self.btn_action = QPushButton(button_text)
        self.btn_action.setFixedHeight(44)
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self.accept)
        self.btn_action.setDefault(True)
        self.btn_action.setFocus()
        card_layout.addWidget(self.btn_action)

        root_layout.addWidget(self.card)

        # Apply styles
        self.apply_theme()

        # Center relative to parent if available
        if parent:
            target_parent = parent.window() if hasattr(parent, 'window') else parent
            if target_parent and target_parent.isVisible():
                p_geo = target_parent.geometry()
                self.adjustSize()
                x = p_geo.x() + (p_geo.width() - self.width()) // 2
                y = p_geo.y() + (p_geo.height() - self.height()) // 2
                self.move(max(0, x), max(0, y))

    def apply_theme(self):
        # Color palettes
        if self.dialog_type == "success":
            accent_color = "#10b981"       # Emerald green
            accent_hover = "#059669"
            accent_light = "rgba(16, 185, 129, 0.15)"
            accent_border = "rgba(16, 185, 129, 0.40)"
            icon_char = "✓"
            badge_text = " SUCCESSFUL "
        elif self.dialog_type == "warning":
            accent_color = "#f59e0b"       # Amber
            accent_hover = "#d97706"
            accent_light = "rgba(245, 158, 11, 0.15)"
            accent_border = "rgba(245, 158, 11, 0.40)"
            icon_char = "!"
            badge_text = " ATTENTION "
        elif self.dialog_type == "error":
            accent_color = "#ef4444"       # Red
            accent_hover = "#dc2626"
            accent_light = "rgba(239, 68, 68, 0.15)"
            accent_border = "rgba(239, 68, 68, 0.40)"
            icon_char = "✕"
            badge_text = " ERROR "
        else: # info
            accent_color = "#0ea5e9"       # Cyan blue
            accent_hover = "#0284c7"
            accent_light = "rgba(14, 165, 233, 0.15)"
            accent_border = "rgba(14, 165, 233, 0.40)"
            icon_char = "ℹ"
            badge_text = " INFO "

        self.badge_lbl.setText(f"  {badge_text}  ")
        self.icon_lbl.setText(icon_char)

        if self.is_dark:
            bg_card = "#111827"
            border_card = "#1e293b"
            title_color = "#ffffff"
            text_color = "#94a3b8"
            close_bg = "transparent"
            close_hover = "#1e293b"
            close_color = "#64748b"
        else:
            bg_card = "#ffffff"
            border_card = "#e2e8f0"
            title_color = "#0f172a"
            text_color = "#64748b"
            close_bg = "transparent"
            close_hover = "#f1f5f9"
            close_color = "#94a3b8"

        self.card.setStyleSheet(f"""
            QFrame#dialogCard {{
                background-color: {bg_card};
                border: 1px solid {border_card};
                border-radius: 16px;
            }}
        """)

        self.badge_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {accent_light};
                color: {accent_color};
                border: 1px solid {accent_border};
                border-radius: 12px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.5px;
                padding-left: 6px;
                padding-right: 6px;
            }}
        """)

        self.btn_close.setStyleSheet(f"""
            QPushButton {{
                background-color: {close_bg};
                color: {close_color};
                border: none;
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {close_hover};
                color: {'#ffffff' if self.is_dark else '#0f172a'};
            }}
        """)

        self.icon_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {accent_light};
                color: {accent_color};
                border: 2px solid {accent_border};
                border-radius: 34px;
                font-size: 32px;
                font-weight: bold;
            }}
        """)

        self.title_lbl.setStyleSheet(f"""
            QLabel {{
                color: {title_color};
                font-size: 18px;
                font-weight: 700;
            }}
        """)

        self.msg_lbl.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                line-height: 1.5;
                margin-top: 2px;
                margin-bottom: 6px;
            }}
        """)

        self.btn_action.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {accent_hover};
            }}
        """)

    # Window dragging support for frameless dialog
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

def show_success_dialog(parent, title="Account Created Successfully!", 
                        message="Your inspector account is ready.\nPlease sign in with your credentials to access the system.", 
                        button_text="CONTINUE TO SIGN IN", is_dark=True):
    """Convenience helper to show a modern success popup."""
    dlg = ModernDialog(parent=parent, title=title, message=message, 
                       dialog_type="success", button_text=button_text, is_dark=is_dark)
    return dlg.exec()

def show_message_dialog(parent, title="", message="", dialog_type="info", 
                        button_text="OK", is_dark=True):
    """Convenience helper to show a modern styled popup."""
    dlg = ModernDialog(parent=parent, title=title, message=message, 
                       dialog_type=dialog_type, button_text=button_text, is_dark=is_dark)
    return dlg.exec()
