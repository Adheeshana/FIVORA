import os
import cv2
import time
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, 
                             QPushButton, QFileDialog, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from validator import validate_image_file

class CaptureThread(QThread):
    progress = pyqtSignal(str)
    finished_capture = pyqtSignal(list)

    def __init__(self, camera_source=0):
        super().__init__()
        self.camera_source = camera_source 

    def run(self):
        cap = cv2.VideoCapture(self.camera_source)
        captured_files = []
        start_time = time.time()
        self.progress.emit("Connecting to Camera & Starting 1-minute capture...")
        
        while time.time() - start_time < 60:
            ret, frame = cap.read()
            if ret:
                temp_path = f"temp_conveyor_{len(captured_files)}.jpg"
                cv2.imwrite(temp_path, frame)
                captured_files.append(temp_path)
                self.progress.emit(f"Capturing... {len(captured_files)} frames (~1 FPS)")
            else:
                self.progress.emit("Failed to grab frame. Check connection.")
                break
            time.sleep(1.0) 
            
        cap.release()
        self.finished_capture.emit(captured_files)

class UploadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 20, 40, 20)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title = QLabel("Image Acquisition & Validation")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.subtitle = QLabel("Upload multiple images or connect Phone Camera for continuous capture")
        
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.subtitle)
        self.main_layout.addSpacing(30)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        
        self.upload_card = QFrame()
        self.upload_card.setFixedSize(380, 220)
        u_lay = QVBoxLayout(self.upload_card)
        
        self.btn_upload_icon = QPushButton("↑")
        self.btn_upload_icon.setFixedSize(64, 64)
        self.btn_upload_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_upload_icon.clicked.connect(self.browse_multiple_files)
        
        self.u_lbl1 = QLabel("Upload Images", alignment=Qt.AlignmentFlag.AlignCenter)
        self.u_lbl2 = QLabel("Select multiple fabric images", alignment=Qt.AlignmentFlag.AlignCenter)
        
        u_lay.addWidget(self.btn_upload_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        u_lay.addWidget(self.u_lbl1)
        u_lay.addWidget(self.u_lbl2)
        
        self.capture_card = QFrame()
        self.capture_card.setFixedSize(380, 220)
        c_lay = QVBoxLayout(self.capture_card)
        
        self.btn_capture_icon = QPushButton("📱")
        self.btn_capture_icon.setFixedSize(64, 64)
        self.btn_capture_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture_icon.clicked.connect(self.start_continuous_capture)
        
        self.c_lbl1 = QLabel("Start Conveyor Capture", alignment=Qt.AlignmentFlag.AlignCenter)
        self.c_lbl2 = QLabel("Connect Phone Camera (1 img/sec for 1 min)", alignment=Qt.AlignmentFlag.AlignCenter)
        
        c_lay.addWidget(self.btn_capture_icon, alignment=Qt.AlignmentFlag.AlignCenter)
        c_lay.addWidget(self.c_lbl1)
        c_lay.addWidget(self.c_lbl2)

        cards_layout.addStretch()
        cards_layout.addWidget(self.upload_card)
        cards_layout.addWidget(self.capture_card)
        cards_layout.addStretch()
        self.main_layout.addLayout(cards_layout)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0ea5e9;")
        self.main_layout.addWidget(self.status_label)

        self.apply_theme(False)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
            self.subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
            self.upload_card.setStyleSheet("QFrame { background: #111827; border: 1px solid #1e293b; border-radius: 12px; }")
            self.capture_card.setStyleSheet("QFrame { background: #111827; border: 1px solid #1e293b; border-radius: 12px; }")
            self.u_lbl1.setStyleSheet("font-size: 15px; font-weight: bold; color: white; border: none;")
            self.u_lbl2.setStyleSheet("color: #94a3b8; font-size: 12px; border: none;")
            self.c_lbl1.setStyleSheet("font-size: 15px; font-weight: bold; color: white; border: none;")
            self.c_lbl2.setStyleSheet("color: #94a3b8; font-size: 12px; border: none;")
            self.btn_upload_icon.setStyleSheet("QPushButton { background-color: #1e293b; color: #0ea5e9; border-radius: 32px; font-size: 28px; font-weight: bold; border: none; }")
            self.btn_capture_icon.setStyleSheet("QPushButton { background-color: #1e293b; color: #0ea5e9; border-radius: 32px; font-size: 24px; border: none; }")
        else:
            self.setStyleSheet("background-color: #f8fafc; color: #0f172a;")
            self.title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0f172a;")
            self.subtitle.setStyleSheet("font-size: 12px; color: #64748b;")
            self.upload_card.setStyleSheet("QFrame { background: white; border: 1px solid #cbd5e1; border-radius: 12px; }")
            self.capture_card.setStyleSheet("QFrame { background: white; border: 1px solid #cbd5e1; border-radius: 12px; }")
            self.u_lbl1.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a; border: none;")
            self.u_lbl2.setStyleSheet("color: #475569; font-size: 12px; border: none;")
            self.c_lbl1.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a; border: none;")
            self.c_lbl2.setStyleSheet("color: #475569; font-size: 12px; border: none;")
            self.btn_upload_icon.setStyleSheet("QPushButton { background-color: #e0f2fe; color: #0ea5e9; border-radius: 32px; font-size: 28px; font-weight: bold; border: none; }")
            self.btn_capture_icon.setStyleSheet("QPushButton { background-color: #e0f2fe; color: #0ea5e9; border-radius: 32px; font-size: 24px; border: none; }")

    def browse_multiple_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Fabric Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_paths:
            self.process_selected_files(file_paths)

    def start_continuous_capture(self):
        text, ok = QInputDialog.getText(self, "Connect Camera", 
                                        "Enter Phone IP Camera URL (e.g. http://192.168.8.100:8080/video)\nOr type '0' to use Laptop Webcam:", 
                                        text="0")
        if not ok: return 
        cam_src = 0 if text.strip() == "0" else text.strip()
        self.btn_capture_icon.setEnabled(False)
        self.btn_upload_icon.setEnabled(False)
        self.capture_thread = CaptureThread(camera_source=cam_src)
        self.capture_thread.progress.connect(self.update_status)
        self.capture_thread.finished_capture.connect(self.on_capture_finished)
        self.capture_thread.start()

    def update_status(self, text):
        self.status_label.setText(text)

    def on_capture_finished(self, captured_files):
        self.btn_capture_icon.setEnabled(True)
        self.btn_upload_icon.setEnabled(True)
        if not captured_files:
            self.status_label.setText("Capture Failed. Please check the Camera URL/Network.")
            return
        self.status_label.setText("Capture complete! Validating images...")
        self.process_selected_files(captured_files)

    def process_selected_files(self, file_paths):
        valid_files = []
        total_images = len(file_paths)
        
        for fp in file_paths:
            is_valid, _ = validate_image_file(fp)
            if is_valid:
                valid_files.append(fp)
            else:
                if "temp_conveyor_" in fp and os.path.exists(fp):
                    os.remove(fp)
                    
        valid_count = len(valid_files)
        if total_images > 0:
            valid_percentage = (valid_count / total_images) * 100
            if valid_percentage < 80.0:
                QMessageBox.warning(self, "Validation Error", f"Only {valid_percentage:.1f}% of images are clear (Need 80%).\nPlease stabilize the camera and retake.")
                self.status_label.setText("")
                for fp in valid_files:
                    if "temp_conveyor_" in fp and os.path.exists(fp):
                        os.remove(fp)
                return

        if not valid_files:
            QMessageBox.warning(self, "Validation Error", "No valid images found!")
            self.status_label.setText("")
            return
            
        self.status_label.setText(f"{valid_percentage:.1f}% images passed. Renaming and Processing...")
        
        # --- Create Batch Folder and Rename Images ---
        batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        batch_dir = os.path.join("captured_batches", batch_id)
        os.makedirs(batch_dir, exist_ok=True)
        
        renamed_files = []
        for idx, fp in enumerate(valid_files):
            ext = os.path.splitext(fp)[1]
            new_filename = f"{batch_id}_img_{idx+1}{ext}"
            new_filepath = os.path.join(batch_dir, new_filename)
            
            if "temp_conveyor_" in fp:
                os.rename(fp, new_filepath)
            else:
                shutil.copy(fp, new_filepath) # If uploaded manually, just copy it
            renamed_files.append(new_filepath)

        dashboard = self.parent.pages.widget(2)
        if hasattr(dashboard, 'process_image_batch'):
            dashboard.process_image_batch(batch_id, renamed_files)
        
        self.status_label.setText("")
        self.parent.switch_page(2)