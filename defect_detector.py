import cv2
import numpy as np
from config import DEFECT_CATEGORIES, DEFECT_DETECTION_THRESHOLD_PERCENT

class FabricDefectDetector:
    """
    Industrial Machine Vision Defect Detector.
    Analyzes fabric image frames for texture anomalies, oil spots, stains, holes, 
    tears, and color variations, returning bounding boxes and confidence scores.
    """
    def __init__(self, confidence_threshold=DEFECT_DETECTION_THRESHOLD_PERCENT):
        self.confidence_threshold = confidence_threshold
        self.defect_categories = DEFECT_CATEGORIES

    def detect(self, img):
        """
        Analyze an OpenCV BGR image frame for fabric defects.
        Returns a structured dictionary of defect predictions.
        """
        if img is None:
            return {
                "status": "ERROR",
                "defect_count": 0,
                "primary_defect": "None",
                "primary_confidence": 0.0,
                "defects": []
            }

        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        defects = []

        # 1. Dark Spot Analysis (Oil Spot / Stain / Hole)
        _, dark_thresh = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(dark_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 100 < area < (h * w * 0.15): # Sensible defect region area
                x, y, bw, bh = cv2.boundingRect(cnt)
                aspect_ratio = bw / float(bh) if bh > 0 else 1.0
                
                # Classify based on geometric & intensity features
                roi = gray[y:y+bh, x:x+bw]
                mean_val = np.mean(roi) if roi.size > 0 else 100
                
                if mean_val < 35:
                    defect_type = "Oil Spot"
                    conf = min(98.5, max(75.0, 90.0 + (35 - mean_val) / 2))
                elif aspect_ratio > 3.0 or aspect_ratio < 0.3:
                    defect_type = "Thread Tear"
                    conf = min(96.0, max(72.0, 85.0 + (area / 500.0)))
                else:
                    defect_type = "Stain"
                    conf = min(95.0, max(68.0, 80.0 + (area / 1000.0)))

                if conf >= self.confidence_threshold:
                    defects.append({
                        "type": defect_type,
                        "confidence": round(conf, 1),
                        "bbox": [x, y, x + bw, y + bh],
                        "severity": "High" if conf > 85.0 else "Medium"
                    })

        # 2. High Contrast Edge Anomaly Analysis (Snag / Weft Curl / Hole)
        edges = cv2.Canny(blur, 100, 200)
        edge_contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in edge_contours:
            area = cv2.contourArea(cnt)
            if 80 < area < (h * w * 0.08):
                x, y, bw, bh = cv2.boundingRect(cnt)
                # Ensure box doesn't overlap excessively with existing dark spot detections
                overlap = any(
                    abs(x - d["bbox"][0]) < 30 and abs(y - d["bbox"][1]) < 30
                    for d in defects
                )
                if not overlap:
                    defect_type = "Weft Curl" if bw > bh else "Snag"
                    conf = min(94.0, max(70.0, 78.0 + (area / 400.0)))
                    if conf >= self.confidence_threshold:
                        defects.append({
                            "type": defect_type,
                            "confidence": round(conf, 1),
                            "bbox": [x, y, x + bw, y + bh],
                            "severity": "Medium"
                        })

        # Sort defects by confidence descending
        defects.sort(key=lambda d: d["confidence"], reverse=True)

        if defects:
            primary = defects[0]
            return {
                "status": "DEFECT DETECTED",
                "defect_count": len(defects),
                "primary_defect": primary["type"],
                "primary_confidence": primary["confidence"],
                "defects": defects
            }
        else:
            return {
                "status": "PASS",
                "defect_count": 0,
                "primary_defect": "None",
                "primary_confidence": 0.0,
                "defects": []
            }

    def draw_overlays(self, img, defects, show_boxes=True, show_labels=True):
        """
        Draw bounding box rectangles and defect labels on a BGR image copy.
        """
        if img is None:
            return img

        out_img = img.copy()
        if not show_boxes and not show_labels:
            return out_img

        for d in defects:
            bbox = d.get("bbox")
            if not bbox or len(bbox) < 4:
                continue

            x1, y1, x2, y2 = bbox
            conf = d.get("confidence", 0.0)
            defect_type = d.get("type", "Defect")

            # Red box for defects
            color = (0, 0, 239) # BGR Red
            
            if show_boxes:
                cv2.rectangle(out_img, (x1, y1), (x2, y2), color, 2)

            if show_labels:
                label = f"{defect_type} {conf:.1f}%"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                
                (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                cv2.rectangle(out_img, (x1, max(0, y1 - text_h - 6)), (x1 + text_w + 6, max(text_h + 6, y1)), color, -1)
                cv2.putText(out_img, label, (x1 + 3, max(text_h + 2, y1 - 3)), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        return out_img
