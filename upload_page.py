"""
Upload Page View & Controller: Manages image file selection and camera capturing workflows
conforming to Functional Requirements (FR 11, FR 12, FR 13, FR 14).
"""
import os
import cv2
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from validator import Validator

class UploadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setStyleSheet("background-color: #f8fafc;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header Section
        header_layout = QHBoxLayout()
        back_btn = QPushButton("←")
        back_btn.setStyleSheet("background: transparent; border: none; font-size: 22px; color: #475569; font-weight: bold;")
        back_btn.setFixedSize(30, 30)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(lambda: self.parent.switch_page(2)) # Go to Dashboard
        
        title_layout = QVBoxLayout()
        title = QLabel("Real-time Analysis")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0f172a;")
        subtitle = QLabel("Upload or capture fabric image for defect detection")
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(back_btn)
        header_layout.addSpacing(10)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        main_layout.addSpacing(30)

        # Cards Layout (Upload / Capture)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        
        # --- 1. UPLOAD CARD (FR 11, FR 12) ---
        upload_card = QFrame()
        upload_card.setStyleSheet("QFrame { background: white; border: 1px solid #cbd5e1; border-radius: 12px; }")
        upload_card.setFixedSize(380, 220)
        u_lay = QVBoxLayout(upload_card)
        u_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_upload_icon = QPushButton("↑")
        self.btn_upload_icon.setFixedSize(64, 64)
        self.btn_upload_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upload_icon.setStyleSheet("QPushButton { background-color: #e0f2fe; color: #0ea5e9; border-radius: 32px; font-size: 28px; font-weight: bold; border: none; }")
        self.btn_upload_icon.clicked.connect(self.browse_file) # FR 11
        
        u_lay.addWidget(self.btn_upload_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        u_lay.addWidget(QLabel("Upload Image", styleSheet="font-size: 15px; font-weight: bold; color: #0f172a; border: none;"), alignment=Qt.AlignmentFlag.AlignCenter)
        u_lay.addWidget(QLabel("Select a fabric image from your device", styleSheet="color: #475569; font-size: 12px; border: none;"), alignment=Qt.AlignmentFlag.AlignCenter)
        
        # --- 2. CAPTURE CARD (FR 13, FR 14) ---
        capture_card = QFrame()
        capture_card.setStyleSheet("QFrame { background: white; border: 1px solid #cbd5e1; border-radius: 12px; }")
        capture_card.setFixedSize(380, 220)
        c_lay = QVBoxLayout(capture_card)
        c_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_capture_icon = QPushButton("📷")
        self.btn_capture_icon.setFixedSize(64, 64)
        self.btn_capture_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture_icon.setStyleSheet("QPushButton { background-color: #e0f2fe; color: #0ea5e9; border-radius: 32px; font-size: 24px; border: none; }")
        self.btn_capture_icon.clicked.connect(self.trigger_camera) # FR 13, 14
        
        c_lay.addWidget(self.btn_capture_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(QLabel("Capture Image", styleSheet="font-size: 15px; font-weight: bold; color: #0f172a; border: none;"), alignment=Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(QLabel("Use camera to capture fabric in real-time", styleSheet="color: #475569; font-size: 12px; border: none;"), alignment=Qt.AlignmentFlag.AlignCenter)

        cards_layout.addStretch()
        cards_layout.addWidget(upload_card)
        cards_layout.addWidget(capture_card)
        cards_layout.addStretch()
        main_layout.addLayout(cards_layout)

    def browse_file(self):
        """FR 11 & FR 12: Open File Picker and Receive Uploaded Image File with validations (Hansani FR 18-22)."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Fabric Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Validate image before passing to dashboard (Hansani's validation module)
            is_valid, message = Validator.validate_image_file(file_path)
            if not is_valid:
                QMessageBox.critical(self, "Validation Error", message) # FR 22
                return
            
            dashboard = self.parent.pages.widget(2)
            dashboard.load_custom_image(file_path)
            self.parent.switch_page(2)

    def trigger_camera(self):
        """FR 13 & FR 14: Start Camera Preview and Capture Frame as File."""
        cap = cv2.VideoCapture(0) # Open default industrial camera / webcam
        if not cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Handle Camera Permission Denied Error: Could not open camera.") # FR 50
            return
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            temp_path = "temp_captured_fabric.jpg"
            cv2.imwrite(temp_path, frame) # Save captured frame as file
            
            # Validate captured image
            is_valid, message = Validator.validate_image_file(temp_path)
            if not is_valid:
                QMessageBox.critical(self, "Validation Error", message) # FR 22
                return

            dashboard = self.parent.pages.widget(2)
            dashboard.load_custom_image(temp_path)
            self.parent.switch_page(2)
        else:
            QMessageBox.warning(self, "Capture Error", "Failed to capture frame from camera feed.")