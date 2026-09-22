import os
import cv2
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QGridLayout, QComboBox, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from database import save_inspection_record
from custom_dialog import show_message_dialog
from report_generator import ReportGenerator


class ResultDetailDialog(QDialog):
    """
    Detailed Inspection Record View for a single fabric sample.
    """
    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Inspection Record — {record.get('filename', 'Sample')}")
        self.resize(720, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        lbl_title = QLabel(f"DETAILED INSPECTION RECORD: {record.get('filename', 'Sample')}")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0ea5e9;")
        layout.addWidget(lbl_title)

        # Content Splitter (Image + Data)
        content_lay = QHBoxLayout()

        # Thumbnail Image
        lbl_img = QLabel()
        lbl_img.setFixedSize(320, 320)
        lbl_img.setStyleSheet("background: #0f172a; border: 1px solid #334155; border-radius: 8px;")
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Render preview image
        batch_id = record.get("batch_id", "")
        fn = record.get("filename", "")
        imgPath = os.path.join("captured_batches", batch_id, fn)
        if os.path.exists(imgPath):
            pix = QPixmap(imgPath).scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
            lbl_img.setPixmap(pix)
        else:
            lbl_img.setText("📷 Preview Image")

        content_lay.addWidget(lbl_img)

        # Data Column
        data_frame = QFrame()
        data_frame.setStyleSheet("background: #1e293b; border-radius: 8px; padding: 12px;")
        data_lay = QVBoxLayout(data_frame)

        fields = [
            ("Batch ID:", record.get("batch_id", "N/A")),
            ("Roll ID:", record.get("roll_id", "ROLL-2026-001")),
            ("Fabric Type:", f"{record.get('type', 'Cotton')} ({record.get('conf', 95.0):.1f}%)"),
            ("Defect Status:", record.get("defect_status", "PASS")),
            ("Defects Count:", str(len(record.get("defects", [])))),
            ("AI Decision:", "REJECT" if record.get("defects") else "PASS"),
            ("Operator Action:", record.get("action_status", "ACCEPTED")),
            ("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        ]

        for k, v in fields:
            f_lay = QHBoxLayout()
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-weight: bold; color: #94a3b8;")
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-weight: bold; color: white;")
            f_lay.addWidget(lbl_k)
            f_lay.addStretch()
            f_lay.addWidget(lbl_v)
            data_lay.addLayout(f_lay)

        data_lay.addStretch()
        content_lay.addWidget(data_frame, 1)

        layout.addLayout(content_lay)

        btn_close = QPushButton("Close Record")
        btn_close.setStyleSheet("background: #0ea5e9; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


class ResultsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_batch = []
        self.filtered_batch = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        # Header Title
        title_lay = QHBoxLayout()
        title = QLabel("INSPECTION RESULTS GALLERY")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")
        title_lay.addWidget(title)
        title_lay.addStretch()

        self.btn_save_all = QPushButton("💾 SAVE ALL RESULTS TO DATABASE")
        self.btn_save_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_all.setStyleSheet("background-color: #10b981; color: white; padding: 10px 18px; font-weight: bold; border-radius: 6px;")
        self.btn_save_all.clicked.connect(self.save_all_to_database)
        title_lay.addWidget(self.btn_save_all)

        main_layout.addLayout(title_lay)

        # QC Filter Toolbar
        filter_frame = QFrame()
        filter_frame.setStyleSheet("background: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 8px;")
        filter_lay = QHBoxLayout(filter_frame)

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("🔍 Search Filename / Roll ID / Batch...")
        self.input_search.textChanged.connect(self.apply_filters)

        self.combo_type_filter = QComboBox()
        self.combo_type_filter.addItems(["All Fabric Types", "Cotton", "Denim", "Silk", "Linen", "Polyester", "Wool"])
        self.combo_type_filter.currentTextChanged.connect(self.apply_filters)

        self.combo_status_filter = QComboBox()
        self.combo_status_filter.addItems(["All Defect Statuses", "PASS / CLEAN", "DEFECT DETECTED"])
        self.combo_status_filter.currentTextChanged.connect(self.apply_filters)

        filter_lay.addWidget(self.input_search, 1)
        filter_lay.addWidget(self.combo_type_filter)
        filter_lay.addWidget(self.combo_status_filter)

        main_layout.addWidget(filter_frame)

        # Grid Scroll Area for Result Cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(15)
        self.scroll.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll, 1)

        self.apply_theme(True)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.scroll.setStyleSheet("QScrollArea { background: #0b0f19; border: none; }")
            self.scroll_content.setStyleSheet("background: #0b0f19;")
            style_input = "QLineEdit, QComboBox { background: #1e293b; border: 1px solid #334155; border-radius: 6px; color: white; padding: 6px; }"
            self.input_search.setStyleSheet(style_input)
            self.combo_type_filter.setStyleSheet(style_input)
            self.combo_status_filter.setStyleSheet(style_input)

    def load_new_batch(self, batch_results):
        self.current_batch = batch_results
        self.apply_filters()

    def apply_filters(self):
        search_txt = self.input_search.text().strip().lower()
        type_txt = self.combo_type_filter.currentText()
        status_txt = self.combo_status_filter.currentText()

        self.filtered_batch = []
        for item in self.current_batch:
            fn = item.get("filename", "").lower()
            ftype = item.get("type", "")
            dstatus = item.get("defect_status", "PASS")

            match_search = not search_txt or search_txt in fn or search_txt in item.get("batch_id", "").lower()
            match_type = (type_txt == "All Fabric Types") or (ftype.lower() == type_txt.lower())
            match_status = (status_txt == "All Defect Statuses") or (dstatus.upper() in status_txt.upper())

            if match_search and match_type and match_status:
                self.filtered_batch.append(item)

        self.render_cards()

    def render_cards(self):
        # Clear existing cards
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not self.filtered_batch:
            empty_lbl = QLabel("NO MATCHING INSPECTION RESULTS FOUND")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #64748b; padding: 40px;")
            self.grid_layout.addWidget(empty_lbl, 0, 0)
            return

        cols = 3
        for idx, item in enumerate(self.filtered_batch):
            card = self.create_result_card(item)
            r = idx // cols
            c = idx % cols
            self.grid_layout.addWidget(card, r, c)

    def create_result_card(self, item):
        card = QFrame()
        card.setFixedSize(260, 240)
        card.setStyleSheet("QFrame { background: #111827; border: 1px solid #1e293b; border-radius: 10px; } QFrame:hover { border: 1px solid #00A3FF; }")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(6)

        # Image thumbnail
        lbl_thumb = QLabel()
        lbl_thumb.setFixedHeight(110)
        lbl_thumb.setStyleSheet("background: #0f172a; border-radius: 6px;")
        lbl_thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)

        batch_id = item.get("batch_id", "")
        fn = item.get("filename", "")
        imgPath = os.path.join("captured_batches", batch_id, fn)
        if os.path.exists(imgPath):
            pix = QPixmap(imgPath).scaled(230, 100, Qt.AspectRatioMode.KeepAspectRatio)
            lbl_thumb.setPixmap(pix)
        else:
            lbl_thumb.setText("📷 FABRIC THUMBNAIL")

        lay.addWidget(lbl_thumb)

        # Info Labels
        lbl_name = QLabel(fn)
        lbl_name.setStyleSheet("font-size: 11px; font-weight: bold; color: white;")
        
        d_status = item.get("defect_status", "PASS")
        status_color = "#34d399" if d_status == "PASS" else "#fca5a5"
        lbl_type = QLabel(f"FABRIC: {item.get('type', 'Cotton').upper()} ({item.get('conf', 95.0):.1f}%)")
        lbl_type.setStyleSheet("font-size: 10px; font-weight: bold; color: #0ea5e9;")

        lbl_defect = QLabel(f"STATUS: {d_status}")
        lbl_defect.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {status_color};")

        lay.addWidget(lbl_name)
        lay.addWidget(lbl_type)
        lay.addWidget(lbl_defect)

        # Detail Button
        btn_details = QPushButton("🔍 View Record Details")
        btn_details.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_details.setStyleSheet("background: #1e293b; color: #cbd5e1; border: 1px solid #334155; border-radius: 4px; padding: 4px; font-size: 10px; font-weight: bold;")
        btn_details.clicked.connect(lambda _, rec=item: self.open_detail_dialog(rec))
        lay.addWidget(btn_details)

        return card

    def open_detail_dialog(self, record):
        dlg = ResultDetailDialog(record, self)
        dlg.exec()

    def save_all_to_database(self):
        if not self.current_batch:
            show_message_dialog(self, "Nothing to Save", "There are no inspection results in this batch.", "warning", "OK", getattr(self.parent, 'is_dark_mode', True))
            return

        success_count = 0
        for item in self.current_batch:
            defects = item.get("defects", [])
            d_count = len(defects)
            primary_d = defects[0]["type"] if defects else "None"
            primary_d_conf = defects[0]["confidence"] if defects else 0.0

            success, _ = save_inspection_record(
                batch_id=item.get("batch_id", "BATCH_01"),
                session_id=item.get("filename", "sample.jpg"),
                user_id=1,
                final_fabric_type=item.get("type", "Cotton"),
                confidence_score=item.get("conf", 95.0),
                is_overridden=False,
                action_status="Batch Processed",
                roll_id=f"ROLL-{item.get('batch_id', '01')}",
                defect_status=item.get("defect_status", "PASS"),
                defect_type=primary_d,
                defect_count=d_count,
                defect_confidence=primary_d_conf,
                ai_decision="REJECT" if d_count > 0 else "PASS",
                operator_decision="ACCEPTED",
                operator_name="QC_INSPECTOR_01"
            )
            if success:
                success_count += 1

        if success_count > 0:
            show_message_dialog(self, "Results Saved", f"{success_count} inspection results were saved.", "success", "DONE", getattr(self.parent, 'is_dark_mode', True))
            self.current_batch = []
            self.render_cards()
            self.parent.switch_page(5)
        else:
            # Local CSV Backup fallback if DB offline
            records = [
                [
                    item.get('batch_id'), item.get('filename'), item.get('type'), 
                    item.get('conf'), "False", "Local Backup", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                for item in self.current_batch
            ]
            fb_fn = f"Offline_Backup_{self.current_batch[0]['batch_id']}.csv"
            ok, msg = ReportGenerator.export_to_csv(records, filename=fb_fn)
            if ok:
                show_message_dialog(self, "Backup Saved", "The results were saved to a local backup file.", "success", "DONE", getattr(self.parent, 'is_dark_mode', True))
                self.current_batch = []
                self.render_cards()