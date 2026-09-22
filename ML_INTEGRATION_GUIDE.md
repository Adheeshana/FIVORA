# FIVORA - ML Model Integration Guide

## Overview

This guide explains how to integrate your fabric defect detection ML model into the FIVORA application.

---

## Current Architecture

### Scan Flow (Current Mock Implementation)

```
User clicks "START SCAN"
    ↓
update_scan_progress() called every 100ms
    ↓
Generate random metrics (simulation)
    ↓
Update UI with metrics
    ↓
Save to database
    ↓
User accepts/rejects roll
```

### Where to Add Your Model

The main scan simulation happens in:
- **File**: `screens/dashboard_screen.py`
- **Method**: `update_scan_progress()`
- **Location**: Around line 180

---

## Step 1: Prepare Your Model

### Supported Frameworks
- TensorFlow/Keras
- PyTorch
- OpenCV
- Custom Python models

### Model Requirements
Your model should:
1. **Input**: Fabric image (numpy array or PIL Image)
2. **Output**: Dictionary containing:
   ```python
   {
       'defects_count': int,      # Number of defects found
       'confidence': float,       # 0-100, confidence percentage
       'quality_score': int,      # 0-100, quality rating
       'defect_locations': list   # Optional: [(x, y, size), ...]
   }
   ```

### Example Model Loading
```python
import tensorflow as tf
import numpy as np

class FabricDetectionModel:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)
    
    def predict(self, image_array):
        """
        Args:
            image_array: numpy array (H, W, C) or PIL Image
        Returns:
            dict with predictions
        """
        # Preprocess
        processed = self._preprocess(image_array)
        
        # Predict
        predictions = self.model.predict(processed)
        
        # Postprocess
        return self._postprocess(predictions)
```

---

## Step 2: Create Model Wrapper

Create a new file: `models/fabric_detector.py`

```python
# models/fabric_detector.py
import numpy as np
from PIL import Image
import threading


class FabricDetector:
    def __init__(self, model_path=None):
        """Initialize detector with optional model file"""
        if model_path:
            self.model = self._load_model(model_path)
        else:
            self.model = None
    
    def _load_model(self, model_path):
        """Load your ML model"""
        # Example with TensorFlow
        import tensorflow as tf
        return tf.keras.models.load_model(model_path)
    
    def predict(self, image_input):
        """
        Predict defects in fabric image
        
        Args:
            image_input: str (path) or numpy array
        
        Returns:
            dict with keys: defects_count, confidence, quality_score
        """
        try:
            # Load image if path provided
            if isinstance(image_input, str):
                image = Image.open(image_input)
                image_array = np.array(image)
            else:
                image_array = image_input
            
            # Preprocess
            processed = self._preprocess(image_array)
            
            # Run inference
            if self.model:
                predictions = self.model.predict(processed)
            else:
                # Fallback to random (for testing)
                import random
                predictions = {
                    'defects': random.randint(0, 5),
                    'confidence': random.randint(70, 99),
                    'quality': random.randint(60, 100)
                }
                return predictions
            
            # Postprocess
            return self._postprocess(predictions)
        
        except Exception as e:
            print(f"Prediction error: {e}")
            return None
    
    def _preprocess(self, image_array):
        """Preprocess image for model"""
        # Resize, normalize, etc.
        # Example:
        from PIL import Image
        img = Image.fromarray(image_array.astype('uint8'))
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        return np.expand_dims(img_array, axis=0)
    
    def _postprocess(self, predictions):
        """Convert model output to required format"""
        return {
            'defects_count': int(predictions[0]),
            'confidence': float(predictions[1]),
            'quality_score': int(predictions[2])
        }
```

---

## Step 3: Integrate Model into Dashboard

### Modify `screens/dashboard_screen.py`

**1. Add import at the top:**
```python
from models.fabric_detector import FabricDetector
```

**2. Modify `__init__` method:**
```python
def __init__(self, user_data):
    super().__init__()
    self.user_data = user_data
    self.scan_running = False
    
    # Initialize ML model
    self.detector = FabricDetector('path/to/your/model.h5')
    
    self.init_ui()
```

**3. Replace `update_scan_progress` method:**
```python
def update_scan_progress(self):
    """Update scan progress with actual model predictions"""
    if self.scan_progress == 0 and not self.current_image:
        # Get image (from camera or file)
        self.current_image = self.capture_image()
    
    self.scan_progress += 10
    
    if self.scan_progress >= 100:
        # Run model inference
        result = self.detector.predict(self.current_image)
        
        if result:
            self.defects_value.setText(str(result['defects_count']))
            self.confidence_value.setText(f"{result['confidence']:.0f}%")
            self.quality_value.setText(str(result['quality_score']))
            self.quality_gauge.set_value(result['quality_score'])
        
        self.scan_timer.stop()
        self.scan_running = False
        # ... rest of code
    else:
        self.progress_bar.setValue(self.scan_progress)
```

**4. Add method to save scan:**
```python
def save_scan_to_database(self):
    """Save scan results to database"""
    from utils.validators import generate_roll_id
    
    roll_id = generate_roll_id()
    defects = int(self.defects_value.text())
    confidence = int(self.confidence_value.text().rstrip('%'))
    quality = int(self.quality_value.text())
    
    self.db_manager.add_scan_log(
        self.user_data['id'],
        roll_id,
        defects,
        confidence,
        quality,
        'completed'
    )
```

---

## Step 4: Add Image Capture/Selection

### Option A: Add Image Selection Dialog

