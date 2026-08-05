import os
import cv2
from PIL import Image

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
MAX_FILE_SIZE_MB = 10
MIN_RESOLUTION = (224, 224)
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
    
    # Check Blur
    try:
        cv_img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        if cv_img is not None:
            laplacian_var = cv2.Laplacian(cv_img, cv2.CV_64F).var()
            if laplacian_var < 15.0:  
                print(f"❌ REJECTED {file_path}: Image is Blurry (Score: {laplacian_var:.1f})")
                return False, "Image is too blurry."
    except Exception:
        pass

    # Check Resolution
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]:
                print(f"❌ REJECTED {file_path}: Resolution too low ({width}x{height}). Needs 224x224.")
                return False, "Resolution too low."
            if width > MAX_RESOLUTION[0] or height > MAX_RESOLUTION[1]:
                return False, "Resolution too high."
    except Exception as e:
        return False, "Invalid image data."
        
    print(f"✅ PASSED {file_path}: Valid Fabric Image.")
    return True, "Image validation passed."