import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import shutil # FR 52 සඳහා Hard Disk ඉඩ බලන්න Import කළා
from datetime import datetime

class ReportGenerator:
    @staticmethod
    def export_to_csv(records, filename="fivora_inspection_history.csv"):
        try:
            # --- FR 52: Handle Storage Limit Exceeded Error ---
            total, used, free = shutil.disk_usage(os.getcwd())
            if free < 5 * 1024 * 1024: # Hard Disk එකේ ඉඩ 5MB වලට වඩා අඩු නම්
                return False, "Storage Limit Exceeded Error: Not enough disk space to save the CSV report!"

            df = pd.DataFrame(records, columns=["Batch ID", "Image Name", "Fabric Type", "Confidence (%)", "Is Overridden", "Action Status", "Timestamp"])
            df.to_csv(filename, index=False)
            return True, f"CSV Report exported successfully to:\n{os.path.abspath(filename)}"
        except Exception as e:
            return False, f"CSV export failed: {e}"

    @staticmethod
    def export_to_pdf(records, batch_name, filename="fivora_latest_report.pdf"):
        try:
            # --- FR 52: Handle Storage Limit Exceeded Error ---
            total, used, free = shutil.disk_usage(os.getcwd())
            if free < 5 * 1024 * 1024: # Hard Disk එකේ ඉඩ 5MB වලට වඩා අඩු නම්
                return False, "Storage Limit Exceeded Error: Not enough disk space to save the PDF report!"

            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 50, "FIVORA - Fabric Quality Inspection Report")
            
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 90, f"Report Scope: {batch_name}")
            c.drawString(50, height - 110, f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, height - 130, f"Total Images Inspected: {len(records)}")
            
            c.line(50, height - 150, width - 50, height - 150)
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 180, "Batch Summary:")
            
            c.setFont("Helvetica", 10)
            y_pos = height - 210
            for i, rec in enumerate(records[:30]): 
                text_line = f"Image: {rec[1]} | Type: {rec[2]} | Conf: {rec[3]} | Action: {rec[5]}"
                c.drawString(60, y_pos, text_line)
                y_pos -= 20
                if y_pos < 50:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_pos = height - 50
                    
            if len(records) > 30:
                c.drawString(60, y_pos - 20, f"... and {len(records) - 30} more images. (Please export CSV for full list)")

            c.save()
            return True, f"PDF Report exported successfully to:\n{os.path.abspath(filename)}"
        except Exception as e:
            return False, f"PDF export failed: {e}"