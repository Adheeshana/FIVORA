import os
import cv2
import json
import random
import time
import numpy as np
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
    QComboBox, QGraphicsView, QGraphicsScene, QLineEdit,
    QProgressBar, QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QRectF
from PyQt6.QtGui import QImage, QPixmap, QColor, QFont

from config import (
    DEFAULT_CAMERA_URL, FABRIC_CATEGORIES, DEFECT_CATEGORIES,
    CLASSIFICATION_THRESHOLD_PERCENT, DEFECT_DETECTION_THRESHOLD_PERCENT
)
from database import save_inspection_record
from custom_dialog import show_message_dialog

# =======================================================
# 1. Persistent AI Engine Thread (Fixes Silent AI Crashes)
# =======================================================
class AIEngineThread(QThread):
    models_loaded_signal = pyqtSignal()
    result_ready = pyqtSignal(dict, dict, str)

    def __init__(self):
        super().__init__()
        self.classifier = None
        self.defect_detector = None
        self.is_running = True
        self.frame_queue = []
        self.img_path_queue = []

    def run(self):
        print("[INFO] AI Engine Thread Started. Loading models safely...")
        try:
            from model_inference import FabricClassifier
            from defect_detector import FabricDefectDetector
            
            self.classifier = FabricClassifier()
            self.defect_detector = FabricDefectDetector()
            self.models_loaded_signal.emit()
            print("[SUCCESS] AI Engine is fully ready for inference.")
        except Exception as e:
            print(f"[ERROR] AI Engine Initialization Failed: {e}")
            return

        while self.is_running:
            if len(self.frame_queue) > 0:
                frame = self.frame_queue.pop(-1)
                path = self.img_path_queue.pop(-1) if self.img_path_queue else None
                
                self.frame_queue.clear()
                self.img_path_queue.clear()
                
                try:
                    defect_res = self.defect_detector.detect(frame)
                    if not path:
                        temp_path = "temp_live_frame.jpg"
                        cv2.imwrite(temp_path, frame)
                        path = temp_path
                        
                    class_res = self.classifier.predict_detailed(path)
                    self.result_ready.emit(class_res, defect_res, path)
                except Exception as e:
                    print(f"[ERROR] AI Inference failed: {e}")
            else:
                time.sleep(0.05)

    def analyze(self, frame, img_path=None):
        if frame is not None:
            self.frame_queue.append(frame.copy())
            self.img_path_queue.append(img_path)

    def stop(self):
        self.is_running = False

