"""
Styling Module - FIVORA Fabric Inspection System
Global stylesheet and theming
"""

from PyQt5.QtWidgets import QApplication


def apply_stylesheet(app):
    """Apply global stylesheet to application"""
    
    stylesheet = """
    /* Main Application */
    QMainWindow {
        background-color: #f5f5f5;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0066cc;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 11px;
    }
    
    QPushButton:hover {
        background-color: #0052a3;
    }
    
    QPushButton:pressed {
        background-color: #003d7a;
    }
    
    QPushButton:disabled {
        background-color: #ccc;
        color: #666;
    }
    
    /* Input Fields */
    QLineEdit {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: white;
        font-size: 12px;
    }
    
    QLineEdit:focus {
        border: 2px solid #667eea;
        outline: none;
    }
    
    /* Labels */
    QLabel {
        color: #333;
    }
    
    /* Check Boxes */
    QCheckBox {
        color: #666;
        spacing: 5px;
    }
    
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
    }
    
    QCheckBox::indicator:unchecked {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 3px;
    }
    
    QCheckBox::indicator:checked {
        background-color: #0066cc;
        border: 1px solid #0066cc;
        border-radius: 3px;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: none;
        background-color: #e5e5e5;
        border-radius: 4px;
        height: 8px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #0066cc;
        border-radius: 4px;
    }
    
    /* Scroll Bars */
    QScrollBar:vertical {
        width: 12px;
        background-color: #f5f5f5;
    }
    
    QScrollBar::handle:vertical {
        background-color: #ccc;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #999;
    }
    
    QScrollBar:horizontal {
        height: 12px;
        background-color: #f5f5f5;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #ccc;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #999;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        border: 1px solid #ddd;
    }
    
    QTabBar::tab {
        background-color: #f5f5f5;
        color: #666;
        padding: 8px 20px;
        border: 1px solid #ddd;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        color: #0066cc;
        border-bottom: 3px solid #0066cc;
    }
    
    /* Table Widget */
    QTableWidget {
        background-color: white;
        gridline-color: #ddd;
        border: 1px solid #ddd;
        border-radius: 4px;
    }
    
    QTableWidget::item {
        padding: 8px;
    }
    
    QTableWidget::item:selected {
        background-color: #e6f2ff;
    }
    
    QHeaderView::section {
        background-color: #f9f9f9;
        color: #333;
        padding: 8px;
        border: none;
        border-right: 1px solid #ddd;
        font-weight: bold;
    }
    
    /* Message Boxes */
    QMessageBox QLabel {
        color: #333;
    }
    
    QMessageBox QPushButton {
        min-width: 60px;
    }
    """
    
    # Apply stylesheet to application
    if isinstance(app, QApplication):
        app.setStyleSheet(stylesheet)


def get_color(color_name):
    """Get color by name"""
    colors = {
        'primary': '#0066cc',
        'secondary': '#667eea',
        'success': '#5cb85c',
        'danger': '#d9534f',
        'warning': '#f0ad4e',
        'info': '#5bc0de',
        'light': '#f5f5f5',
        'dark': '#333',
        'white': '#ffffff',
        'gray': '#999'
    }
    return colors.get(color_name, '#0066cc')


def get_font_style(style_name):
    """Get font style"""
    styles = {
        'title': 'font-size: 28px; font-weight: bold;',
        'heading': 'font-size: 18px; font-weight: bold;',
        'subheading': 'font-size: 14px; font-weight: bold;',
        'normal': 'font-size: 12px;',
        'small': 'font-size: 10px;',
    }
    return styles.get(style_name, 'font-size: 12px;')
