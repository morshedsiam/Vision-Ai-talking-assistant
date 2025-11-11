# yolo_detector.py
from ultralytics import YOLO
import numpy as np

class ScreenElementDetector:
    """YOLOv8 detector for screen UI elements"""
    
    def __init__(self, model_path='runs/train/screen_detector_v13/weights/best.pt', confidence=0.4):
        """
        Args:
            model_path: Path to trained YOLOv8 weights
            confidence: Minimum confidence threshold (0-1)
        """
        print(f"📦 Loading model: {model_path}")
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.class_names = self.model.names
        print(f"✅ Model loaded with {len(self.class_names)} classes")
    
    def detect(self, frame):
        """
        Detect UI elements in frame
        
        Args:
            frame: numpy array (H, W, 3) RGB image
            
        Returns:
            list of detections: [
                {
                    'bbox': [x1, y1, x2, y2],
                    'class_id': int,
                    'class_name': str,
                    'confidence': float,
                    'center': [x, y]
                },
                ...
            ]
        """
        results = self.model(frame, verbose=False, conf=self.confidence)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = self.class_names[class_id]
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': round(conf, 3),
                    'center': [int((x1+x2)/2), int((y1+y2)/2)]
                })
        
        return detections
    
    def get_clickable_objects(self, detections):
        """
        Filter only clickable UI elements
        
        Returns: List of clickable detections
        """
        clickable_classes = [
            'Search button',
            'WhatsApp Send Button',
            'Search box',
            'WhatsApp Message box'
        ]
        
        return [d for d in detections if d['class_name'] in clickable_classes]
    
    def format_for_llm(self, detections):
        """
        Format detections as text for LLM input
        
        Returns: String description of detected objects
        """
        if not detections:
            return "No UI elements detected."
        
        text = f"Detected {len(detections)} UI elements:\n"
        for i, det in enumerate(detections, 1):
            text += f"{i}. {det['class_name']} at position {det['center']} (confidence: {det['confidence']:.2f})\n"
        
        return text


# Test the detector
if __name__ == "__main__":
    from screen_capture import ScreenCapture
    
    detector = ScreenElementDetector(confidence=0.4)
    capture = ScreenCapture(target_fps=10, resize=(640, 640))
    
    print("\n🧪 Testing detector for 10 seconds...\n")
    
    for frame in capture.capture_stream(duration=10):
        detections = detector.detect(frame)
        
        if detections:
            print(detector.format_for_llm(detections))
            print("\nClickable objects:")
            clickable = detector.get_clickable_objects(detections)
            for obj in clickable:
                print(f"  - {obj['class_name']} at {obj['center']}")
            print("-" * 50)
    
    print("\n✅ Detector test complete!")