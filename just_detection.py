# just_detection.py - Pure detection visualization (NO AI, NO SPEECH)
from screen_understanding import ScreenUnderstanding
from screen_capture import ScreenCapture
import cv2
import numpy as np

print("="*70)
print("👁️  PURE DETECTION VIEWER")
print("="*70)
print()
print("Shows ONLY what YOLO detects - no AI, no speech, no generation")
print("Press 'q' to quit")
print()
print("Starting in 3 seconds...")
import time
time.sleep(3)

understanding = ScreenUnderstanding()
capture = ScreenCapture(target_fps=10, resize=(640, 640))

colors = {
    0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255),
    3: (255, 255, 0), 4: (255, 0, 255), 5: (0, 255, 255),
    6: (128, 0, 128), 7: (255, 128, 0), 8: (0, 128, 255),
}

frame_count = 0

for frame in capture.capture_stream(duration=300):
    frame_count += 1
    
    # JUST DETECT (no AI generation!)
    analysis = understanding.analyze_screen(frame)
    
    # Draw detections
    display = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
    
    # Draw each object
    for obj in analysis['objects']:
        x1, y1, x2, y2 = obj['bbox']
        color = colors.get(obj['class_id'], (255, 255, 255))
        
        # Box
        cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
        
        # Label
        label = f"{obj['class_name']} {obj['confidence']:.0%}"
        
        # Background for text
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(display, (x1, y1 - h - 10), (x1 + w, y1), color, -1)
        
        # Text
        cv2.putText(display, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Center dot
        center = obj['center']
        cv2.circle(display, tuple(center), 5, color, -1)
        
        # Clickable marker
        if obj in analysis['clickable_objects']:
            cv2.circle(display, tuple(center), 20, (0, 255, 0), 3)
    
    # Info bar
    info = f"Objects: {analysis['object_count']} | Clickable: {analysis['clickable_count']} | Frame: {frame_count}"
    cv2.putText(display, info, (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Scene caption
    cv2.putText(display, analysis['caption'][:60], (10, 60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)
    
    # Show
    cv2.imshow("Detection View (Press Q to quit)", display)
    
    # Print to console
    if frame_count % 30 == 0:  # Every 3 seconds at 10fps
        print(f"\n[Frame {frame_count}] Detected: {analysis['object_count']} objects")
        for obj in analysis['objects']:
            clickable = "✅" if obj in analysis['clickable_objects'] else "⭕"
            print(f"  {clickable} {obj['class_name']:25} {obj['confidence']:5.1%}")
    
    # Quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("\n✅ Done!")