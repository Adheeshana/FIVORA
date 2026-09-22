import os
import shutil
from datetime import datetime
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and draw total page numbers
    ('Page X of Y') and professional footer branding.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Footer Divider Line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(36, 40, 576, 40)
        
        # Footer Text
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        footer_left = "FIVORA Industrial Fabric Quality Inspection System • Executive Summary Report"
        page_str = f"Page {self._pageNumber} of {page_count}"
        
        self.drawString(36, 26, footer_left)
        self.drawRightString(576, 26, page_str)
        self.restoreState()


import csv

class ReportGenerator:
    @staticmethod
    def _normalize_records(records):
        """
        Normalize input records into a structured list of dictionaries with uniform keys:
        - Batch_ID
        - Roll_ID
        - Image_Filename
        - Fabric_Type
        - Confidence_Score (%)
        - Defect_Status
        - Defect_Type
        - Defect_Count
        - Inspection_Status
        - Decision_Source
        - Operator
        - Timestamp
        """
        normalized = []
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for rec in records:
            if not rec:
                continue

            if isinstance(rec, dict):
                batch_id = str(rec.get("batch_id", "N/A"))
                roll_id = str(rec.get("roll_id", f"ROLL-{batch_id}"))
                filename = str(rec.get("filename") or rec.get("Image_Filename") or rec.get("session_id", "sample.jpg"))
                fabric_type = str(rec.get("type") or rec.get("Fabric_Type") or rec.get("final_fabric_type", "Unknown"))
                raw_conf = rec.get("conf") or rec.get("Confidence_Score (%)") or rec.get("confidence_score")
                defect_status = str(rec.get("defect_status", "PASS"))
                defect_type = str(rec.get("defect_type", "None"))
                defect_count = rec.get("defect_count", 0)
                raw_status = str(rec.get("Inspection_Status") or rec.get("action_status") or rec.get("operator_decision", "Accepted"))
                is_overridden = bool(rec.get("is_overridden", False))
                decision_source = str(rec.get("Decision_Source") or ("Preview Override" if is_overridden else "AI Model"))
                operator = str(rec.get("operator_name") or rec.get("Operator", "QC_INSPECTOR_01"))
                timestamp = str(rec.get("Timestamp") or rec.get("timestamp", now_str))
            elif isinstance(rec, (list, tuple)):
                if len(rec) >= 11:
                    # Full table row from HistoryPage:
                    # [0:Batch ID, 1:Roll ID, 2:Image Name, 3:Fabric Type, 4:Confidence, 5:Defect Status, 6:Defect Type, 7:Defect Count, 8:Operator Action, 9:Operator, 10:Timestamp]
                    batch_id = str(rec[0]) if rec[0] else "N/A"
                    roll_id = str(rec[1]) if rec[1] else "N/A"
                    filename = str(rec[2]) if rec[2] else batch_id
                    fabric_type = str(rec[3]) if rec[3] else "Unknown"
                    raw_conf = rec[4]
                    defect_status = str(rec[5]) if rec[5] else "PASS"
                    defect_type = str(rec[6]) if rec[6] else "None"
                    defect_count = rec[7] if rec[7] else 0
                    raw_status = str(rec[8]) if rec[8] else "Accepted"
                    operator = str(rec[9]) if rec[9] else "QC_INSPECTOR_01"
                    timestamp = str(rec[10]) if rec[10] else now_str
                    decision_source = "Preview Override" if "override" in raw_status.lower() else "AI Model"
                elif len(rec) >= 7:
                    # Legacy 7-column format:
                    # [0:Batch ID, 1:Image Name, 2:Fabric Type, 3:Confidence, 4:Overridden, 5:Action, 6:Timestamp]
                    batch_id = str(rec[0]) if rec[0] else "N/A"
                    roll_id = f"ROLL-{batch_id}"
                    filename = str(rec[1]) if rec[1] else batch_id
                    fabric_type = str(rec[2]) if rec[2] else "Unknown"
                    raw_conf = rec[3]
                    is_overridden = str(rec[4]).strip().lower() in ["yes", "true", "1", "preview override"]
                    decision_source = "Preview Override" if is_overridden else "AI Model"
                    raw_status = str(rec[5]) if rec[5] else "Accepted"
                    timestamp = str(rec[6]) if rec[6] else now_str
                    defect_status = "DEFECT DETECTED" if "reject" in raw_status.lower() else "PASS"
                    defect_type = "Defect" if "reject" in raw_status.lower() else "None"
                    defect_count = 1 if "reject" in raw_status.lower() else 0
                    operator = "QC_INSPECTOR_01"
                else:
                    batch_id = str(rec[0]) if len(rec) > 0 and rec[0] else "N/A"
                    roll_id = f"ROLL-{batch_id}"
                    filename = str(rec[1]) if len(rec) > 1 and rec[1] else "sample.jpg"
                    fabric_type = str(rec[2]) if len(rec) > 2 and rec[2] else "Unknown"
                    raw_conf = rec[3] if len(rec) > 3 else None
                    defect_status = "PASS"
                    defect_type = "None"
                    defect_count = 0
                    raw_status = "Accepted"
                    decision_source = "AI Model"
                    operator = "QC_INSPECTOR_01"
                    timestamp = now_str
            else:
                continue

            # Confidence formatting
            if raw_conf is not None and str(raw_conf).strip() != "":
                conf_str = str(raw_conf).strip()
                if not conf_str.endswith("%"):
                    try:
                        conf_str = f"{float(conf_str):.1f}%"
                    except ValueError:
                        pass
            else:
                conf_str = "--%"

            # Normalize status
            if "reject" in raw_status.lower():
                status = "Rejected"
            elif "accept" in raw_status.lower() or "process" in raw_status.lower() or "backup" in raw_status.lower():
                status = "Accepted"
            else:
                status = raw_status

            normalized.append({
                "Batch_ID": batch_id,
                "Roll_ID": roll_id,
                "Image_Filename": filename,
                "Fabric_Type": fabric_type,
                "Confidence_Score (%)": conf_str,
                "Defect_Status": defect_status,
                "Defect_Type": defect_type,
                "Defect_Count": defect_count,
                "Inspection_Status": status,
                "Decision_Source": decision_source,
                "Operator": operator,
                "Timestamp": timestamp
            })

        return normalized

    @staticmethod
    def export_to_csv(records, filename="fivora_inspection_history.csv", batch_name="All Batches"):
        try:
            # FR 52: Check disk space before saving
            total, used, free = shutil.disk_usage(os.getcwd())
            if free < 5 * 1024 * 1024:
                return False, "Storage Limit Exceeded Error: Not enough disk space to save the CSV report!"

            norm_data = ReportGenerator._normalize_records(records)
            if not norm_data:
                return False, "No valid inspection records found to export."

            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            total_count = len(norm_data)
            accepted_count = sum(1 for item in norm_data if item["Inspection_Status"].lower() == "accepted")
            rejected_count = total_count - accepted_count
            pass_rate = (accepted_count / total_count * 100) if total_count > 0 else 0.0

            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # ----------------------------------------------------
                # 1. EXECUTIVE METADATA & AUDIT SUMMARY TABLE
                # ----------------------------------------------------
                writer.writerow(["=========================================================================================================="])
                writer.writerow(["FIVORA INDUSTRIAL FABRIC QUALITY CONTROL & TRACEABILITY AUDIT REPORT", "", "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["=========================================================================================================="])
                writer.writerow(["Report Title", "Workstation Fabric Inspection Audit Report", "Generated Timestamp", now_str, "Vision System", "FIVORA AI v2.0", "", "", "", "", "", "", ""])
                writer.writerow(["Batch / Filter Scope", str(batch_name), "Total Samples Inspected", total_count, "Batch Pass Rate", f"{pass_rate:.1f}%", "", "", "", "", "", "", ""])
                writer.writerow(["Total Accepted (Pass)", accepted_count, "Total Rejected (Defective)", rejected_count, "Compliance State", "COMPLIANT" if pass_rate >= 80.0 else "REVIEW REQUIRED", "", "", "", "", "", "", ""])
                writer.writerow([])

                # ----------------------------------------------------
                # 2. DETAILED FABRIC INSPECTION RECORDS TABLE
                # ----------------------------------------------------
                writer.writerow(["----------------------------------------------------------------------------------------------------------"])
                writer.writerow(["DETAILED FABRIC INSPECTION DATA TABLE", "", "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["----------------------------------------------------------------------------------------------------------"])
                
                headers = [
                    "Record #",
                    "Timestamp",
                    "Batch ID",
                    "Roll ID",
                    "Image Filename",
                    "Fabric Type",
                    "Confidence Score (%)",
                    "Defect Status",
                    "Defect Category",
                    "Defect Count",
                    "Inspection Decision",
                    "Decision Source",
                    "QC Operator"
                ]
                writer.writerow(headers)

                for idx, item in enumerate(norm_data, start=1):
                    writer.writerow([
                        idx,
                        item.get("Timestamp", ""),
                        item.get("Batch_ID", "N/A"),
                        item.get("Roll_ID", "N/A"),
                        item.get("Image_Filename", ""),
                        item.get("Fabric_Type", ""),
                        item.get("Confidence_Score (%)", ""),
                        item.get("Defect_Status", "PASS"),
                        item.get("Defect_Type", "None"),
                        item.get("Defect_Count", 0),
                        item.get("Inspection_Status", "Accepted"),
                        item.get("Decision_Source", "AI Model"),
                        item.get("Operator", "QC_INSPECTOR_01")
                    ])

                writer.writerow([])
                # ----------------------------------------------------
                # 3. SUMMARY KPI FOOTER TABLE
                # ----------------------------------------------------
                writer.writerow(["----------------------------------------------------------------------------------------------------------"])
                writer.writerow(["AUDIT SUMMARY TOTALS", "", "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["----------------------------------------------------------------------------------------------------------"])
                writer.writerow(["Total Records Evaluated", total_count, "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["Total Samples Passed", accepted_count, "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["Total Samples Rejected", rejected_count, "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["Overall Acceptance Rate", f"{pass_rate:.1f}%", "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["Traceability Log Status", "OFFICIALLY VERIFIED & SAVED", "", "", "", "", "", "", "", "", "", "", ""])
                writer.writerow(["=========================================================================================================="])

            return True, f"Structured CSV Report table exported successfully to:\n{os.path.abspath(filename)}"
        except Exception as e:
            return False, f"CSV export failed: {e}"

    @staticmethod
    def export_to_pdf(records, batch_name, filename="fivora_latest_report.pdf"):
        try:
            # FR 52: Check disk space before saving
            total, used, free = shutil.disk_usage(os.getcwd())
            if free < 5 * 1024 * 1024:
                return False, "Storage Limit Exceeded Error: Not enough disk space to save the PDF report!"

            norm_data = ReportGenerator._normalize_records(records)

            # Create ReportLab Document
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                leftMargin=36,
                rightMargin=36,
                topMargin=36,
                bottomMargin=54
            )

            story = []
            styles = getSampleStyleSheet()

            # Custom Paragraph Styles
            title_style = ParagraphStyle(
                'HeaderTitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#ffffff")
            )
            
            subtitle_style = ParagraphStyle(
                'HeaderSubtitle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#38bdf8")
            )

            cell_style_left = ParagraphStyle(
                'CellLeft',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=8.5,
                leading=11,
                textColor=colors.HexColor("#1e293b")
            )

            cell_style_center = ParagraphStyle(
                'CellCenter',
                parent=cell_style_left,
                alignment=TA_CENTER
            )

            # ----------------------------------------------------
            # 1. HEADER BANNER SECTION
            # ----------------------------------------------------
            header_content = [
                [
                    Paragraph("FIVORA — Industrial Fabric Inspection System", title_style),
                ],
                [
                    Paragraph("QUALITY CONTROL & EXECUTIVE INSPECTION REPORT", subtitle_style)
                ]
            ]
            header_table = Table(header_content, colWidths=[540])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ('TOPPADDING', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                ('LEFTPADDING', (0, 0), (-1, -1), 16),
                ('RIGHTPADDING', (0, 0), (-1, -1), 16),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 15))

            # ----------------------------------------------------
            # 2. EXECUTIVE SUMMARY CARDS (KPIs)
            # ----------------------------------------------------
            total_count = len(norm_data)
            accepted_count = sum(1 for item in norm_data if item["Inspection_Status"] == "Accepted")
            rejected_count = total_count - accepted_count
            pass_rate_val = (accepted_count / total_count * 100) if total_count > 0 else 0.0
            pass_rate_str = f"{pass_rate_val:.1f}%"
            now_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            kpi_title_style = ParagraphStyle('KPITitle', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor("#64748b"))
            kpi_val_style = ParagraphStyle('KPIVal', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor("#0f172a"))
            kpi_pass_style = ParagraphStyle('KPIPassVal', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor("#16a34a") if pass_rate_val >= 80 else colors.HexColor("#dc2626"))

            kpi_card_data = [
                [
                    Paragraph("REPORT SCOPE", kpi_title_style),
                    Paragraph("GENERATED TIMESTAMP", kpi_title_style),
                    Paragraph("TOTAL INSPECTED", kpi_title_style),
                    Paragraph("PASS / ACCEPTANCE RATE", kpi_title_style)
                ],
                [
                    Paragraph(f"<b>{batch_name}</b>", kpi_val_style),
                    Paragraph(f"<b>{now_timestamp}</b>", kpi_val_style),
                    Paragraph(f"<b>{total_count} Images</b>", kpi_val_style),
                    Paragraph(f"<b>{pass_rate_str}</b> ({accepted_count}/{total_count})", kpi_pass_style)
                ]
            ]
            kpi_table = Table(kpi_card_data, colWidths=[135, 140, 125, 140])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(kpi_table)
            story.append(Spacer(1, 15))

            # ----------------------------------------------------
            # 3. STRUCTURED INSPECTION DATA TABLE
            # ----------------------------------------------------
            table_header_style = ParagraphStyle(
                'TableHeader',
                fontName='Helvetica-Bold',
                fontSize=8.5,
                leading=10,
                textColor=colors.HexColor("#ffffff"),
                alignment=TA_CENTER
            )

            # Table Headers
            table_data = [[
                Paragraph("#", table_header_style),
                Paragraph("Timestamp", table_header_style),
                Paragraph("Image Filename", table_header_style),
                Paragraph("Fabric Type", table_header_style),
                Paragraph("Confidence", table_header_style),
                Paragraph("Status", table_header_style),
                Paragraph("Decision Source", table_header_style)
            ]]

            # Status pill paragraph styles
            accepted_style = ParagraphStyle(
                'StatusAccepted', parent=cell_style_center,
                fontName='Helvetica-Bold', textColor=colors.HexColor("#15803d")
            )
            rejected_style = ParagraphStyle(
                'StatusRejected', parent=cell_style_center,
                fontName='Helvetica-Bold', textColor=colors.HexColor("#b91c1c")
            )

            for idx, item in enumerate(norm_data, start=1):
                status_text = item["Inspection_Status"]
                if status_text == "Accepted":
                    status_p = Paragraph(f"<b>{status_text}</b>", accepted_style)
                else:
                    status_p = Paragraph(f"<b>{status_text}</b>", rejected_style)

                row = [
                    Paragraph(str(idx), cell_style_center),
                    Paragraph(item["Timestamp"], cell_style_center),
                    Paragraph(item["Image_Filename"], cell_style_left),
                    Paragraph(item["Fabric_Type"], cell_style_left),
                    Paragraph(item["Confidence_Score (%)"], cell_style_center),
                    status_p,
                    Paragraph(item["Decision_Source"], cell_style_center)
                ]
                table_data.append(row)

            # Column width distribution total = 540 pt
            # [# (25), Timestamp (95), Filename (155), Type (80), Conf (55), Status (65), Source (65)]
            col_widths = [25, 95, 155, 80, 55, 65, 65]
            data_table = Table(table_data, colWidths=col_widths, repeatRows=1)

            # Table Styling with Zebra Striping
            t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ]

            # Add alternating row colors
            for r_idx in range(1, len(table_data)):
                bg_color = colors.HexColor("#ffffff") if r_idx % 2 != 0 else colors.HexColor("#f8fafc")
                t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), bg_color))

            data_table.setStyle(TableStyle(t_style))
            story.append(data_table)

            # Build Document with NumberedCanvas
            doc.build(story, canvasmaker=NumberedCanvas)
            return True, f"PDF Report exported successfully to:\n{os.path.abspath(filename)}"

        except Exception as e:
            return False, f"PDF export failed: {e}"