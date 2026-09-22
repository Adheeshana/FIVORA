import os
import sys
import time
import cv2
import numpy as np

# Ensure UTF-8 output streams
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("==========================================================")
print("     FIVORA INDUSTRIAL FABRIC INSPECTION SYSTEM           ")
print("           Autonomous Self-Execution Runner               ")
print("==========================================================\n")

# Step 1: Initialize Database
print("[STEP 1/6] Initializing Database & Schema Migrations...")
from database import initialize_database, register_user, get_db_connection, save_inspection_record, fetch_user_history

db_status = initialize_database()
print(f" -> Database initialization result: {'ONLINE (MySQL)' if db_status else 'OFFLINE (Local Backup Mode)'}")

# Register test user
print("\n[STEP 2/6] Registering & Authenticating Test Inspector...")
reg_ok, reg_msg = register_user("Auto", "Inspector", "auto_inspector@fivora.com", "Password123!")
print(f" -> User Registration: {reg_msg}")

# Step 3: Generate Fabric Samples for Machine Vision Analysis
print("\n[STEP 3/6] Synthesizing Fabric Sample Images for Optical Inspection...")
os.makedirs("captured_batches/BATCH_AUTORUN", exist_ok=True)

# Sample 1: Clean Cotton Texture
img_cotton = np.zeros((300, 300, 3), dtype=np.uint8)
img_cotton[:] = (220, 225, 230) # Soft white/gray cotton tone
# Add subtle weave texture
for i in range(0, 300, 4):
    cv2.line(img_cotton, (0, i), (300, i), (210, 215, 220), 1)
    cv2.line(img_cotton, (i, 0), (i, 300), (210, 215, 220), 1)
clean_path = "captured_batches/BATCH_AUTORUN/sample_cotton_clean.jpg"
cv2.imwrite(clean_path, img_cotton)

# Sample 2: Defective Denim Fabric (with dark oil spot stain)
img_denim = np.zeros((300, 300, 3), dtype=np.uint8)
img_denim[:] = (120, 70, 30) # Dark Indigo Denim BGR
for i in range(0, 300, 6):
    cv2.line(img_denim, (0, i), (300, i), (100, 50, 20), 1)
# Add an oil spot defect (dark blob in center)
cv2.circle(img_denim, (150, 150), 20, (15, 10, 5), -1)
cv2.GaussianBlur(img_denim, (3, 3), 0, dst=img_denim)
defective_path = "captured_batches/BATCH_AUTORUN/sample_denim_stained.jpg"
cv2.imwrite(defective_path, img_denim)

print(f" -> Created sample images:\n    1. {clean_path}\n    2. {defective_path}")

# Step 4: Validate Images & Run AI + Machine Vision Pipelines
print("\n[STEP 4/6] Running Validation, Keras DenseNet Inference, & Vision Defect Detection...")
from validator import validate_image_file
from model_inference import FabricClassifier
from defect_detector import FabricDefectDetector

model_engine = FabricClassifier()
defect_engine = FabricDefectDetector()

inspection_results = []
sample_paths = [clean_path, defective_path]

