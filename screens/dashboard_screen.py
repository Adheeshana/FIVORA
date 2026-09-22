"""
Dashboard Screen - FIVORA Fabric Inspection System
Main fabric inspection and monitoring interface
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
                             QProgressBar, QGraphicsView, QGraphicsScene)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush
# from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis  # Not available in PyQt5
from PyQt5.QtCore import Qt as QtCore_Qt
from components.navbar import Navbar
import random
from datetime import datetime


class DashboardScreen(QWidget):
    logout_clicked = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.scan_running = False
        self.init_ui()
    
    def init_ui(self):
        """Initialize dashboard UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add modern navbar
        navbar = Navbar(user_name=self.user_data['full_name'])
        navbar.logout_clicked.connect(self.on_logout)
        main_layout.addWidget(navbar)
        
        # Content area with tabs
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left panel - Fabric scan display
        left_panel = self.create_scan_panel()
        content_layout.addLayout(left_panel, 3)
        
        # Right panel - Control panel
        right_panel = self.create_control_panel()
        content_layout.addLayout(right_panel, 1)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        self.setLayout(main_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
    
    def create_scan_panel(self):
        """Create scan panel UI"""
        panel_layout = QVBoxLayout()
        
        # Scan Canvas
        self.scan_canvas = FabricScanCanvas()
        panel_layout.addWidget(self.scan_canvas, 5)
        
        # Progress bar
        progress_label = QLabel("Scan Progress:")
        progress_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        panel_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #e5e5e5;
                border-radius: 4px;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #0066cc;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        panel_layout.addWidget(self.progress_bar)
        
        # Stats display
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        # Defects stat
        defects_layout = QVBoxLayout()
        defects_label = QLabel("Defects Detected")
        defects_label.setFont(QFont("Segoe UI", 9))
        defects_label.setStyleSheet("color: #999;")
        self.defects_value = QLabel("0")
        self.defects_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.defects_value.setStyleSheet("color: #d9534f;")
        defects_layout.addWidget(defects_label)
        defects_layout.addWidget(self.defects_value)
        stats_layout.addLayout(defects_layout)
        
        # Confidence stat
        confidence_layout = QVBoxLayout()
        confidence_label = QLabel("Confidence")
        confidence_label.setFont(QFont("Segoe UI", 9))
        confidence_label.setStyleSheet("color: #999;")
        self.confidence_value = QLabel("0%")
        self.confidence_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.confidence_value.setStyleSheet("color: #5cb85c;")
        confidence_layout.addWidget(confidence_label)
        confidence_layout.addWidget(self.confidence_value)
        stats_layout.addLayout(confidence_layout)
        
        # Quality stat
        quality_layout = QVBoxLayout()
        quality_label = QLabel("Quality Score")
        quality_label.setFont(QFont("Segoe UI", 9))
        quality_label.setStyleSheet("color: #999;")
        self.quality_value = QLabel("0")
        self.quality_value.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.quality_value.setStyleSheet("color: #0066cc;")
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_value)
        stats_layout.addLayout(quality_layout)
        
        stats_layout.addStretch()
        panel_layout.addLayout(stats_layout)
        
        return panel_layout
    
    def create_control_panel(self):
        """Create control panel UI"""
        panel_layout = QVBoxLayout()
        panel_layout.setSpacing(15)
        
        # Control panel header
        control_label = QLabel("CONTROLS")
        control_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        control_label.setStyleSheet("color: #666;")
        panel_layout.addWidget(control_label)
        
        # Start Scan Button
        self.start_button = QPushButton("▶ START SCAN")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QPushButton:pressed {
                background-color: #398439;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.start_button.setFixedHeight(45)
        self.start_button.clicked.connect(self.on_start_scan)
        panel_layout.addWidget(self.start_button)
        
        # Quality Gauge
        gauge_label = QLabel("Quality Gauge:")
        gauge_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        gauge_label.setStyleSheet("color: #666;")
        panel_layout.addWidget(gauge_label)
        
        self.quality_gauge = QualityGaugeWidget()
        panel_layout.addWidget(self.quality_gauge)
        
        # Accept/Reject Buttons
        self.accept_button = QPushButton("✓ ACCEPT ROLL")
        self.accept_button.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.accept_button.setFixedHeight(40)
        self.accept_button.clicked.connect(lambda: self.on_accept_reject("accept"))
        self.accept_button.setEnabled(False)
        panel_layout.addWidget(self.accept_button)
        
        self.reject_button = QPushButton("✕ REJECT ROLL")
        self.reject_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.reject_button.setFixedHeight(40)
        self.reject_button.clicked.connect(lambda: self.on_accept_reject("reject"))
        self.reject_button.setEnabled(False)
        panel_layout.addWidget(self.reject_button)
        
        panel_layout.addStretch()
        
        # Setup timer for scan progress
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan_progress)
        self.scan_progress = 0
        
        return panel_layout
    
    def on_start_scan(self):
        """Start fabric scan"""
        if not self.scan_running:
            self.scan_running = True
            self.scan_progress = 0
            self.start_button.setEnabled(False)
            self.accept_button.setEnabled(False)
            self.reject_button.setEnabled(False)
            self.progress_bar.setValue(0)
            self.scan_timer.start(100)
    
    def update_scan_progress(self):
        """Update scan progress"""
        self.scan_progress += random.randint(5, 15)
        
        if self.scan_progress >= 100:
            self.scan_progress = 100
            self.scan_timer.stop()
            self.scan_running = False
            self.start_button.setEnabled(True)
            self.accept_button.setEnabled(True)
            self.reject_button.setEnabled(True)
        
        self.progress_bar.setValue(self.scan_progress)
        
        # Generate scan metrics
        if self.scan_running:
            defects = random.randint(0, 5)
            confidence = random.randint(70, 99)
            quality_score = random.randint(60, 100)
            
            self.defects_value.setText(str(defects))
            self.confidence_value.setText(f"{confidence}%")
            self.quality_value.setText(str(quality_score))
            self.quality_gauge.set_value(quality_score)
            self.scan_canvas.update()
    
    def on_accept_reject(self, action):
        """Handle accept/reject button click"""
        if action == "accept":
            QMessageBox.information(self, "Success", "Roll accepted and logged!")
        else:
            QMessageBox.information(self, "Success", "Roll rejected and logged!")
        
        # Reset controls
        self.start_button.setEnabled(True)
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.scan_canvas.reset()
    
    def on_logout(self):
        """Handle logout"""
        self.logout_clicked.emit()