```python
# Add to imports
from PyQt6.QtWidgets import QFileDialog

# Add method to DashboardScreen
def select_image_for_scan(self):
    """Open file dialog to select fabric image"""
    file_dialog = QFileDialog()
    image_path, _ = file_dialog.getOpenFileName(
        self, "Select Fabric Image", "",
        "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
    )
    
    if image_path:
        self.current_image = image_path
        return True
    return False

# Modify on_start_scan method
def on_start_scan(self):
    """Start fabric scan with selected image"""
    if self.select_image_for_scan():
        if not self.scan_running:
            self.scan_running = True
            self.scan_progress = 0
            self.start_button.setEnabled(False)
            self.accept_button.setEnabled(False)
            self.reject_button.setEnabled(False)
            self.progress_bar.setValue(0)
            self.scan_timer.start(100)
```

### Option B: Use Camera/Webcam

```python
# Add to imports
import cv2
from PyQt6.QtCore import QThread, pyqtSignal

# Create camera capture thread
class CameraCaptureThread(QThread):
    image_captured = pyqtSignal(str)

    def run(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite('temp_capture.jpg', frame)
            self.image_captured.emit('temp_capture.jpg')

# Add to DashboardScreen
def capture_from_camera(self):
    """Capture image from webcam"""
    self.camera_thread = CameraCaptureThread()
    self.camera_thread.image_captured.connect(self.start_scan_with_image)
    self.camera_thread.start()

def start_scan_with_image(self, image_path):
    """Start scan with captured image"""
    self.current_image = image_path
    self.on_start_scan()
```

---

## Step 5: Optimize Performance

### Use Threading to Prevent UI Freeze

```python
from PyQt6.QtCore import QThread, pyqtSignal

class ScanThread(QThread):
    progress_updated = pyqtSignal(dict)

    def run(self):
        # Run model in background thread
        result = self.detector.predict(self.image)
        self.progress_updated.emit(result)

# Modify DashboardScreen
def on_start_scan(self):
    """Start scan in background thread"""
    self.start_button.setEnabled(False)
    
    self.scan_thread = ScanThread()
    self.scan_thread.progress_updated.connect(self.update_from_thread)
    self.scan_thread.start()

def update_from_thread(self, prediction):
    """Update UI from scan thread"""
    self.defects_value.setText(str(prediction['defects_count']))
    self.confidence_value.setText(f"{prediction['confidence']}%")
    self.quality_value.setText(str(prediction['quality_score']))
    self.quality_gauge.set_value(prediction['quality_score'])

def on_scan_complete(self):
    """Handle scan completion"""
    self.start_button.setEnabled(True)
    self.accept_button.setEnabled(True)
    self.reject_button.setEnabled(True)
    self.save_scan_to_database()
```

---

## Step 6: Test Your Model

### Create test script: `test_model.py`

```python
from models.fabric_detector import FabricDetector
import time

# Initialize detector
detector = FabricDetector('path/to/your/model.h5')

# Test prediction
start_time = time.time()
result = detector.predict('test_image.jpg')
elapsed_time = time.time() - start_time

print(f"Defects: {result['defects_count']}")
print(f"Confidence: {result['confidence']:.1f}%")
print(f"Quality: {result['quality_score']}")
print(f"Time: {elapsed_time:.2f}s")
```

---

## Step 7: Handle Edge Cases

### Error Handling

```python
def predict_safe(self, image_input):
    """Predict with error handling"""
    try:
        result = self.predict(image_input)
        
        if result is None:
            raise ValueError("Model returned None")
        
        # Validate ranges
        if not (0 <= result['quality_score'] <= 100):
            raise ValueError("Invalid quality score")
        
        return result
    
    except FileNotFoundError:
        print("Model file not found")
        return self._get_default_result()
    
    except Exception as e:
        print(f"Prediction error: {e}")
        return self._get_default_result()

def _get_default_result(self):
    """Return default result on error"""
    return {
        'defects_count': 0,
        'confidence': 0,
        'quality_score': 0
    }
```

---

## Step 8: Deploy

### Production Deployment

1. **Package your model**
   ```bash
   # Save model file
   model.save('fabric_detector_v1.h5')
   ```

2. **Update path in code**
   ```python
   self.detector = FabricDetector('models/fabric_detector_v1.h5')
   ```

3. **Add to requirements if needed**
   ```text
   tensorflow>=2.10.0
   opencv-python>=4.6.0
   ```

4. **Test end-to-end**
   - Create account
   - Login
   - Run scan
   - Verify results saved to database

---

## Performance Optimization Tips

1. **Model Compression**: Use quantization or pruning
2. **Batch Processing**: Process multiple images efficiently
3. **GPU Acceleration**: Use CUDA for TensorFlow/PyTorch
4. **Caching**: Cache model predictions for repeated images
5. **Threading**: Run inference in separate thread (see Step 5)

---

## Debugging

### Enable detailed logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In predict method:
logger.debug(f"Image shape: {image_array.shape}")
logger.debug(f"Predictions: {predictions}")
```

---

## Common Issues

### Issue: Model too slow
**Solution**: Use threading (Step 5) or optimize model

### Issue: Memory errors
**Solution**: Process smaller batches or use model quantization

### Issue: Incorrect predictions
**Solution**: Check image preprocessing & model training data

### Issue: Model file not found
**Solution**: Check file path and use absolute paths

---

## Example Integration (Complete)

See `examples/fabric_detector_example.py` for a complete working example.

---

## Support

For model-specific questions, consult:
- Your ML framework documentation (TensorFlow, PyTorch, etc.)
- Model training repository
- ML community forums
