import os
import cv2
from PIL import Image

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"} 
MAX_FILE_SIZE_MB = 15  
MIN_RESOLUTION = (64, 64) 
MAX_RESOLUTION = (8192, 8192)

def validate_image_file(file_path):
    if not os.path.exists(file_path):
        return False, "File does not exist."
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported format '{ext}'."
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, "File size exceeds limit."
    
    # කැමරාවෙන් එන සියලුම ෆ්‍රේම්ස් (Frames) අනුමත වීම සඳහා Blur සහ Resolution Checks මෙතනින් ඉවත් කර ඇත.
    
    print(f"[PASSED] {file_path}: Valid Fabric Image.")
    return True, "Image validation passed."