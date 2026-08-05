from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QMessageBox
from PyQt6.QtCore import Qt
from database import save_inspection_record
from datetime import datetime

class ResultsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.current_batch = [] 
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        
        header_layout = QHBoxLayout()
        title = QLabel("Conveyor Stream Analysis Results (Pending Save)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        self.btn_save_all = QPushButton("SAVE ENTIRE BATCH")
        self.btn_save_all.setStyleSheet("background-color: #10b981; color: white; padding: 12px 20px; font-weight: bold; border-radius: 8px;")
        self.btn_save_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_all.clicked.connect(self.save_entire_batch)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_save_all)
        main_layout.addLayout(header_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        
        main_layout.addWidget(self.scroll)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.container.setStyleSheet("background-color: #0b0f19;")
        else:
            self.setStyleSheet("background-color: #f8fafc; color: #0f172a;")
            self.container.setStyleSheet("background-color: #f8fafc;")

    def load_new_batch(self, batch_data):
        self.current_batch = batch_data
        self.refresh_results()

    def refresh_results(self):
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.current_batch:
            lbl = QLabel("No active batch. Go to Upload / Capture to start.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 14px;")
            self.container_layout.addWidget(lbl)
            return

        for item in self.current_batch:
            row_frame = QFrame()
            row_frame.setStyleSheet("background: #1e293b; color: white; border-radius: 8px; padding: 10px;" if self.parent.is_dark_mode else "background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px;")
            row_layout = QHBoxLayout(row_frame)
            
            lbl_info = QLabel(f"<b>Batch:</b> {item['batch_id']} | <b>File:</b> {item['filename']} | <b>Type:</b> {item['type']} | <b>Confidence:</b> {item['conf']:.1f}%")
            lbl_info.setStyleSheet("border: none;")
            
            row_layout.addWidget(lbl_info)
            self.container_layout.addWidget(row_frame)

    def save_entire_batch(self):
        if not self.current_batch:
            QMessageBox.warning(self, "Warning", "No active batch results to save!")
            return
            
        success_count = 0
        for item in self.current_batch:
            success, _ = save_inspection_record(
                batch_id=item['batch_id'],
                session_id=item['filename'],
                user_id=1,
                final_fabric_type=item['type'],
                confidence_score=item['conf'],
                is_overridden=False,
                action_status="Batch Processed" 
            )
            if success:
                success_count += 1
                
        if success_count > 0:
            QMessageBox.information(self, "Success", f"All {success_count} results saved to database!")
            self.current_batch = [] # Clear memory after saving
            self.refresh_results()
            self.parent.switch_page(5) # Switch to Reports
        else:
            QMessageBox.critical(self, "Error", "Failed to save data.")