import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, 
    QComboBox, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from database import fetch_user_history
from report_generator import ReportGenerator
from custom_dialog import show_message_dialog, show_success_dialog


class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.saved_export_directory = None
        self.all_records = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        # ----------------------------------------------------
        # 1. HEADER WITH BATCH FILTER
        # ----------------------------------------------------
        header_layout = QHBoxLayout()
        title = QLabel("INSPECTION HISTORY & TRACEABILITY REPORTS")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0ea5e9; letter-spacing: 1px;")

        self.batch_combo = QComboBox()
        self.batch_combo.addItem("All Batches")
        self.batch_combo.currentTextChanged.connect(self.filter_by_batch)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Filter Batch:"))
        header_layout.addWidget(self.batch_combo)
        main_layout.addLayout(header_layout)

        # ----------------------------------------------------
        # 2. INDUSTRIAL QUALITY SUMMARY (KPI CARDS)
        # ----------------------------------------------------
        kpi_lay = QHBoxLayout()
        kpi_lay.setSpacing(12)

        self.card_total = self.create_kpi_card("TOTAL INSPECTED", "0", "#00A3FF")
        self.card_pass_rate = self.create_kpi_card("PASS RATE %", "0.0%", "#10b981")
        self.card_reject_rate = self.create_kpi_card("REJECT RATE %", "0.0%", "#ef4444")
        self.card_defects = self.create_kpi_card("DEFECT COUNT", "0", "#f59e0b")
        self.card_overrides = self.create_kpi_card("OVERRIDE COUNT", "0", "#8b5cf6")

        kpi_lay.addWidget(self.card_total)
        kpi_lay.addWidget(self.card_pass_rate)
        kpi_lay.addWidget(self.card_reject_rate)
        kpi_lay.addWidget(self.card_defects)
        kpi_lay.addWidget(self.card_overrides)

        main_layout.addLayout(kpi_lay)

        # ----------------------------------------------------
        # 3. TRACEABILITY DATA TABLE
        # ----------------------------------------------------
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        headers = [
            "Batch ID", "Roll ID", "Image Name", "Fabric Type", 
            "Confidence", "Defect Status", "Defect Type", "Defect Count", 
            "Operator Action", "Operator", "Timestamp"
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table, 1)

        # ----------------------------------------------------
        # 4. EXPORT TOOLBAR
        # ----------------------------------------------------
        btn_layout = QHBoxLayout()
        self.btn_pdf = QPushButton("📄 Export Visible Records to Executive PDF")
        self.btn_pdf.setStyleSheet("background-color: #ef4444; color: white; padding: 12px; font-weight: bold; border-radius: 6px;")
        self.btn_pdf.clicked.connect(self.export_pdf)

        self.btn_csv = QPushButton("📊 Export Visible Records to Structured CSV")
        self.btn_csv.setStyleSheet("background-color: #10b981; color: white; padding: 12px; font-weight: bold; border-radius: 6px;")
        self.btn_csv.clicked.connect(self.export_csv)

        btn_layout.addWidget(self.btn_pdf)
        btn_layout.addWidget(self.btn_csv)
        main_layout.addLayout(btn_layout)

        self.apply_theme(True)

    def create_kpi_card(self, title, val, accent_color):
        card = QFrame()
        card.setFixedHeight(64)
        card.setStyleSheet("QFrame { background: #111827; border: 1px solid #1e293b; border-radius: 8px; }")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet("font-size: 9px; font-weight: bold; color: #64748b;")

        lbl_v = QLabel(val)
        lbl_v.setObjectName("kpi_val")
        lbl_v.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {accent_color};")

        lay.addWidget(lbl_t)
        lay.addWidget(lbl_v)
        return card

    def apply_theme(self, is_dark):
        if is_dark:
            self.setStyleSheet("background-color: #0b0f19; color: white;")
            self.batch_combo.setStyleSheet("QComboBox { background: #1e293b; color: white; padding: 6px; border-radius: 4px; border: 1px solid #334155; }")
            self.table.setStyleSheet("background-color: #1e293b; color: white; border: 1px solid #334155; gridline-color: #334155;")
            self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: #0f172a; color: white; border: 1px solid #334155; font-weight: bold; }")

    def refresh_data(self):
        self.all_records = fetch_user_history(1)
        
        batches = sorted(list(set([str(r[0]) for r in self.all_records])), reverse=True)
        self.batch_combo.blockSignals(True)
        self.batch_combo.clear()
        self.batch_combo.addItem("All Batches")
        self.batch_combo.addItems(batches)
        self.batch_combo.blockSignals(False)

        self.filter_by_batch("All Batches")

    def filter_by_batch(self, selected_batch):
        if selected_batch == "All Batches":
            display_records = self.all_records
        else:
            display_records = [r for r in self.all_records if str(r[0]) == selected_batch]

        # Calculate KPIs
        total_count = len(display_records)
        accepted_count = 0
        total_defects = 0
        override_count = 0

        self.table.setRowCount(total_count)
        for row_idx, row_data in enumerate(display_records):
            # Extract attributes from tuple safely
            batch_id = str(row_data[0]) if len(row_data) > 0 else "N/A"
            session_id = str(row_data[1]) if len(row_data) > 1 else "sample.jpg"
            ftype = str(row_data[2]) if len(row_data) > 2 else "Cotton"
            conf = f"{float(row_data[3]):.1f}%" if len(row_data) > 3 and row_data[3] else "--%"
            is_overridden = "Yes" if len(row_data) > 4 and str(row_data[4]) in ["1", "True", "Yes"] else "No"
            action = str(row_data[5]) if len(row_data) > 5 else "ACCEPTED"
            ts = str(row_data[6]) if len(row_data) > 6 else ""

            roll_id = str(row_data[7]) if len(row_data) > 7 and row_data[7] else f"ROLL-{batch_id}"
            d_status = str(row_data[8]) if len(row_data) > 8 and row_data[8] else ("DEFECT DETECTED" if "Reject" in action else "PASS")
            d_type = str(row_data[9]) if len(row_data) > 9 and row_data[9] else "None"
            d_count = int(row_data[10]) if len(row_data) > 10 and str(row_data[10]).isdigit() else (1 if d_status == "DEFECT DETECTED" else 0)
            operator_name = str(row_data[14]) if len(row_data) > 14 and row_data[14] else "QC_INSPECTOR_01"

            if "Accept" in action or d_status == "PASS":
                accepted_count += 1
            total_defects += d_count
            if is_overridden == "Yes":
                override_count += 1

            row_items = [
                batch_id, roll_id, session_id, ftype, conf, 
                d_status, d_type, str(d_count), action, operator_name, ts
            ]

            for col_idx, val in enumerate(row_items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

        pass_rate = (accepted_count / total_count * 100) if total_count > 0 else 0.0
        reject_rate = 100.0 - pass_rate if total_count > 0 else 0.0

        # Update KPI Card values
        self.card_total.findChild(QLabel, "kpi_val").setText(str(total_count))
        self.card_pass_rate.findChild(QLabel, "kpi_val").setText(f"{pass_rate:.1f}%")
        self.card_reject_rate.findChild(QLabel, "kpi_val").setText(f"{reject_rate:.1f}%")
        self.card_defects.findChild(QLabel, "kpi_val").setText(str(total_defects))
        self.card_overrides.findChild(QLabel, "kpi_val").setText(str(override_count))

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
        is_dark = getattr(self.parent, 'is_dark_mode', True) if self.parent else True
        if not records:
            show_message_dialog(
                parent=self.window(),
                title="No Records Found",
                message="No inspection records available in the selected view to export.",
                dialog_type="warning",
                button_text="OK",
                is_dark=is_dark
            )
            return
            
        batch_name = self.batch_combo.currentText()
        filename = f"fivora_{batch_name}_executive_report.pdf" if batch_name != "All Batches" else "fivora_all_inspection_reports.pdf"
        filepath = self.get_export_path(filename)
        if not filepath: return

        success, msg = ReportGenerator.export_to_pdf(records, batch_name, filename=filepath)
        if success:
            show_success_dialog(
                parent=self.window(),
                title="PDF Export Successful!",
                message=msg,
                button_text="DONE",
                is_dark=is_dark
            )
        else:
            show_message_dialog(
                parent=self.window(),
                title="Export Failed",
                message=msg,
                dialog_type="error",
                button_text="CLOSE",
                is_dark=is_dark
            )

    def export_csv(self):
        records = self.get_visible_records()
        is_dark = getattr(self.parent, 'is_dark_mode', True) if self.parent else True
        if not records:
            show_message_dialog(
                parent=self.window(),
                title="No Records Found",
                message="No inspection records available in the selected view to export.",
                dialog_type="warning",
                button_text="OK",
                is_dark=is_dark
            )
            return
            
        batch_name = self.batch_combo.currentText()
        filename = f"fivora_{batch_name}_data.csv" if batch_name != "All Batches" else "fivora_all_inspection_data.csv"
        filepath = self.get_export_path(filename)
        if not filepath: return

        success, msg = ReportGenerator.export_to_csv(records, filename=filepath, batch_name=batch_name)
        if success:
            show_success_dialog(
                parent=self.window(),
                title="CSV Table Export Successful!",
                message=f"Inspection data table exported with complete summary headers and formatted columns:\n\n{filepath}",
                button_text="DONE",
                is_dark=is_dark
            )
        else:
            show_message_dialog(
                parent=self.window(),
                title="Export Failed",
                message=msg,
                dialog_type="error",
                button_text="CLOSE",
                is_dark=is_dark
            )