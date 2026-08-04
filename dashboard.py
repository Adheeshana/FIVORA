
import cv2
import numpy as np
import tensorflow as tf
import json
import os
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # AI Settings & Session variables
        self.IMG_SIZE = (224, 224)
        self.model = None
        self.classes = []
        self.current_raw_image = None
        self.current_session_data = {} # FR 26 - Store results in session

        # Load Class Labels from JSON
        json_path = os.path.join("fabric_classifier_model", "class_info.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                self.classes = json.load(f).get("classes", [])

        # Load Keras AI Model
        model_path = os.path.join("fabric_classifier_model", "fabric_classifier.keras")
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)

        # --- Left Panel: Camera/Image Feed (FR 16) ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        self.cam_title = QLabel("📷 Real-Time Fabric Scan")
        self.cam_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.roll_id = QLabel("ROLL_ID: 24M20M_00234")
        self.roll_id.setStyleSheet("font-size: 12px; font-weight: bold;")

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.cam_title)
        header_layout.addStretch()
        header_layout.addWidget(self.roll_id)
        left_panel.addLayout(header_layout)

        self.cam_label = QLabel("📷 NO FABRIC FEED AVAILABLE\n\nGo to 'Upload Image' tab to upload a sample.")
        self.cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.cam_label, 1)
        self.main_layout.addLayout(left_panel, 3)

        # --- Right Sidebar: Results & Classification (FR 27, 37) ---
        self.sidebar = QFrame()
        side_lay = QVBoxLayout(self.sidebar)
        side_lay.setContentsMargins(15, 15, 15, 15)
        side_lay.setSpacing(15)

        self.type_header = QLabel("FABRIC CLASSIFICATION")
        self.type_header.setStyleSheet("font-size: 11px; font-weight: bold;")
        side_lay.addWidget(self.type_header)

        # FR 37 - Display Fabric Type to User
        self.type_label = QLabel("TYPE: PENDING")
        self.type_label.setStyleSheet("color: #00A3FF; font-size: 16px; font-weight: bold;")
        side_lay.addWidget(self.type_label)

        # FR 27 - Allow Manual Fabric-Type Override Dropdown
        self.override_combo = QComboBox()
        self.override_combo.addItems(["Auto Detect"] + self.classes)
        self.override_combo.currentTextChanged.connect(self.handle_manual_override)
        side_lay.addWidget(self.override_combo)

        # Metrics Panels (Pending placeholders for defect model)
        metrics_row = QHBoxLayout()
        self.defect_card = QFrame()
        d_lay = QVBoxLayout(self.defect_card)
        self.d_title = QLabel("DEFECTS", styleSheet="font-size: 11px; font-weight: bold;")
        self.defect_val = QLabel("--", styleSheet="color: #ef4444; font-size: 22px; font-weight: bold;")
        d_lay.addWidget(self.d_title)
        d_lay.addWidget(self.defect_val)

        self.conf_card = QFrame()
        c_lay = QVBoxLayout(self.conf_card)
        self.c_title = QLabel("CONFIDENCE", styleSheet="font-size: 11px; font-weight: bold;")
        self.conf_val = QLabel("--%", styleSheet="color: #00A3FF; font-size: 22px; font-weight: bold;")
        c_lay.addWidget(self.c_title)
        c_lay.addWidget(self.conf_val)

        metrics_row.addWidget(self.defect_card)
        metrics_row.addWidget(self.conf_card)
        side_lay.addLayout(metrics_row)

        self.q_title = QLabel("QUALITY SCORE", styleSheet="font-size: 11px; font-weight: bold;", alignment=Qt.AlignmentFlag.AlignCenter)
        side_lay.addWidget(self.q_title)

        self.quality_score = QLabel("--\nWAITING")
        self.quality_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        badge_container = QHBoxLayout()
        badge_container.addStretch()
        badge_container.addWidget(self.quality_score)
        badge_container.addStretch()
        side_lay.addLayout(badge_container)

        side_lay.addStretch()

        accept_btn = QPushButton("ACCEPT ROLL")
        accept_btn.setStyleSheet("background-color: #10b981; color: white; padding: 12px; font-weight: bold; border-radius: 8px;")
        reject_btn = QPushButton("REJECT ROLL")
        reject_btn.setStyleSheet("background-color: #ef4444; color: white; padding: 12px; font-weight: bold; border-radius: 8px;")
        
        side_lay.addWidget(accept_btn)
        side_lay.addWidget(reject_btn)
        self.main_layout.addWidget(self.sidebar, 1)

        self.apply_theme(True)

    def apply_theme(self, is_dark):
        """Applies adaptive theme styles (Light/Dark mode toggle)."""
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.cam_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
            self.roll_id.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
            self.cam_label.setStyleSheet("background: #0f172a; border: 2px dashed #334155; border-radius: 12px; color: #94a3b8; font-weight: bold;")
            self.sidebar.setStyleSheet("background: #111827; border-radius: 12px; border: 1px solid #1e293b;")
            self.type_header.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; border: none;")
            self.override_combo.setStyleSheet("QComboBox { background: #1e293b; color: white; padding: 8px; border-radius: 6px; border: 1px solid #334155; } QComboBox::drop-down { border: none; }")
            self.defect_card.setStyleSheet("background: #1e293b; border-radius: 8px; border: none;")
            self.conf_card.setStyleSheet("background: #1e293b; border-radius: 8px; border: none;")
            self.d_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
            self.c_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold;")
            self.q_title.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; border: none;")
            self.quality_score.setStyleSheet("QLabel { border: 6px solid #334155; border-radius: 65px; min-height: 130px; max-height: 130px; min-width: 130px; max-width: 130px; color: white; font-size: 18px; font-weight: bold; background-color: #0f172a; }")
        else:
            self.setStyleSheet("background-color: #f4f6f9; color: #0f172a;")
            self.cam_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
            self.roll_id.setStyleSheet("color: #64748b; font-size: 12px; font-weight: bold;")
            self.cam_label.setStyleSheet("background: #e2e8f0; border: 2px dashed #cbd5e1; border-radius: 12px; color: #64748b; font-weight: bold;")
            self.sidebar.setStyleSheet("background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0;")
            self.type_header.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; border: none;")
            self.override_combo.setStyleSheet("QComboBox { background: #f1f5f9; color: #0f172a; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; } QComboBox::drop-down { border: none; }")
            self.defect_card.setStyleSheet("background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;")
            self.conf_card.setStyleSheet("background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;")
            self.d_title.setStyleSheet("color: #475569; font-size: 11px; font-weight: bold;")
            self.c_title.setStyleSheet("color: #475569; font-size: 11px; font-weight: bold;")
            self.q_title.setStyleSheet("color: #475569; font-size: 11px; font-weight: bold; border: none;")
            self.quality_score.setStyleSheet("QLabel { border: 6px solid #cbd5e1; border-radius: 65px; min-height: 130px; max-height: 130px; min-width: 130px; max-width: 130px; color: #0f172a; font-size: 18px; font-weight: bold; background-color: #ffffff; }")

    def load_custom_image(self, file_path):
        """FR 15: Store Raw Image Temporarily & FR 16: Display Image Preview to User."""
        image = cv2.imread(file_path)
        if image is not None:
            self.current_raw_image = image.copy() # Store raw image in memory temporarily
            
            # Display image preview
            h, w, ch = image.shape
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
            self.cam_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                self.cam_label.width(), self.cam_label.height(), Qt.AspectRatioMode.KeepAspectRatio
            ))
            
            # Run AI Pipeline (Aberathna's part)
            self.run_fabric_classification(image)

    def run_fabric_classification(self, image):
        """
        FR 23: Preprocess Image for AI Input
        FR 24: Send Image to Fabric-Type Model
        FR 25: Receive Fabric-Type Prediction
        FR 37: Display Fabric Type to User
        """
        if self.model is None: 
            return
        
        # FR 23 - Preprocess image
        resized = cv2.resize(image, self.IMG_SIZE)
        rgb_resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        preprocessed = tf.keras.applications.densenet.preprocess_input(rgb_resized)
        input_data = np.expand_dims(preprocessed, axis=0)
        
        # FR 24 & 25 - Send to model and receive prediction
        predictions = self.model.predict(input_data, verbose=0)
        predicted_index = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0])) * 100
        
        if self.classes:
            fabric_type = self.classes[predicted_index]
            
            # FR 37 - Display Fabric Type to User
            self.type_label.setText(f"TYPE: {fabric_type.upper()}")
            
            # Sync dropdown without triggering manual override signal
            self.override_combo.blockSignals(True)
            self.override_combo.setCurrentText(fabric_type)
            self.override_combo.blockSignals(False)
            
            # FR 26 - Store Result in Session dictionary
            self.current_session_data = {
                "predicted_type": fabric_type,
                "confidence": confidence
            }
            self.conf_val.setText(f"{confidence:.1f}%")

    def handle_manual_override(self, selected_text):
        """FR 27: Allow Manual Fabric-Type Override."""
        if selected_text != "Auto Detect":
            self.type_label.setText(f"TYPE: {selected_text.upper()} (MANUAL)")
            self.current_session_data["predicted_type"] = selected_text