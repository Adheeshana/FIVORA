import os
import cv2
import time
import shutil
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
    QFileDialog, QLineEdit, QProgressBar, QGroupBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from validator import validate_image_file
from config import DEFAULT_CAMERA_URL, SUPPORTED_EXTENSIONS, MAX_FILE_SIZE_MB
from custom_dialog import show_message_dialog


class CaptureThread(QThread):
    progress = pyqtSignal(str)
    finished_capture = pyqtSignal(list)

    def __init__(self, camera_source=0):
        super().__init__()
        self.camera_source = camera_source 

    def run(self):
        cap = cv2.VideoCapture(self.camera_source)
        if not cap.isOpened():
            self.progress.emit("ERROR: Camera permission denied or stream unavailable.")
            self.finished_capture.emit([]) 
            return

        captured_files = []
        start_time = time.time()
        self.progress.emit("Connecting to Camera Stream & Initiating Conveyor Capture...")
        
        while time.time() - start_time < 30: # 30-sec acquisition window
            ret, frame = cap.read()
            if ret:
                temp_path = f"temp_conveyor_{len(captured_files)}.jpg"
                cv2.imwrite(temp_path, frame)
                captured_files.append(temp_path)
                self.progress.emit(f"Acquiring Stream Frames... {len(captured_files)} frames recorded (~1 FPS)")
            else:
                self.progress.emit("Stream interruption detected. Reconnecting...")
                break
            time.sleep(1.0) 
            
        cap.release()
        self.finished_capture.emit(captured_files)


class UploadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.selected_files = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # Title Section
        header_vbox = QVBoxLayout()
        self.title = QLabel("INSPECTION ACQUISITION CONTROLLER")
        self.title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")
        self.subtitle = QLabel("Configure real-time camera stream connections or queue batch fabric sample images")
        self.subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        header_vbox.addWidget(self.title)
        header_vbox.addWidget(self.subtitle)
        main_layout.addLayout(header_vbox)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # ----------------------------------------------------
        # CARD A — CAMERA & STREAM CONFIGURATION
        # ----------------------------------------------------
        self.card_cam = QGroupBox("CARD A — CAMERA & STREAM CONFIGURATION")
        cam_lay = QVBoxLayout(self.card_cam)
        cam_lay.setSpacing(10)

        cam_grid1 = QHBoxLayout()
        cam_grid1.addWidget(QLabel("Camera Name:"))
        self.input_cam_name = QLineEdit("QC Conveyor Camera 1")
        cam_grid1.addWidget(self.input_cam_name)
        cam_lay.addLayout(cam_grid1)

        cam_grid2 = QHBoxLayout()
        cam_grid2.addWidget(QLabel("Stream URL:"))
        self.input_cam_url = QLineEdit(DEFAULT_CAMERA_URL)
        cam_grid2.addWidget(self.input_cam_url)
        cam_lay.addLayout(cam_grid2)
        
        ports_lay = QHBoxLayout()
        ports_lay.addWidget(QLabel("HTTP Port:"))
        self.spin_http = QSpinBox()
        self.spin_http.setMaximum(65535)  
        self.spin_http.setValue(8080)    
        ports_lay.addWidget(self.spin_http)

        ports_lay.addWidget(QLabel("RTSP Port:"))
        self.spin_rtsp = QSpinBox()
        self.spin_rtsp.setMaximum(65535)  
        self.spin_rtsp.setValue(8080)
        ports_lay.addWidget(self.spin_rtsp)
        
        cam_lay.addLayout(ports_lay)

        btn_grid = QHBoxLayout()
        self.btn_test_conn = QPushButton("⚡ TEST CONNECTION")
        self.btn_connect_cam = QPushButton("▶ CONNECT CAMERA")
        
        for b in [self.btn_test_conn, self.btn_connect_cam]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("background-color: #0ea5e9; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        
        self.btn_test_conn.clicked.connect(self.test_camera_connection)
        self.btn_connect_cam.clicked.connect(self.start_camera_capture)

        btn_grid.addWidget(self.btn_test_conn)
        btn_grid.addWidget(self.btn_connect_cam)
        cam_lay.addLayout(btn_grid)
        cam_lay.addStretch()

        cards_layout.addWidget(self.card_cam, 1)

        # ----------------------------------------------------
        # CARD B — OFFLINE BATCH INSPECTION
        # ----------------------------------------------------
        self.card_batch = QGroupBox("CARD B — BATCH IMAGE INSPECTION")
        batch_lay = QVBoxLayout(self.card_batch)
        batch_lay.setSpacing(12)

        self.btn_browse = QPushButton("📁 Browse Image Files / Select Folder")
        self.btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_browse.setStyleSheet("background-color: #1e293b; color: #00A3FF; font-weight: bold; border: 2px dashed #00A3FF; border-radius: 8px; padding: 16px; font-size: 13px;")
        self.btn_browse.clicked.connect(self.browse_batch_files)

        self.lbl_selected_count = QLabel("SELECTED IMAGES: 0")
        self.lbl_selected_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_selected_count.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")

        self.lbl_formats = QLabel("Supported Formats: JPG, JPEG, PNG, BMP, TIFF (Max 5MB)")
        self.lbl_formats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_formats.setStyleSheet("font-size: 11px; color: #64748b;")

        self.btn_start_batch = QPushButton("🚀 START BATCH INSPECTION")
        self.btn_start_batch.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start_batch.setStyleSheet("background-color: #10b981; color: white; font-weight: bold; padding: 12px; border-radius: 6px; font-size: 14px;")
        self.btn_start_batch.clicked.connect(self.process_batch_queue)

        batch_lay.addWidget(self.btn_browse)
        batch_lay.addWidget(self.lbl_selected_count)
        batch_lay.addWidget(self.lbl_formats)
        batch_lay.addWidget(self.btn_start_batch)
        batch_lay.addStretch()

        cards_layout.addWidget(self.card_batch, 1)
        main_layout.addLayout(cards_layout)

        # Status & Progress Section
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { background: #1e293b; border-radius: 6px; } QProgressBar::chunk { background: #10b981; border-radius: 6px; }")

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #0ea5e9;")

        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.status_label)

        self.apply_theme(True)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            style_box = "QGroupBox { font-size: 11px; font-weight: bold; color: #0ea5e9; border: 1px solid #1e293b; border-radius: 10px; padding-top: 18px; background: #111827; } QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }"
            self.card_cam.setStyleSheet(style_box)
            self.card_batch.setStyleSheet(style_box)
            style_input = "QLineEdit, QSpinBox { background: #1e293b; border: 1px solid #334155; border-radius: 6px; color: white; padding: 6px; }"
            self.input_cam_name.setStyleSheet(style_input)
            self.input_cam_url.setStyleSheet(style_input)
            self.spin_http.setStyleSheet(style_input)
            self.spin_rtsp.setStyleSheet(style_input)

    def test_camera_connection(self):
        url = self.input_cam_url.text().strip()
        self.status_label.setText(f"Testing stream connection to '{url}'...")
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            if ret:
                show_message_dialog(self, "Camera Ready", "The camera connection is working.", "success", "DONE", getattr(self.parent, 'is_dark_mode', True))
                self.status_label.setText("Camera Stream Status: ONLINE")
                return
        show_message_dialog(self, "Connection Unavailable", "The camera could not be reached. Check the stream address and try again.", "warning", "OK", getattr(self.parent, 'is_dark_mode', True))
        self.status_label.setText("Camera Stream Status: OFFLINE")

    def start_camera_capture(self):
        url = self.input_cam_url.text().strip()
        self.capture_thread = CaptureThread(camera_source=url)
        self.capture_thread.progress.connect(self.status_label.setText)
        self.capture_thread.finished_capture.connect(self.on_capture_complete)
        self.capture_thread.start()

    def on_capture_complete(self, files):
        if files:
            self.selected_files = files
            self.lbl_selected_count.setText(f"SELECTED IMAGES: {len(files)}")
            self.process_batch_queue()
        else:
            show_message_dialog(self, "Capture Unavailable", "No images were captured. Check the camera and try again.", "error", "CLOSE", getattr(self.parent, 'is_dark_mode', True))

    def browse_batch_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Fabric Images", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff)")
        if paths:
            self.selected_files = paths
            self.lbl_selected_count.setText(f"SELECTED IMAGES: {len(paths)}")

    def process_batch_queue(self):
        if not self.selected_files:
            show_message_dialog(self, "No Images Selected", "Choose image files or capture frames before starting.", "warning", "OK", getattr(self.parent, 'is_dark_mode', True))
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        total = len(self.selected_files)

        batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_dir = os.path.join("captured_batches", batch_id)
        os.makedirs(batch_dir, exist_ok=True)

        valid_files = []
        for idx, fp in enumerate(self.selected_files, start=1):
            is_valid, msg = validate_image_file(fp)
            if is_valid:
                ext = os.path.splitext(fp)[1]
                dest_path = os.path.join(batch_dir, f"{batch_id}_img_{idx}{ext}")
                if "temp_conveyor_" in fp:
                    os.rename(fp, dest_path)
                else:
                    shutil.copy(fp, dest_path)
                valid_files.append(dest_path)

            progress_pct = int((idx / total) * 100)
            self.progress_bar.setValue(progress_pct)
            self.status_label.setText(f"Processing Batch Queue: {idx} / {total} ({progress_pct}%)")

        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Batch '{batch_id}' Processed ({len(valid_files)} valid images). Loading Workstation...")

        dashboard = self.parent.pages.widget(2)
        if hasattr(dashboard, 'process_image_batch'):
            dashboard.process_image_batch(batch_id, valid_files)

        self.parent.switch_page(2)