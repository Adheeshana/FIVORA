import cv2
import numpy as np
from ultralytics import RTDETR  
from config import DEFECT_DETECTION_THRESHOLD_PERCENT

class FabricDefectDetector:
    """
    Real RT-DETR-L Industrial Machine Vision Defect Detector.
    Analyzes fabric image frames using the custom-trained AI model.
    """
    def __init__(self, model_path="defect_model/best.pt", confidence_threshold=DEFECT_DETECTION_THRESHOLD_PERCENT):
        self.confidence_threshold = confidence_threshold
        try:
            self.model = RTDETR(model_path)
            self.is_loaded = True
            print(f"[SUCCESS] Real RT-DETR-L Defect Detection Model loaded from {model_path}")
        except Exception as e:
            print(f"[ERROR] Could not load RT-DETR Defect Model: {e}")
            self.is_loaded = False

    def detect(self, img):
        if not self.is_loaded or img is None:
            return {
                "status": "ERROR", "defect_count": 0, "primary_defect": "None",
                "primary_confidence": 0.0, "defects": []
            }

        conf_thresh = self.confidence_threshold / 100.0 if self.confidence_threshold > 1 else self.confidence_threshold
        
        results = self.model.predict(source=img, conf=conf_thresh, imgsz=640, verbose=False)
        
        defects = []
        if len(results) > 0:
            boxes = results[0].boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0]) * 100.0
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                
                defects.append({
                    "type": label,
                    "confidence": round(conf, 1),
                    "bbox": [x1, y1, x2, y2] 
                })
        
        defects.sort(key=lambda d: d["confidence"], reverse=True)
        
        d_count = len(defects)
        status = "DEFECT DETECTED" if d_count > 0 else "PASS"
        
        if d_count > 0:
            return {
                "status": status,
                "defect_count": d_count,
                "primary_defect": defects[0]["type"],
                "primary_confidence": defects[0]["confidence"],
                "defects": defects
            }
        else:
            return {
                "status": status,
                "defect_count": 0,
                "primary_defect": "None",
                "primary_confidence": 0.0,
                "defects": []
            }

    def draw_overlays(self, img, defects, show_boxes=True, show_labels=True):
        if img is None:
            return img

        out_img = img.copy()
        if not show_boxes and not show_labels:
            return out_img

        for d in defects:
            bbox = d.get("bbox") or d.get("box")
            if not bbox or len(bbox) < 4:
                continue

            x1, y1, x2, y2 = bbox
            conf = d.get("confidence", 0.0)
            defect_type = d.get("type", "Defect")

            color = (0, 0, 239) 
            
            if show_boxes:
                cv2.rectangle(out_img, (x1, y1), (x2, y2), color, 2)

            if show_labels:
                label = f"{defect_type.upper()} {conf:.1f}%"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                
                (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                cv2.rectangle(out_img, (x1, max(0, y1 - text_h - 6)), (x1 + text_w + 6, max(text_h + 6, y1)), color, -1)
                cv2.putText(out_img, label, (x1 + 3, max(text_h + 2, y1 - 3)), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        return out_img