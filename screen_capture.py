# screen_capture.py
import mss
import numpy as np
from PIL import Image
import time
import cv2

class ScreenCapture:
    def __init__(self, target_fps=10, resize=(640, 640)):
        self.sct = mss.mss()
        self.target_fps = target_fps
        self.frame_delay = 1.0 / target_fps
        self.resize = resize
        
    def get_primary_monitor(self):
        """Get the primary monitor dimensions"""
        return self.sct.monitors[1]  # Monitor 1 is primary
    
    def capture_frame(self):
        """Capture a single frame and return as numpy array (640x640)"""
        monitor = self.get_primary_monitor()
        
        # Capture screenshot
        screenshot = self.sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        
        # Resize to 640x640
        img_resized = img.resize(self.resize, Image.Resampling.LANCZOS)
        
        # Convert to numpy array for processing
        frame = np.array(img_resized)
        
        return frame
    
    def capture_stream(self, duration=10):
        """Capture frames for a specified duration (in seconds)"""
        print(f"📹 Starting screen capture at {self.target_fps} FPS")
        print(f"🖥️  Monitor: {self.get_primary_monitor()}")
        print(f"📐 Resize: {self.resize}")
        print(f"⏱️  Duration: {duration} seconds")
        print("\nPress Ctrl+C to stop early\n")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < duration:
                frame_start = time.time()
                
                # Capture frame
                frame = self.capture_frame()
                
                # Yield frame for processing
                yield frame
                
                frame_count += 1
                
                # Calculate FPS
                elapsed = time.time() - start_time
                current_fps = frame_count / elapsed if elapsed > 0 else 0
                
                # Print stats every 10 frames
                if frame_count % 10 == 0:
                    print(f"Frame {frame_count} | FPS: {current_fps:.2f} | Shape: {frame.shape}")
                
                # Maintain target FPS
                frame_time = time.time() - frame_start
                sleep_time = max(0, self.frame_delay - frame_time)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n⏹️  Capture stopped by user")
        
        print(f"\n✅ Captured {frame_count} frames in {elapsed:.2f} seconds")
        print(f"📊 Average FPS: {current_fps:.2f}")


# Test the screen capture
if __name__ == "__main__":
    # Initialize capture
    capture = ScreenCapture(target_fps=10, resize=(640, 640))
    
    # Capture for 10 seconds
    for frame in capture.capture_stream(duration=10):
        # Frame is in memory as numpy array (640, 640, 3)
        # You can process it here
        pass
    
    print("\n🎉 Screen capture test complete!")