# =======================================================
# 2. UI Components
# =======================================================
class MachineVisionCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setStyleSheet("background-color: #0b0f19; border-radius: 8px; border: 1px solid #1e293b;")

        self.placeholder_text = self.scene.addText(
            "CAMERA / IMAGE PREVIEW\n\nStart the camera or upload an image to begin inspection."
        )
        self.placeholder_text.setDefaultTextColor(QColor("#475569"))
        self.placeholder_text.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))

    def set_image(self, pixmap):
        self.scene.clear()
        self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def fit_to_view(self):
        if not self.scene.items(): return
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        zoom_in_factor = 1.2
        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(1 / zoom_in_factor, 1 / zoom_in_factor)

    def trigger_flash(self):
        if not self.scene.sceneRect().isEmpty():
            flash_rect = self.scene.addRect(self.scene.sceneRect(), brush=QColor(255, 255, 255, 220))
            QTimer.singleShot(150, lambda: self.scene.removeItem(flash_rect))

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        self.models_loaded = False
        self.current_frame = None
        self.current_defects = []
        
        self.current_fabric_type = "Cotton"
        self.current_fabric_conf = 95.0

        self.best_fabric_type = "Cotton"
        self.best_fabric_conf = -1.0
        self.total_batch_defect_count = 0
        self.last_defect_time = 0  

        self.current_batch_id = f"B-{datetime.now().strftime('%Y%m%d-%H%M')}"
        self.current_roll_id = f"ROLL-{datetime.now().strftime('%Y%m%d-001')}"

        self.show_boxes = True
        self.show_labels = True
        self.is_camera_connected = False
        self.camera_cap = None
        self.last_ai_run_time = 0

        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(15, 15, 15, 15)
        main_vbox.setSpacing(12)

        self.create_top_status_bar(main_vbox)
        self.create_source_controller_bar(main_vbox)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setStyleSheet("QSplitter::handle { background-color: transparent; }")

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.canvas = MachineVisionCanvas()
        self.canvas.setMinimumSize(480, 360)
        left_layout.addWidget(self.canvas, 1)

        toolbar_layout = QHBoxLayout()
        self.btn_fit = QPushButton("🔍 Fit View")
        self.btn_zoom_in = QPushButton("➕ Zoom In")
        self.btn_zoom_out = QPushButton("➖ Zoom Out")
        self.btn_toggle_boxes = QPushButton("🟩 Bounding Boxes ON")
        self.btn_toggle_labels = QPushButton("🏷 Labels ON")

        for b in [self.btn_fit, self.btn_zoom_in, self.btn_zoom_out, self.btn_toggle_boxes, self.btn_toggle_labels]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("background-color: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 6px; padding: 6px 12px; font-weight: 600;")
            toolbar_layout.addWidget(b)

        self.btn_fit.clicked.connect(self.canvas.fit_to_view)
        self.btn_zoom_in.clicked.connect(lambda: self.canvas.scale(1.2, 1.2))
        self.btn_zoom_out.clicked.connect(lambda: self.canvas.scale(0.8, 0.8))
        self.btn_toggle_boxes.clicked.connect(self.toggle_boxes)
        self.btn_toggle_labels.clicked.connect(self.toggle_labels)

        toolbar_layout.addStretch()
        left_layout.addLayout(toolbar_layout)
        content_splitter.addWidget(left_panel)

        self.create_right_qc_sidebar(content_splitter)

        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 1)
        main_vbox.addWidget(content_splitter, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_camera_feed)
        self.apply_theme(True)

        self.lbl_fabric_type.setText("AI WAITING...")
        self.lbl_fabric_type.setStyleSheet("font-size: 16px; font-weight: 800; color: #64748b;")
        
        self.ai_engine = AIEngineThread()
        self.ai_engine.models_loaded_signal.connect(self.on_models_loaded)
        self.ai_engine.result_ready.connect(self.on_analysis_finished)
        self.show_welcome_image()

    def start_ai_models(self):
        if not self.models_loaded and not self.ai_engine.isRunning():
            self.lbl_fabric_type.setText("AI LOADING...")
            self.lbl_fabric_type.setStyleSheet("font-size: 16px; font-weight: 800; color: #f59e0b;")
            self.ai_engine.start()

    def on_models_loaded(self):
        self.models_loaded = True
        self.lbl_fabric_type.setText("SYSTEM READY")
        self.lbl_fabric_type.setStyleSheet("font-size: 16px; font-weight: 800; color: #10b981;")

    def create_top_status_bar(self, parent_layout):
        self.status_frame = QFrame()
        self.status_frame.setFixedHeight(44)
        lay = QHBoxLayout(self.status_frame)
        lay.setContentsMargins(15, 0, 15, 0)
        self.lbl_batch_tag = QLabel(f"BATCH: {self.current_batch_id}")
        self.lbl_batch_tag.setStyleSheet("font-size: 12px; font-weight: bold; color: #94a3b8; background: #1e293b; padding: 6px 12px; border-radius: 4px; border: 1px solid #334155;")
        lay.addStretch()
        lay.addWidget(self.lbl_batch_tag)
        parent_layout.addWidget(self.status_frame)

    def create_source_controller_bar(self, parent_layout):
        self.ctrl_frame = QFrame()
        self.ctrl_frame.setFixedHeight(56)
        lay = QHBoxLayout(self.ctrl_frame)
        lay.setContentsMargins(15, 0, 15, 0)
        lay.setSpacing(10)

        lbl_src = QLabel("INSPECTION SOURCE:")
        lbl_src.setStyleSheet("font-size: 11px; font-weight: bold; color: #64748b;")
        self.combo_source = QComboBox()
        self.combo_source.addItems(["Live IP Camera", "Laptop Webcam (0)", "Local Sample Image"])
        self.combo_source.setFixedWidth(170)
        self.combo_source.setMinimumHeight(34)
        self.input_url = QLineEdit(DEFAULT_CAMERA_URL)
        self.input_url.setPlaceholderText("http://10.210.10.242:8080/video")
        self.input_url.setMinimumHeight(34)

        self.btn_camera = QPushButton("▶  START CAMERA")
        self.btn_capture = QPushButton("📷  CAPTURE && INSPECT")
        self.btn_camera.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_camera.setMinimumHeight(36)
        self.btn_capture.setMinimumHeight(36)
        self.btn_camera.setMinimumWidth(150)
        self.btn_capture.setMinimumWidth(180)

        self.btn_camera.setStyleSheet("QPushButton { background-color: #334155; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px; border: none; font-size: 12px; } QPushButton:hover { background-color: #475569; }")
        self.btn_capture.setStyleSheet("QPushButton { background-color: #0284c7; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px; border: none; font-size: 12px; } QPushButton:hover { background-color: #0369a1; }")

        self.btn_camera.clicked.connect(self.toggle_camera)
        self.btn_capture.clicked.connect(self.trigger_manual_inspection)

        lay.addWidget(lbl_src)
        lay.addWidget(self.combo_source)
        lay.addWidget(self.input_url, 1)
        lay.addWidget(self.btn_camera)
        lay.addWidget(self.btn_capture)
        parent_layout.addWidget(self.ctrl_frame)

    def create_right_qc_sidebar(self, parent_splitter):
        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(330)
        self.sidebar.setMaximumWidth(410)
        side_lay = QVBoxLayout(self.sidebar)
        side_lay.setContentsMargins(16, 16, 16, 16)
        side_lay.setSpacing(14)

        box_class = QGroupBox("SECTION A — CLASSIFICATION")
        lay_class = QVBoxLayout(box_class)
        lay_class.setSpacing(8)
        self.lbl_fabric_type = QLabel("COTTON")
        self.lbl_fabric_type.setStyleSheet("font-size: 20px; font-weight: 800; color: #e2e8f0;")
        self.lbl_fabric_conf = QLabel("Confidence: 96.4%")
        self.lbl_fabric_conf.setStyleSheet("font-size: 12px; font-weight: bold; color: #94a3b8;")
        self.progress_conf = QProgressBar()
        self.progress_conf.setValue(96)
        self.progress_conf.setFixedHeight(6)
        self.progress_conf.setTextVisible(False)
        self.progress_conf.setStyleSheet("QProgressBar { background: #1e293b; border-radius: 3px; border: 1px solid #334155; } QProgressBar::chunk { background: #0369a1; border-radius: 3px; }")

        lay_class.addWidget(self.lbl_fabric_type)
        lay_class.addWidget(self.lbl_fabric_conf)
        lay_class.addWidget(self.progress_conf)
        side_lay.addWidget(box_class)

        box_defect = QGroupBox("SECTION B — INSPECTION")
        lay_defect = QVBoxLayout(box_defect)
        lay_defect.setSpacing(8)
        self.lbl_defect_badge = QLabel("✔ PASS / CLEAN")
        self.lbl_defect_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_defect_badge.setFixedHeight(36)
        self.lbl_defect_badge.setStyleSheet("font-size: 13px; font-weight: bold; background: #064e3b; color: #a7f3d0; border-radius: 4px; border: 1px solid #059669;")
        self.lbl_defect_count = QLabel("Defects Detected: 0")
        self.lbl_defect_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_defect_count.setStyleSheet("font-size: 12px; font-weight: bold; color: #94a3b8;")

        lay_defect.addWidget(self.lbl_defect_badge)
        lay_defect.addWidget(self.lbl_defect_count)
        side_lay.addWidget(box_defect)

        box_op = QGroupBox("SECTION C — CONTROL PANEL")
        lay_op = QVBoxLayout(box_op)
        lay_op.setSpacing(8)
        lay_op.setContentsMargins(12, 16, 12, 12)
        lbl_roll = QLabel("ROLL ID")
        lbl_roll.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; letter-spacing: 1px;")
        self.input_roll_id = QLineEdit(self.current_roll_id)
        self.input_roll_id.setPlaceholderText("ROLL ID")
        self.input_roll_id.setMinimumHeight(34)
        lay_op.addWidget(lbl_roll)
        lay_op.addWidget(self.input_roll_id)

        lbl_override = QLabel("MANUAL OVERRIDE")
        lbl_override.setStyleSheet("font-size: 10px; font-weight: bold; color: #64748b; letter-spacing: 1px;")
        self.override_combo = QComboBox()
        self.override_combo.addItems(["AI Quality Decision", "Force Accept", "Force Reject"])
        self.override_combo.setMinimumHeight(34)
        self.override_combo.currentTextChanged.connect(self.handle_override_change)
        lay_op.addWidget(lbl_override)
        lay_op.addWidget(self.override_combo)

        self.btn_accept = QPushButton("✔ ACCEPT ROLL")
        self.btn_reject = QPushButton("⚠ REJECT ROLL")
        for b in [self.btn_accept, self.btn_reject]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setMinimumHeight(38)

        self.btn_accept.setStyleSheet("QPushButton { background-color: #064e3b; color: #d1fae5; font-weight: bold; border: 1px solid #022c22; border-radius: 6px; font-size: 13px; } QPushButton:hover { background-color: #065f46; }")
        self.btn_reject.setStyleSheet("QPushButton { background-color: #7f1d1d; color: #fee2e2; font-weight: bold; border: 1px solid #450a0a; border-radius: 6px; font-size: 13px; } QPushButton:hover { background-color: #991b1b; }")

        self.btn_accept.clicked.connect(lambda: self.execute_quality_decision("ACCEPTED"))
        self.btn_reject.clicked.connect(lambda: self.execute_quality_decision("REJECTED"))

        lay_op.addSpacing(8)
        lay_op.addWidget(self.btn_accept)
        lay_op.addWidget(self.btn_reject)
        side_lay.addWidget(box_op)
        side_lay.addStretch()

        parent_splitter.addWidget(self.sidebar)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: #f8fafc;")
            self.status_frame.setStyleSheet("background-color: #111827; border: 1px solid #1e293b; border-radius: 6px;")
            self.ctrl_frame.setStyleSheet("background-color: #111827; border: 1px solid #1e293b; border-radius: 6px;")
            self.sidebar.setStyleSheet("QFrame { background: #111827; border-radius: 6px; border: 1px solid #1e293b; } QGroupBox { font-size: 11px; font-weight: 800; color: #94a3b8; border: 1px solid #1e293b; border-radius: 6px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
            input_style = "QLineEdit { background: #0f172a; border: 1px solid #334155; border-radius: 4px; color: #f8fafc; padding: 6px 10px; font-size: 12px; } QLineEdit:focus { border: 1px solid #0284c7; }"
            combo_style = "QComboBox { background: #0f172a; border: 1px solid #334155; border-radius: 4px; color: #f8fafc; padding: 6px 10px; font-size: 12px; } QComboBox QAbstractItemView { background: #0f172a; color: #f8fafc; selection-background-color: #1e293b; }"
            self.input_url.setStyleSheet(input_style)
            self.combo_source.setStyleSheet(combo_style)
            self.override_combo.setStyleSheet(combo_style)
            self.input_roll_id.setStyleSheet(input_style)

    def toggle_boxes(self):
        self.show_boxes = not self.show_boxes
        self.btn_toggle_boxes.setText("🟩 Bounding Boxes ON" if self.show_boxes else "⬜ Bounding Boxes OFF")
        self.refresh_canvas_display()

    def toggle_labels(self):
        self.show_labels = not self.show_labels
        self.btn_toggle_labels.setText("🏷️ Labels ON" if self.show_labels else "🏷️ Labels OFF")
        self.refresh_canvas_display()

    def toggle_camera(self):
        if not self.models_loaded:
            show_message_dialog(self, "AI Initializing", "Please wait a few seconds while AI models are loading.", "warning", "OK", True)
            return

        if self.is_camera_connected:
            self.disconnect_camera()
            return

        src_text = self.combo_source.currentText()
        if "Webcam" in src_text:
            cam_src = 0
        elif "Local Sample" in src_text:
            self.load_sample_image()
            return
        else:
            cam_src = self.input_url.text().strip()

        try:
            self.camera_cap = cv2.VideoCapture(cam_src)
            if not self.camera_cap.isOpened():
                show_message_dialog(self, "Camera Unavailable", "Check the source and try again.", "warning", "OK", True)
                return

            self.best_fabric_conf = -1.0
            self.best_fabric_type = "Cotton"
            self.total_batch_defect_count = 0

            self.is_camera_connected = True
            self.btn_camera.setText("■  STOP CAMERA")
            self.btn_camera.setStyleSheet("QPushButton { background-color: #991b1b; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px; border: none; font-size: 12px; } QPushButton:hover { background-color: #7f1d1d; }")
            self.timer.start(33) 
            show_message_dialog(self, "Camera Ready", "The camera is now streaming.", "success", "DONE", True)
        except Exception:
            show_message_dialog(self, "Camera Unavailable", "Error starting camera.", "error", "CLOSE", True)

    def disconnect_camera(self):
        self.timer.stop()
        if self.camera_cap:
            self.camera_cap.release()
            self.camera_cap = None
        self.is_camera_connected = False
        self.btn_camera.setText("▶  START CAMERA")
        self.btn_camera.setStyleSheet("QPushButton { background-color: #334155; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px; border: none; font-size: 12px; } QPushButton:hover { background-color: #475569; }")

    def update_camera_feed(self):
        if not self.camera_cap or not self.camera_cap.isOpened():
            return
            
        for _ in range(2):
            self.camera_cap.grab()
            
        ret, frame = self.camera_cap.read()
        if ret:
            self.current_frame = frame
            self.refresh_canvas_display()
            
            current_time = time.time()
            if current_time - self.last_ai_run_time >= 1.0:
                if self.models_loaded:
                    self.analyze_frame(frame)
                    self.last_ai_run_time = current_time
                    
    def load_sample_image(self, file_path=None):
        self.best_fabric_conf = -1.0
        self.best_fabric_type = "Cotton"
        self.total_batch_defect_count = 0
        
        if not file_path:
            captured_dir = "captured_batches"
            sample_candidates = []
            if os.path.exists(captured_dir):
                for root, dirs, files in os.walk(captured_dir):
                    for f in files:
                        if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                            sample_candidates.append(os.path.join(root, f))
            if sample_candidates:
                file_path = sample_candidates[0]

        if file_path and os.path.exists(file_path):
            img = cv2.imread(file_path)
            if img is not None:
                self.current_frame = img
                self.analyze_frame(img, file_path)

    def analyze_frame(self, frame, img_path=None):
        if frame is None or not self.models_loaded: return
        self.lbl_fabric_type.setText("⏳ ANALYZING...")
        self.lbl_fabric_type.setStyleSheet("font-size: 16px; font-weight: 800; color: #94a3b8;")
        self.progress_conf.setStyleSheet("QProgressBar { background: #1e293b; border-radius: 3px; border: none; } QProgressBar::chunk { background: #64748b; border-radius: 3px; }")
        self.ai_engine.analyze(frame, img_path)

    def on_analysis_finished(self, class_res, defect_res, img_path):
        raw_defects = defect_res.get("defects", [])
        
        self.current_defects = [d for d in raw_defects if d.get("confidence", 0.0) > 45.0]
        
        d_count = len(self.current_defects)
        d_status = "DEFECT DETECTED" if d_count > 0 else "PASS"

        current_time = time.time()
        if d_count > 0:
            if not hasattr(self, 'last_defect_time'): self.last_defect_time = 0
            if current_time - self.last_defect_time > 4.0: 
                self.total_batch_defect_count += d_count
                self.last_defect_time = current_time
                self.auto_save_to_results()

        if d_status == "DEFECT DETECTED":
            self.lbl_defect_badge.setText(f"⚠ {d_status}")
            self.lbl_defect_badge.setStyleSheet("font-size: 13px; font-weight: bold; background: #7f1d1d; color: #fca5a5; border-radius: 4px; border: 1px solid #991b1b;")
        else:
            self.lbl_defect_badge.setText("✔ PASS / CLEAN")
            self.lbl_defect_badge.setStyleSheet("font-size: 13px; font-weight: bold; background: #064e3b; color: #a7f3d0; border-radius: 4px; border: 1px solid #059669;")

        self.lbl_defect_count.setText(f"Defects Detected: {self.total_batch_defect_count}")
        
        self.current_fabric_type = class_res.get("fabric_type", "Cotton")
        self.current_fabric_conf = class_res.get("confidence", 0.0)

        self.lbl_fabric_type.setText(self.current_fabric_type.upper())
        self.lbl_fabric_type.setStyleSheet("font-size: 20px; font-weight: 800; color: #e2e8f0;")
        self.lbl_fabric_conf.setText(f"Confidence: {self.current_fabric_conf:.1f}%")
        self.progress_conf.setValue(int(self.current_fabric_conf))
        self.progress_conf.setStyleSheet("QProgressBar { background: #1e293b; border-radius: 3px; border: 1px solid #334155; } QProgressBar::chunk { background: #0284c7; border-radius: 3px; }")
        
        self.refresh_canvas_display()

    def refresh_canvas_display(self):
        if self.current_frame is None: return
        overlay_frame = self.current_frame.copy()
        
        if self.show_boxes or self.show_labels:
            for d in self.current_defects:
                bbox = d.get("bbox") or d.get("box")
                if bbox and len(bbox) >= 4:
                    x1, y1, x2, y2 = map(int, bbox)
                    conf = d.get("confidence", 0.0)
                    label = f"{d.get('type', 'Defect').upper()} {conf:.1f}%"
                    color = (0, 0, 239) # Red color
                    
                    if self.show_boxes:
                        cv2.rectangle(overlay_frame, (x1, y1), (x2, y2), color, 2)
                    if self.show_labels:
                        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        cv2.rectangle(overlay_frame, (x1, max(0, y1 - th - 6)), (x1 + tw + 6, max(0, y1)), color, -1)
                        cv2.putText(overlay_frame, label, (x1 + 3, max(th + 2, y1 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        h, w, ch = overlay_frame.shape
        rgb = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.canvas.set_image(QPixmap.fromImage(qimg))

    def show_welcome_image(self):
        welcome_path = "welcome_fabric.jfif"
        
        if os.path.exists(welcome_path):
            self.canvas.set_image(QPixmap(welcome_path))
        else:
            self.canvas.scene.clear()
            self.canvas.scene.addItem(self.canvas.placeholder_text)
            
        self.current_frame = None
        self.current_defects = []
        self.total_batch_defect_count = 0
        
        self.lbl_fabric_type.setText("SYSTEM READY")
        self.lbl_fabric_type.setStyleSheet("font-size: 16px; font-weight: 800; color: #10b981;")
        self.lbl_fabric_conf.setText("Confidence: 0.0%")
        self.progress_conf.setValue(0)
        self.progress_conf.setStyleSheet("QProgressBar { background: #1e293b; border-radius: 3px; border: 1px solid #334155; } QProgressBar::chunk { background: #0369a1; border-radius: 3px; }")
        
        self.lbl_defect_badge.setText("WAITING FOR ROLL")
        self.lbl_defect_badge.setStyleSheet("font-size: 13px; font-weight: bold; background: #1e293b; color: #94a3b8; border-radius: 4px; border: 1px solid #334155;")
        self.lbl_defect_count.setText("Defects Detected: 0")

    def auto_save_to_results(self):
        if self.current_frame is None or len(self.current_defects) == 0:
            return 
            
        batch_id = self.current_batch_id
        base_dir = os.path.abspath(os.path.join(os.getcwd(), "captured_batches"))
        batch_dir = os.path.join(base_dir, batch_id)
        os.makedirs(batch_dir, exist_ok=True)
        img_filename = f"auto_defect_{datetime.now().strftime('%H%M%S')}.jpg"
        filepath = os.path.join(batch_dir, img_filename)
        
        save_frame = self.current_frame.copy()
        if self.show_boxes or self.show_labels:
            for d in self.current_defects:
                bbox = d.get("bbox") or d.get("box")
                if bbox and len(bbox) >= 4:
                    x1, y1, x2, y2 = map(int, bbox)
                    conf = d.get("confidence", 0.0)
                    label = f"{d.get('type', 'Defect').upper()} {conf:.1f}%"
                    color = (0, 0, 239)
                    
                    if self.show_boxes:
                        cv2.rectangle(save_frame, (x1, y1), (x2, y2), color, 2)
                    if self.show_labels:
                        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                        cv2.rectangle(save_frame, (x1, max(0, y1 - th - 6)), (x1 + tw + 6, max(0, y1)), color, -1)
                        cv2.putText(save_frame, label, (x1 + 3, max(th + 2, y1 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imwrite(filepath, save_frame)
        
        d_status = "DEFECT DETECTED"
        new_record = {
            "batch_id": batch_id, "filename": img_filename, "filepath": filepath, "file_path": filepath,
            "type": self.current_fabric_type, "conf": self.current_fabric_conf,
            "defect_status": d_status, "defects": self.current_defects
        }
        
        if not hasattr(self, 'manual_captured_results'): self.manual_captured_results = []
        self.manual_captured_results.append(new_record)
        results_page = self.parent.pages.widget(4)
        if hasattr(results_page, 'load_new_batch'): results_page.load_new_batch(self.manual_captured_results)

    def trigger_manual_inspection(self):
        if not self.models_loaded:
            show_message_dialog(self, "AI Initializing", "Please wait a few seconds while AI models are loading.", "warning", "OK", True)
            return
            
        if self.current_frame is not None:
            self.canvas.trigger_flash()
            
            real_defects = [d for d in self.current_defects if d.get("confidence", 0) > 45.0]
            
            batch_id = self.current_batch_id
            base_dir = os.path.abspath(os.path.join(os.getcwd(), "captured_batches"))
            batch_dir = os.path.join(base_dir, batch_id)
            os.makedirs(batch_dir, exist_ok=True)
            img_filename = f"manual_defect_{datetime.now().strftime('%H%M%S')}.jpg"
            filepath = os.path.join(batch_dir, img_filename)
            
            save_frame = self.current_frame.copy()
            if self.show_boxes or self.show_labels:
                for d in real_defects:
                    bbox = d.get("bbox") or d.get("box")
                    if bbox and len(bbox) >= 4:
                        x1, y1, x2, y2 = map(int, bbox)
                        conf = d.get("confidence", 0.0)
                        label = f"{d.get('type', 'Defect').upper()} {conf:.1f}%"
                        color = (0, 0, 239)
                        
                        if self.show_boxes:
                            cv2.rectangle(save_frame, (x1, y1), (x2, y2), color, 2)
                        if self.show_labels:
                            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                            cv2.rectangle(save_frame, (x1, max(0, y1 - th - 6)), (x1 + tw + 6, max(0, y1)), color, -1)
                            cv2.putText(save_frame, label, (x1 + 3, max(th + 2, y1 - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            cv2.imwrite(filepath, save_frame)
            
            d_status = "DEFECT DETECTED" if len(real_defects) > 0 else "PASS"
            new_record = {
                "batch_id": batch_id, "filename": img_filename, "filepath": filepath, "file_path": filepath,
                "type": self.current_fabric_type, "conf": self.current_fabric_conf,
                "defect_status": d_status, "defects": real_defects
            }
            if not hasattr(self, 'manual_captured_results'): self.manual_captured_results = []
            self.manual_captured_results.append(new_record)
            
            results_page = self.parent.pages.widget(4)
            if hasattr(results_page, 'load_new_batch'): results_page.load_new_batch(self.manual_captured_results)
            
            self.lbl_batch_tag.setText(f"BATCH: {batch_id}")
        else:
            self.load_sample_image()

    def handle_override_change(self, text):
        if text != "AI Quality Decision":
            self.lbl_defect_badge.setText(f"MANUAL: {text.upper()}")
            self.lbl_defect_badge.setStyleSheet("font-size: 13px; font-weight: bold; background: #1e293b; color: #38bdf8; border-radius: 4px; border: 1px solid #334155;")

    def process_image_batch(self, batch_id, valid_files):
        if not valid_files or not self.models_loaded: return
        self.current_batch_id = batch_id
        self.lbl_batch_tag.setText(f"BATCH: {batch_id}")
        
        try:
            from model_inference import FabricClassifier
            from defect_detector import FabricDefectDetector
            batch_classifier = FabricClassifier()
            batch_detector = FabricDefectDetector()
            
            batch_results = []
            best_file = valid_files[0]
            highest_conf = -1.0
            
            for fp in valid_files:
                img = cv2.imread(fp)
                if img is None: continue
                c_res = batch_classifier.predict_detailed(fp)
                d_res = batch_detector.detect(img)
                if c_res["confidence"] > highest_conf:
                    highest_conf = c_res["confidence"]
                    best_file = fp
                abs_fp = os.path.abspath(fp)
                batch_results.append({
                    "batch_id": batch_id, "filename": os.path.basename(abs_fp), "filepath": abs_fp, 
                    "file_path": abs_fp, "type": c_res["fabric_type"], "conf": c_res["confidence"],
                    "defect_status": d_res["status"], "defects": d_res["defects"]
                })
            
            if best_file: self.load_sample_image(best_file)
            results_page = self.parent.pages.widget(4)
            if hasattr(results_page, 'load_new_batch'): results_page.load_new_batch(batch_results)
        except Exception as e:
            print(f"Batch Processing Error: {e}")

    def execute_quality_decision(self, decision):
        roll_id = self.input_roll_id.text().strip() or self.current_roll_id
        override_text = self.override_combo.currentText()
        is_overridden = (override_text != "AI Quality Decision")
        d_count = len(self.current_defects)
        primary_d = self.current_defects[0]["type"] if self.current_defects else "None"
        primary_d_conf = self.current_defects[0]["confidence"] if self.current_defects else 0.0
        
        operator_name = "QC_INSPECTOR_01"
        if self.parent and hasattr(self.parent, 'current_user') and self.parent.current_user:
            u = self.parent.current_user
            operator_name = " ".join(filter(None, [u.get("fname"), u.get("lname")])).strip() or u.get("email", "QC_INSPECTOR_01")

        success, msg = save_inspection_record(
            batch_id=self.current_batch_id, session_id=f"{roll_id}_img_01.jpg", user_id=1,
            final_fabric_type=self.current_fabric_type, confidence_score=self.current_fabric_conf,
            is_overridden=is_overridden, action_status=decision, roll_id=roll_id,
            defect_status="DEFECT DETECTED" if d_count > 0 else "PASS", defect_type=primary_d,
            defect_count=d_count, defect_confidence=primary_d_conf, ai_decision="REJECT" if d_count > 0 else "PASS",
            operator_decision=decision, override_reason=override_text if is_overridden else "",
            operator_name=operator_name
        )
        if success:
            show_message_dialog(self, "Decision Saved", f"Roll {roll_id} marked as {decision}.", "success", "DONE", getattr(self.parent, 'is_dark_mode', True))
                        
            self.show_welcome_image() 
        else:
            show_message_dialog(self, "Could Not Save", "The decision could not be saved. Please try again.", "error", "CLOSE", getattr(self.parent, 'is_dark_mode', True))