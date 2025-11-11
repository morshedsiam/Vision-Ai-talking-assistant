# debug_detection.py - Check what's ACTUALLY being detected
from screen_understanding import ScreenUnderstanding
from screen_capture import ScreenCapture
import cv2

print("🔍 DETECTION DEBUGGER")
print("="*70)
print("Open WhatsApp and let's see what gets detected!\n")

understanding = ScreenUnderstanding()
capture = ScreenCapture(target_fps=5, resize=(640, 640))

print("Capturing screen for 10 seconds...")
print("Open WhatsApp NOW!\n")

for frame in capture.capture_stream(duration=10):
    analysis = understanding.analyze_screen(frame)
    
    if analysis['object_count'] > 0:
        print("\n" + "="*70)
        print(f"📊 DETECTED {analysis['object_count']} OBJECTS:")
        print("="*70)
        
        for i, obj in enumerate(analysis['objects'], 1):
            print(f"\n{i}. {obj['class_name']}")
            print(f"   Confidence: {obj['confidence']:.2%}")
            print(f"   Position: {obj['center']}")
            print(f"   BBox: {obj['bbox']}")
            print(f"   Clickable: {'YES ✅' if obj in analysis['clickable_objects'] else 'NO ❌'}")
        
        print("\n" + "="*70)
        print(f"CLICKABLE OBJECTS: {analysis['clickable_count']}")
        print("="*70)
        
        if analysis['clickable_objects']:
            for obj in analysis['clickable_objects']:
                print(f"  ✅ {obj['class_name']} at {obj['center']}")
        else:
            print("  ❌ NONE DETECTED AS CLICKABLE!")
        
        print("\n" + "="*70)

print("\n✅ Debug complete!")