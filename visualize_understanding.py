# visualize_understanding.py
from screen_understanding import ScreenUnderstanding
from screen_capture import ScreenCapture
import cv2
import numpy as np

class VisualScreenUnderstanding:
    """Display screen understanding with visual overlay"""
    
    def __init__(self):
        self.understanding = ScreenUnderstanding()
        self.capture = ScreenCapture(target_fps=10, resize=(640, 640))
        
        # Colors for different classes (BGR format for OpenCV)
        self.colors = {
            0: (255, 0, 0),      # Disk Driver - Blue
            1: (0, 255, 0),      # Image - Green
            2: (0, 0, 255),      # Notification - Red
            3: (255, 255, 0),    # Search box - Cyan
            4: (255, 0, 255),    # Search button - Magenta
            5: (0, 255, 255),    # Video - Yellow
            6: (128, 0, 128),    # WhatsApp Message box - Purple
            7: (255, 128, 0),    # WhatsApp Send Button - Orange
            8: (0, 128, 255),    # WhatsApp person - Light Blue
        }
    
    def draw_analysis(self, frame, analysis):
        """Draw detections and captions on frame"""
        # Convert RGB to BGR for OpenCV
        display_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
        h, w = display_frame.shape[:2]
        
        # Create info panel at top
        panel_height = 120
        panel = np.zeros((panel_height, w, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)  # Dark gray background
        
        # Draw scene caption
        caption_text = f"Scene: {analysis['caption']}"
        conf_text = f"Confidence: {analysis['scene_confidence']:.1%}"
        
        cv2.putText(panel, caption_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(panel, conf_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Draw object counts
        stats_text = f"Objects: {analysis['object_count']} | Clickable: {analysis['clickable_count']}"
        time_text = f"Speed: {analysis['processing_time']*1000:.0f}ms"
        
        cv2.putText(panel, stats_text, (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(panel, time_text, (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Combine panel with frame
        display_frame = np.vstack([panel, display_frame])
        
        # Draw object detections (offset by panel height)
        for obj in analysis['objects']:
            x1, y1, x2, y2 = obj['bbox']
            y1 += panel_height  # Offset for panel
            y2 += panel_height
            
            color = self.colors.get(obj['class_id'], (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label background
            label = f"{obj['class_name']} {obj['confidence']:.2f}"
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            
            cv2.rectangle(display_frame, 
                         (x1, y1 - label_h - 10), 
                         (x1 + label_w, y1), 
                         color, -1)
            
            # Draw label text
            cv2.putText(display_frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Draw center point
            center_x, center_y = obj['center']
            center_y += panel_height
            cv2.circle(display_frame, (center_x, center_y), 5, color, -1)
            
            # If clickable, add special marker
            if obj in analysis['clickable_objects']:
                cv2.circle(display_frame, (center_x, center_y), 15, (0, 255, 0), 2)
                cv2.putText(display_frame, "CLICK", (center_x - 25, center_y - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        return display_frame
    
    def run(self, duration=300):
        """Run visualization for specified duration (seconds)"""
        print("="*70)
        print("🎬 VISUAL SCREEN UNDERSTANDING")
        print("="*70)
        print("\n📺 Controls:")
        print("   - Press 'q' to quit")
        print("   - Press 's' to save screenshot")
        print("   - Press 'p' to pause/unpause")
        print("\n💡 Tips:")
        print("   - Open WhatsApp, File Explorer, or web browser")
        print("   - See detections appear in real-time!")
        print("   - Clickable objects have green circles\n")
        
        paused = False
        screenshot_count = 0
        
        for frame in self.capture.capture_stream(duration=duration):
            if not paused:
                # Analyze screen
                analysis = self.understanding.analyze_screen(frame)
                
                # Draw visualization
                display_frame = self.draw_analysis(frame, analysis)
            
            # Show frame
            cv2.imshow("Screen Understanding - Live View", display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n⏹️  Stopped by user")
                break
            elif key == ord('s'):
                filename = f"screenshot_{screenshot_count:03d}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"📸 Saved: {filename}")
                screenshot_count += 1
            elif key == ord('p'):
                paused = not paused
                print(f"⏸️  {'Paused' if paused else 'Resumed'}")
        
        cv2.destroyAllWindows()
        print("\n✅ Visualization complete!")


# Run the visualization
if __name__ == "__main__":
    visualizer = VisualScreenUnderstanding()
    visualizer.run(duration=300)  # Run for 5 minutes