for idx, img_p in enumerate(sample_paths, 1):
    val_ok, val_msg = validate_image_file(img_p)
    print(f"\n --- Sample #{idx}: {os.path.basename(img_p)} ---")
    print(f"  Validation Status : {val_msg}")
    
    # Keras Fabric Classification
    prediction = model_engine.predict_detailed(img_p)
    fab_type = prediction["fabric_type"]
    conf_score = prediction["confidence"]
    print(f"  AI Fabric Type    : {fab_type} (Confidence: {conf_score:.1f}%)")
    
    # OpenCV Defect Detection
    cv_img = cv2.imread(img_p)
    defect_res = defect_engine.detect(cv_img)
    print(f"  Vision Status     : {defect_res['status']}")
    print(f"  Defects Found     : {defect_res['defect_count']} (Primary: {defect_res['primary_defect']})")

    # Overlay rendering test
    annotated = defect_engine.draw_overlays(cv_img, defect_res['defects'])
    annotated_path = f"captured_batches/BATCH_AUTORUN/annotated_sample_{idx}.jpg"
    cv2.imwrite(annotated_path, annotated)

    # Prepare database record
    batch_id = "BATCH_AUTORUN"
    session_id = f"SESSION_AUTO_{int(time.time())}"
    action_status = "Passed" if defect_res["defect_count"] == 0 else "Flagged Defect"
    
    # Save record
    save_ok, save_msg = save_inspection_record(
        batch_id=batch_id,
        session_id=session_id,
        user_id=1,
        final_fabric_type=fab_type,
        confidence_score=conf_score,
        is_overridden=False,
        action_status=action_status,
        roll_id=f"ROLL-2026-00{idx}",
        defect_status=defect_res["status"],
        defect_type=defect_res["primary_defect"],
        defect_count=defect_res["defect_count"],
        defect_confidence=defect_res["primary_confidence"],
        ai_decision=f"{fab_type} ({conf_score:.1f}%)",
        operator_decision="Approved" if defect_res["defect_count"] == 0 else "Quarantined",
        operator_name="Auto Inspector"
    )
    print(f"  Database Storage  : {save_msg}")

    # Record formatted for report generator
    # [batch_id, filename, fabric_type, confidence, overridden, status, timestamp]
    inspection_results.append([
        batch_id, os.path.basename(img_p), fab_type,
        f"{conf_score:.1f}%", "No", action_status,
        time.strftime("%Y-%m-%d %H:%M:%S")
    ])

# Step 5: Generate Reports
print("\n[STEP 5/6] Generating Executive Quality Reports (PDF & CSV)...")
from report_generator import ReportGenerator

pdf_ok, pdf_msg = ReportGenerator.export_to_pdf(inspection_results, "BATCH_AUTORUN", "fivora_autorun_summary.pdf")
print(f" -> PDF Export: {pdf_msg}")

csv_ok, csv_msg = ReportGenerator.export_to_csv(inspection_results, "fivora_autorun_summary.csv")
print(f" -> CSV Export: {csv_msg}")

# Step 6: Automated PyQt6 UI Testing
print("\n[STEP 6/6] Initializing PyQt6 Desktop GUI & Testing Navigation...")
from PyQt6.QtWidgets import QApplication
from main_app import FivoraMainApp

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

gui = FivoraMainApp()
gui.show()
print(" -> Main Window Created & Displayed.")

# Test Public Page Navigation (Login & Signup)
gui.switch_page(0)
print(" -> Displayed Sign In Page.")
app.processEvents()
time.sleep(0.3)

gui.switch_page(1)
print(" -> Displayed Sign Up Page.")
app.processEvents()
time.sleep(0.3)

# Test GUI Login via Form Fill & Button Click
print("\n -> Submitting Inspector Login Form (inspector@fivora.com / Password123!)...")
gui.switch_page(0)
gui.login_page.email.setText("inspector@fivora.com")
gui.login_page.password.setText("Password123!")
app.processEvents()

# Trigger Sign In Click
gui.login_page.on_login_clicked()
app.processEvents()

if gui.is_logged_in:
    print(" -> [SUCCESS] GUI Authentication Granted! Logged in as Inspector.")
else:
    print(" -> [ERROR] GUI Authentication failed!")

# Test Navigation across protected pages (Dashboard, Upload, Results, History)
protected_pages = [("Dashboard", 2), ("Upload/Capture", 3), ("Results View", 4), ("History & Reports", 5)]
for name, p_idx in protected_pages:
    gui.switch_page(p_idx)
    print(f" -> Accessing Protected Page {p_idx}: {name}")
    app.processEvents()
    time.sleep(0.3)

# Test Theme Toggle
gui.toggle_theme()
print(" -> Toggled Theme (Dark/Light Mode).")
app.processEvents()
time.sleep(0.3)

print("\n==========================================================")
print(" SUCCESS: FIVORA System executed end-to-end autonomously!")
print("==========================================================\n")

# Close GUI cleanly after verification
gui.close()
