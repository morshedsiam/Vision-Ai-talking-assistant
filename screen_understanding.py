# screen_understanding.py
from yolo_detector import ScreenElementDetector
from clip_captioner import CLIPScreenCaptioner
import time

class ScreenUnderstanding:
    """
    Combines YOLO object detection + CLIP captioning
    Provides complete screen understanding for AI decision-making
    """
    
    def __init__(self, 
                 yolo_path='runs/train/screen_detector_v13/weights/best.pt',
                 yolo_conf=0.4,
                 device='cuda'):
        """Initialize both models"""
        print("🚀 Initializing Screen Understanding System...\n")
        
        # Load models
        self.detector = ScreenElementDetector(yolo_path, yolo_conf)
        self.captioner = CLIPScreenCaptioner(device=device)
        
        print("✅ Screen Understanding ready!\n")
    
    def analyze_screen(self, frame):
        """
        Fully analyze a screen frame
        
        Args:
            frame: numpy array (H, W, 3)
            
        Returns:
            dict: {
                'caption': str,
                'scene_confidence': float,
                'objects': list of detections,
                'clickable_objects': list,
                'summary': str (formatted for LLM)
            }
        """
        start_time = time.time()
        
        # Get caption
        caption_result = self.captioner.caption_frame(frame, top_k=1)
        
        # Get objects
        objects = self.detector.detect(frame)
        clickable = self.detector.get_clickable_objects(objects)
        
        # Create summary for LLM
        summary = self._format_for_llm(caption_result, objects, clickable)
        
        elapsed = time.time() - start_time
        
        return {
            'caption': caption_result['primary'],
            'scene_confidence': caption_result['confidence'],
            'objects': objects,
            'clickable_objects': clickable,
            'object_count': len(objects),
            'clickable_count': len(clickable),
            'summary': summary,
            'processing_time': round(elapsed, 3)
        }
    
    def _format_for_llm(self, caption_result, objects, clickable):
        """Format analysis as text for LLM"""
        summary = f"""SCREEN ANALYSIS:

Scene: {caption_result['primary']}
Confidence: {caption_result['confidence']:.1%}

Detected Objects ({len(objects)}):"""
        
        if objects:
            for i, obj in enumerate(objects, 1):
                summary += f"\n  {i}. {obj['class_name']} at position {obj['center']} (confidence: {obj['confidence']})"
        else:
            summary += "\n  (none)"
        
        summary += f"\n\nClickable Elements ({len(clickable)}):"
        
        if clickable:
            for i, obj in enumerate(clickable, 1):
                summary += f"\n  {i}. {obj['class_name']} at position {obj['center']}"
        else:
            summary += "\n  (none)"
        
        return summary


# Test the combined system
if __name__ == "__main__":
    from screen_capture import ScreenCapture
    
    print("🧠 Testing Combined Screen Understanding...\n")
    
    # Initialize
    understanding = ScreenUnderstanding()
    capture = ScreenCapture(target_fps=5, resize=(640, 640))
    
    print("📺 Analyzing your screen for 20 seconds...")
    print("Open WhatsApp, File Explorer, or browser to see full analysis!\n")
    
    for frame in capture.capture_stream(duration=20):
        analysis = understanding.analyze_screen(frame)
        
        print("="*70)
        print(f"⏱️  Processing time: {analysis['processing_time']*1000:.0f}ms")
        print(f"📊 Objects: {analysis['object_count']} | Clickable: {analysis['clickable_count']}")
        print("\n" + analysis['summary'])
        print("="*70)
        print()
    
    print("\n✅ Screen Understanding test complete!")