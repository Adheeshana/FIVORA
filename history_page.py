from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QComboBox)
from PyQt6.QtCore import Qt
from database import fetch_user_history
from report_generator import ReportGenerator

class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.saved_export_directory = None
        self.all_records = []
        
        # Main layout for the page
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 20)
        
        # --- Header with Dropdown ---
        header_layout = QHBoxLayout()
        title = QLabel("Saved Reports & History")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        
        self.batch_combo = QComboBox()
        self.batch_combo.addItem("All Batches")
        self.batch_combo.currentTextChanged.connect(self.filter_by_batch)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filter by Batch:"))
        header_layout.addWidget(self.batch_combo)
        main_layout.addLayout(header_layout)
        
        # --- Table (This will automatically scroll internally) ---
        self.table = QTableWidget()
        self.table.setColumnCount(7) 
        self.table.setHorizontalHeaderLabels(["Batch ID", "Image Name", "Fabric Type", "Confidence", "Overridden", "Action", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table, 1) 
        
        # --- Bottom Buttons (Always Visible) ---
        btn_layout = QHBoxLayout()
        self.btn_pdf = QPushButton("Export Visible to PDF")
        self.btn_pdf.setStyleSheet("background-color: #ef4444; color: white; padding: 12px; font-weight: bold; border-radius: 6px;")
        self.btn_pdf.clicked.connect(self.export_pdf)
        
        self.btn_csv = QPushButton("Export Visible to CSV")
        self.btn_csv.setStyleSheet("background-color: #10b981; color: white; padding: 12px; font-weight: bold; border-radius: 6px;")
        self.btn_csv.clicked.connect(self.export_csv)
        
        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_csv)
        main_layout.addLayout(btn_layout)

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.batch_combo.setStyleSheet("QComboBox { background: #1e293b; color: white; padding: 5px; border-radius: 4px; border: 1px solid #334155; }")
            self.table.setStyleSheet("background-color: #1e293b; color: white; border: 1px solid #334155; gridline-color: #334155;")
            self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #0f172a; color: white; border: 1px solid #334155; }")
        else:
            self.setStyleSheet("background-color: #f8fafc; color: #0f172a;")
            self.batch_combo.setStyleSheet("QComboBox { background: white; color: black; padding: 5px; border-radius: 4px; border: 1px solid #cbd5e1; }")
            self.table.setStyleSheet("background-color: white; color: black; border: 1px solid #cbd5e1; gridline-color: #cbd5e1;")
            self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #f1f5f9; color: black; border: 1px solid #cbd5e1; }")

    def refresh_data(self):
        self.all_records = fetch_user_history(1) 
        
        batches = list(set([r[0] for r in self.all_records]))
        self.batch_combo.blockSignals(True)
        self.batch_combo.clear()
        self.batch_combo.addItem("All Batches")
        self.batch_combo.addItems(sorted(batches, reverse=True))
        self.batch_combo.blockSignals(False)
        
        self.filter_by_batch("All Batches")

    def filter_by_batch(self, selected_batch):
        if selected_batch == "All Batches":
            display_records = self.all_records
        else:
            display_records = [r for r in self.all_records if r[0] == selected_batch]
            
        self.table.setRowCount(len(display_records))
        for row_idx, row_data in enumerate(display_records):
            for col_idx, data in enumerate(row_data):
                if col_idx == 4:
                    val = "Yes" if data == 1 else "No"
                elif col_idx == 3:
                    val = f"{float(data):.1f}%" if data else "--%"
                else:
                    val = str(data)
                
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def get_export_path(self, default_name):
        if not self.saved_export_directory:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save Reports")
            if dir_path:
                self.saved_export_directory = dir_path
            else:
                return None
        return f"{self.saved_export_directory}/{default_name}"

    def get_visible_records(self):
        records = []
        for row in range(self.table.rowCount()):
            record = [self.table.item(row, col).text() for col in range(self.table.columnCount())]
            records.append(record)
        return records

    def export_pdf(self):
        records = self.get_visible_records()
        if not records:
            QMessageBox.warning(self, "Warning", "No records found.")
            return
            
        batch_name = self.batch_combo.currentText()
        filename = f"fivora_{batch_name}_report.pdf" if batch_name != "All Batches" else "fivora_all_reports.pdf"
        filepath = self.get_export_path(filename)
        if not filepath: return

        from report_generator import ReportGenerator
        success, msg = ReportGenerator.export_to_pdf(records, batch_name, filename=filepath)
        QMessageBox.information(self, "Export Status", msg)

    def export_csv(self):
        records = self.get_visible_records()
        if not records:
            QMessageBox.warning(self, "Warning", "No records found.")
            return
            
        batch_name = self.batch_combo.currentText()
        filename = f"fivora_{batch_name}_report.csv" if batch_name != "All Batches" else "fivora_all_reports.csv"
        filepath = self.get_export_path(filename)
        if not filepath: return

        from report_generator import ReportGenerator
        success, msg = ReportGenerator.export_to_csv(records, filename=filepath)
        QMessageBox.information(self, "Export Status", msg)