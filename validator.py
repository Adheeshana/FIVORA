
import re
import os
import cv2

class Validator:
    @staticmethod
    def is_valid_email(email):
        """Validates the format of an email address using Regular Expressions (FR 02)."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not email:
            return False, "Email address cannot be empty."
        if re.match(email_regex, email):
            return True, "Valid Email"
        else:
            return False, "Invalid Email Format. Please enter a valid email."

    @staticmethod
    def validate_image_file(file_path):
        """
        Validates image format, file size, and resolution.
        Covers: FR 17 (Format), FR 18 (Size), FR 19 (Resolution), 
                FR 20 (Quality), FR 48 (Unsupported Format), FR 49 (Size Exceeded).
        """
        # 48 - Handle Unsupported File Format Error & 17 - Check Image File Format
        valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp']
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in valid_extensions:
            return False, f"Unsupported Format Error: '{ext}' is not supported. Please use JPG or PNG."

        # 18 & 49 - Check Image File Size & Handle Size Exceeded Error (Max 10MB)
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 10:
                return False, f"File Size Exceeded Error: Size ({file_size_mb:.1f} MB) exceeds the 10 MB limit."
        except Exception as e:
            return False, f"Error reading file size: {str(e)}"

        # 19 & 20 - Check Image Resolution and Quality
        img = cv2.imread(file_path)
        if img is None:
            return False, "Invalid Image: File is corrupted or unreadable."

        h, w, _ = img.shape
        if h < 200 or w < 200:
            return False, f"Quality Warning: Resolution ({w}x{h}) is too low. Minimum required is 200x200."

        # 21 - Mark Image as Valid
        return True, "Image is Valid"