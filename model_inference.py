import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.densenet import preprocess_input
from tensorflow.keras.preprocessing import image

class FabricClassifier:
    """
    Industrial AI Fabric Classifier.
    Classifies fabric samples into 9 industrial categories using the real model.
    """
    def __init__(self, model_path="fabric_classifier_model/fabric_classifier.keras"):
        self.model_path = model_path
        self.model = None
        
        self.classes = [
            "Chiffon", "Cotton", "Denim", "Linen", "Polyester", 
            "Silk", "Velvet", "Viscose", "Wool"
        ]
        self.status = "OFFLINE"
        self.load_model()

    def load_model(self):
        try:
            possible_paths = [
                self.model_path,
                "fabric_classifier.keras",
                os.path.join("fabric_classifier_model", "densenet_fabric.h5"),
                os.path.join("fabric_classifier_model", "fabric_classifier.h5")
            ]
            
            loaded_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    loaded_path = p
                    break

            if loaded_path:
                self.model = tf.keras.models.load_model(loaded_path)
                self.status = "ONLINE"
                print(f"[SUCCESS] Real Fabric Classification Model loaded from {loaded_path}")
            else:
                self.status = "ERROR"
                print("[ERROR] Classification model NOT FOUND! Please check the folder path.")
        except Exception as e:
            self.status = "ERROR"
            print(f"[ERROR] Model Load Error: {e}")

    def preprocess_image(self, img_path):
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            
            return preprocess_input(img_array)
    
    def predict_detailed(self, img_path):
            """
            Real AI model mathi prediction return kare che.
            """
            if self.model is None:
                return {
                    "fabric_type": "MODEL ERROR",
                    "confidence": 0.0,
                    "status": "ERROR",
                    "top_predictions": [("Error", 0.0)]
                }
    
            try:
                processed_img = self.preprocess_image(img_path)
                preds = self.model.predict(processed_img, verbose=0)[0]
                top_indices = np.argsort(preds)[::-1]
                
                top_class_idx = top_indices[0]
                confidence = float(preds[top_class_idx]) * 100.0
                
                predicted_class = self.classes[top_class_idx] if top_class_idx < len(self.classes) else "Unknown"
                
                top_preds = []
                for idx in top_indices[:3]:
                    c_name = self.classes[idx] if idx < len(self.classes) else f"Cat_{idx}"
                    c_conf = float(preds[idx]) * 100.0
                    top_preds.append((c_name, round(c_conf, 1)))
    
                return {
                    "fabric_type": predicted_class,
                    "confidence": round(confidence, 1),
                    "status": self.status,
                    "top_predictions": top_preds
                }
            except Exception as e:
                print(f"[ERROR] Prediction failed for {img_path}: {e}")
                return {
                    "fabric_type": "ERROR",
                    "confidence": 0.0,
                    "status": "ERROR",
                    "top_predictions": [("Error", 0.0)]
                }

    def predict(self, img_path):
        res = self.predict_detailed(img_path)
        return res["fabric_type"], res["confidence"]