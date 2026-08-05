import cv2
import numpy as np
import tensorflow as tf
import json
import os
import uuid
import random
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from database import save_inspection_record

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self.IMG_SIZE = (224, 224)
        self.model = None
        self.classes = []
        self.preview_data_cache = None
        self.current_batch_id = None
        
        json_path = os.path.join("fabric_classifier_model", "class_info.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                self.classes = json.load(f).get("classes", [])

        model_path = os.path.join("fabric_classifier_model", "fabric_classifier.keras")
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)

        # --- Center Panel ---
        center_panel = QVBoxLayout()
        center_panel.setSpacing(10)
        
        header_layout = QHBoxLayout()
        self.btn_cam_icon = QPushButton("📷")
        self.btn_cam_icon.setStyleSheet("background: transparent; font-size: 20px; border: none; color: #0ea5e9;")
        self.btn_cam_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cam_icon.setToolTip("Go to Capture / Upload")
        self.btn_cam_icon.clicked.connect(lambda: self.parent.switch_page(3)) 
        
        self.cam_title = QLabel("Real-Time Fabric Scan Preview")
        self.cam_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        header_layout.addWidget(self.btn_cam_icon)
        header_layout.addWidget(self.cam_title)
        header_layout.addStretch()
        center_panel.addLayout(header_layout)
        
        self.cam_label = QLabel("📷 NO FABRIC FEED AVAILABLE\n\nClick the camera icon to capture.")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_label.setMinimumSize(320, 240) # Allow shrinking
        center_panel.addWidget(self.cam_label, 1) # Expand ratio
        
        self.batch_info_label = QLabel("")
        self.batch_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_panel.addWidget(self.batch_info_label)
        
        self.main_layout.addLayout(center_panel, 3) # Left takes 3/4 width

        # --- Right Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setMinimumWidth(280)
        self.sidebar.setMaximumWidth(350)
        side_lay = QVBoxLayout(self.sidebar)
        side_lay.setContentsMargins(15, 15, 15, 15)
        side_lay.setSpacing(15)

        self.type_header = QLabel("AI CLASSIFICATION RESULT")
        self.type_label = QLabel("TYPE: PENDING")
        self.override_combo = QComboBox()
        self.override_combo.addItems(["Auto Detect"] + self.classes)
        self.override_combo.currentTextChanged.connect(self.handle_manual_override)
        
        self.conf_val = QLabel("Confidence: --%")
        
        side_lay.addWidget(self.type_header)
        side_lay.addWidget(self.type_label)
        side_lay.addWidget(self.override_combo)
        side_lay.addWidget(self.conf_val)
        side_lay.addStretch() # Pushes buttons to the absolute bottom of sidebar
        
        self.btn_accept = QPushButton("✔ ACCEPT PREVIEW ROLL")
        self.btn_accept.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_accept.setStyleSheet("background-color: #10b981; color: white; padding: 14px; font-weight: bold; border-radius: 8px; font-size: 14px;")
        self.btn_accept.clicked.connect(lambda: self.save_preview_action("Accepted"))
        
        self.btn_reject = QPushButton("⚠ REJECT PREVIEW ROLL")
        self.btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reject.setStyleSheet("background-color: #ef4444; color: white; padding: 14px; font-weight: bold; border-radius: 8px; font-size: 14px;")
        self.btn_reject.clicked.connect(lambda: self.save_preview_action("Rejected"))
        
        side_lay.addWidget(self.btn_accept)
        side_lay.addWidget(self.btn_reject)
        
        self.main_layout.addWidget(self.sidebar, 1) # Sidebar takes 1/4 width
        self.apply_theme(False)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.cam_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
            self.cam_label.setStyleSheet("background: #0f172a; border: 2px dashed #334155; border-radius: 12px; color: #94a3b8; font-weight: bold;")
            self.batch_info_label.setStyleSheet("color: #0ea5e9; font-weight: bold; font-size: 14px;")
            self.sidebar.setStyleSheet("background: #111827; border-radius: 12px; border: 1px solid #1e293b;")
            self.type_header.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; border: none;")
            self.type_label.setStyleSheet("color: #00A3FF; font-size: 16px; font-weight: bold; border: none;")
            self.override_combo.setStyleSheet("QComboBox { background: #1e293b; color: white; padding: 8px; border-radius: 6px; border: 1px solid #334155; }")
            self.conf_val.setStyleSheet("color: #10b981; font-size: 14px; font-weight: bold; border: none;")
        else:
            self.setStyleSheet("background-color: #f4f6f9; color: #0f172a;")
            self.cam_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
            self.cam_label.setStyleSheet("background: #e2e8f0; border: 2px dashed #cbd5e1; border-radius: 12px; color: #64748b; font-weight: bold;")
            self.batch_info_label.setStyleSheet("color: #0284c7; font-weight: bold; font-size: 14px;")
            self.sidebar.setStyleSheet("background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;")
            self.type_header.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; border: none;")
            self.type_label.setStyleSheet("color: #00A3FF; font-size: 16px; font-weight: bold; border: none;")
            self.override_combo.setStyleSheet("QComboBox { background: #f1f5f9; color: #0f172a; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; }")
            self.conf_val.setStyleSheet("color: #059669; font-size: 14px; font-weight: bold; border: none;")

    def handle_manual_override(self, selected_text):
        if selected_text != "Auto Detect":
            self.type_label.setText(f"TYPE: {selected_text.upper()} (MANUAL)")
            if self.preview_data_cache:
                self.preview_data_cache["overridden_type"] = selected_text
        else:
            if self.preview_data_cache:
                self.type_label.setText(f"TYPE: {self.preview_data_cache['type'].upper()}")
                self.preview_data_cache["overridden_type"] = None

    def process_image_batch(self, batch_id, valid_files):
        if not valid_files: return
        self.current_batch_id = batch_id
        random_preview_file = random.choice(valid_files)
        
        batch_results = []
        
        for fp in valid_files:
            image = cv2.imread(fp)
            if image is not None and self.model is not None:
                resized = cv2.resize(image, self.IMG_SIZE)
                preprocessed = tf.keras.applications.densenet.preprocess_input(cv2.cvtColor(resized, cv2.COLOR_BGR2RGB))
                preds = self.model.predict(np.expand_dims(preprocessed, axis=0), verbose=0)
                
                idx = np.argmax(preds[0])
                conf = float(np.max(preds[0])) * 100
                ftype = self.classes[idx] if self.classes else "Unknown"
                img_name = os.path.basename(fp) 
                
                batch_results.append({
                    "batch_id": batch_id,
                    "filename": img_name,
                    "type": ftype,
                    "conf": conf
                })
                
                if fp == random_preview_file:
                    self.preview_data_cache = {"filename": img_name, "type": ftype, "conf": conf, "overridden_type": None}
                    h, w, ch = image.shape
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
                    self.cam_label.setPixmap(QPixmap.fromImage(qimg).scaled(self.cam_label.width(), self.cam_label.height(), Qt.AspectRatioMode.KeepAspectRatio))
                    self.type_label.setText(f"TYPE: {ftype.upper()}")
                    self.conf_val.setText(f"Confidence: {conf:.1f}%")
                    self.override_combo.blockSignals(True)
                    self.override_combo.setCurrentIndex(0)
                    self.override_combo.blockSignals(False)

        results_page = self.parent.pages.widget(4)
        if hasattr(results_page, 'load_new_batch'):
            results_page.load_new_batch(batch_results)

        self.batch_info_label.setText(f"Batch {batch_id} Analyzed. Please check 'Results' tab to save.")

    

    def save_preview_action(self, status):
        if not self.preview_data_cache or not self.current_batch_id:
            QMessageBox.warning(self, "Warning", "No preview available to save!")
            return
            
        final_type = self.preview_data_cache.get("overridden_type") or self.preview_data_cache["type"]
        is_overridden = bool(self.preview_data_cache.get("overridden_type"))
            
        success, msg = save_inspection_record(
            batch_id=self.current_batch_id,
            session_id=self.preview_data_cache["filename"],
            user_id=1,
            final_fabric_type=final_type,
            confidence_score=self.preview_data_cache["conf"],
            is_overridden=is_overridden,
            action_status=f"{status} (Preview Override)"
        )
        if success:
            QMessageBox.information(self, "Success", f"Preview Action marked as {status} and saved!")
            self.parent.switch_page(5) 
        else:
            QMessageBox.critical(self, "Error", msg)