class FabricScanCanvas(QWidget):
    """Custom widget to display fabric scan with defect highlighting"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white; border-radius: 4px; border: 1px solid #ddd;")
    
    def paintEvent(self, event):
        """Paint fabric scan visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw fabric background
        painter.fillRect(self.rect(), QColor(245, 245, 245))
        
        # Draw fabric pattern
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        for i in range(0, self.width(), 20):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 20):
            painter.drawLine(0, i, self.width(), i)
        
        # Draw random defects (simulation)
        painter.setPen(QPen(QColor(217, 83, 79), 2))
        painter.setBrush(QBrush(QColor(217, 83, 79, 100)))
        
        import random
        random.seed(42)
        for _ in range(random.randint(1, 5)):
            x = random.randint(50, self.width() - 50)
            y = random.randint(50, self.height() - 50)
            painter.drawEllipse(x, y, 30, 30)
    
    def reset(self):
        """Reset canvas"""
        self.update()


class QualityGaugeWidget(QWidget):
    """Custom widget to display quality score as a circular gauge"""
    
    def __init__(self):
        super().__init__()
        self.value = 0
        self.setMinimumHeight(120)
    
    def set_value(self, value):
        """Set gauge value (0-100)"""
        self.value = max(0, min(100, value))
        self.update()
    
    def paintEvent(self, event):
        """Paint quality gauge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center and size
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 2 - 10
        
        # Draw background circle
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Draw filled arc based on value
        painter.setPen(QPen(QColor(0, 102, 204), 8))
        start_angle = 90 * 16  # Start from top
        arc_angle = -int((self.value / 100) * 360 * 16)  # Clockwise
        painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2,
                       start_angle, arc_angle)
        
        # Draw center circle
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        center_radius = radius - 15
        painter.drawEllipse(center_x - center_radius, center_y - center_radius,
                           center_radius * 2, center_radius * 2)
        
        # Draw value text
        painter.setPen(QColor(51, 51, 51))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        text = f"{self.value}%"
        text_rect = painter.fontMetrics().boundingRect(text)
        painter.drawText(center_x - text_rect.width() // 2,
                        center_y + text_rect.height() // 3, text)
