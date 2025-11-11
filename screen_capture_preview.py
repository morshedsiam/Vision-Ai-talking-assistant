# screen_capture_preview.py
import cv2
from screen_capture import ScreenCapture

capture = ScreenCapture(target_fps=10, resize=(640, 640))

print("Showing preview window. Press 'q' to quit.")

for frame in capture.capture_stream(duration=60):
    # Convert RGB to BGR for OpenCV
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Show preview
    cv2.imshow("Screen Capture Preview", frame_bgr)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("Preview closed")