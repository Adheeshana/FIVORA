import os

# ============================================================
# FIVORA — INDUSTRIAL SYSTEM CONFIGURATION
# ============================================================

APP_NAME = "FIVORA"
APP_TITLE = "FIVORA — Industrial Fabric Inspection System"
APP_SUBTITLE = "Workstation Quality Control & Traceability Engine"

# --- Camera & Image Acquisition Configuration ---
DEFAULT_CAMERA_URL = "http://172.31.98.149:8080/video"
DEFAULT_CAMERA_NAME = "QC Conveyor Camera 1"
DEFAULT_HTTP_PORT = 8080
DEFAULT_RTSP_PORT = 8080
DEFAULT_FPS = 30
DEFAULT_RESOLUTION = (1920, 1080)
CAMERA_RECONNECT_INTERVAL_SEC = 5.0
FRAME_PROCESSING_INTERVAL_SEC = 0.5

# --- AI Thresholds & Machine Vision Configuration ---
CLASSIFICATION_THRESHOLD_PERCENT = 70.0
DEFECT_DETECTION_THRESHOLD_PERCENT = 50.0

FABRIC_CATEGORIES = [
    "Cotton", "Denim", "Silk", "Linen", "Polyester", 
    "Wool", "Rayon", "Nylon", "Satin"
]

DEFECT_CATEGORIES = [
    "Hole", "Stain", "Thread Tear", "Weft Curl", 
    "Color Variation", "Snag", "Oil Spot"
]

INSPECTION_STATES = [
    "SYSTEM READY",
    "CAMERA DISCONNECTED",
    "CAMERA CONNECTING",
    "CAMERA ONLINE",
    "ACQUIRING IMAGE",
    "PROCESSING",
    "INSPECTING",
    "PASS",
    "DEFECT DETECTED",
    "OPERATOR REVIEW",
    "ACCEPTED",
    "REJECTED",
    "ERROR"
]

# --- File & Storage Configuration ---
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
MAX_FILE_SIZE_MB = 5.0
MIN_STORAGE_FREE_MB = 5.0
CAPTURED_BATCHES_DIR = "captured_batches"

# Ensure batch directory exists
os.makedirs(CAPTURED_BATCHES_DIR, exist_ok=True)
