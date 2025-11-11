# mimi_visual.py - COMPLETE WORKING VERSION
from screen_understanding import ScreenUnderstanding
from vtuber_ai_ollama import VTuberAI
from automation_controller import AutomationController
from screen_capture import ScreenCapture
import cv2
import numpy as np
import pyautogui
import time

class VisualMimiAssistant:
    """Visual VTuber Assistant - See what Mimi sees!"""
    
    def __init__(self, vtuber_name="Mimi", personality="cheerful", safety_mode=True):
        print("🌸 Initializing Visual Mimi Assistant...\n")
        
        screen_size = pyautogui.size()
        
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name=vtuber_name, personality=personality)
        self.controller = AutomationController(screen_size=screen_size, safety_mode=safety_mode)
        self.capture = ScreenCapture(target_fps=5, resize=(640, 640))
        
        self.vtuber_name = vtuber_name
        self.safety_mode = safety_mode
        
        self.colors = {
            'happy': (0, 255, 0),
            'excited': (0, 255, 255),
            'thinking': (255, 165, 0),
            'confused': (0, 165, 255),
            'proud': (255, 0, 255),
        }
        
        print(f"✅ {vtuber_name} is ready with visual display!\n")
    
    def create_info_panel(self, width, height, analysis, decision):
        """Create information panel"""
        panel = np.zeros((height, width, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)
        
        y_pos = 30
        line_height = 25
        
        # Title
        cv2.putText(panel, f"{self.vtuber_name}'s Vision", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 255), 2)
        y_pos += 40
        
        # Scene
        cv2.putText(panel, "SCENE:", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
        y_pos += 25
        
        # Wrap caption text
        caption = analysis['caption']
        if len(caption) > 35:
            line1 = caption[:35]
            line2 = caption[35:70]
            cv2.putText(panel, line1, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 20
            if line2:
                cv2.putText(panel, line2, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                y_pos += 20
        else:
            cv2.putText(panel, caption, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 25
        
        y_pos += 10
        
        # Stats
        cv2.putText(panel, f"Objects: {analysis['object_count']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
        y_pos += 25
        
        cv2.putText(panel, f"Clickable: {analysis['clickable_count']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
        y_pos += 30
        
        # Emotion
        emotion = decision.get('emotion', 'thinking')
        emotion_color = self.colors.get(emotion, (255, 255, 255))
        
        cv2.putText(panel, "EMOTION:", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
        cv2.circle(panel, (120, y_pos - 5), 8, emotion_color, -1)
        cv2.putText(panel, emotion, (135, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, emotion_color, 1)
        y_pos += 30
        
        # Action
        action_type = decision.get('action_type', 'wait').upper()
        action_color = (0, 255, 0) if action_type == 'CLICK' else (255, 200, 0)
        
        cv2.putText(panel, f"ACTION: {action_type}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, action_color, 2)
        y_pos += 30
        
        # Target
        if decision.get('target'):
            target = decision['target'][:30]  # Truncate
            cv2.putText(panel, f"Target: {target}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 25
        
        y_pos += 15
        
        # Dialogue box
        box_top = y_pos - 10
        box_bottom = min(y_pos + 180, height - 10)
        cv2.rectangle(panel, (5, box_top), (width - 5, box_bottom), (60, 40, 80), -1)
        cv2.rectangle(panel, (5, box_top), (width - 5, box_bottom), (150, 100, 200), 2)
        
        cv2.putText(panel, f"{self.vtuber_name} says:", (15, y_pos + 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 255), 2)
        y_pos += 35
        
        # Dialogue text (manual word wrap)
        dialogue = decision.get('vtuber_speech', '...')
        words = dialogue.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) <= 28:  # Characters per line
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:6]):  # Max 6 lines
            cv2.putText(panel, line, (15, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
            y_pos += 22
        
        return panel
    
    def draw_detections(self, frame, analysis):
        """Draw detection boxes"""
        frame_display = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
        
        colors = {
            0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255),
            3: (255, 255, 0), 4: (255, 0, 255), 5: (0, 255, 255),
            6: (128, 0, 128), 7: (255, 128, 0), 8: (0, 128, 255),
        }
        
        for obj in analysis['objects']:
            x1, y1, x2, y2 = obj['bbox']
            color = colors.get(obj['class_id'], (255, 255, 255))
            
            # Box
            cv2.rectangle(frame_display, (x1, y1), (x2, y2), color, 2)
            
            # Label
            label = f"{obj['class_name']} {obj['confidence']:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame_display, (x1, y1 - h - 10), (x1 + w, y1), color, -1)
            cv2.putText(frame_display, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Center
            center_x, center_y = obj['center']
            cv2.circle(frame_display, (center_x, center_y), 5, color, -1)
            
            # Clickable marker
            if obj in analysis['clickable_objects']:
                cv2.circle(frame_display, (center_x, center_y), 20, (0, 255, 0), 3)
                cv2.putText(frame_display, "CLICK", (center_x - 25, center_y - 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame_display
    
    def run(self, task="help me with the screen", duration=300):
        """Run visual assistant"""
        print("="*70)
        print(f"👀 {self.vtuber_name.upper()} - VISUAL MODE")
        print("="*70)
        print()
        print("Controls:")
        print("  Q - Quit")
        print("  E - Execute action")
        print("  P - Pause/Resume")
        print("  S - Save screenshot")
        print()
        print(f"Task: {task}")
        print(f"Duration: {duration}s\n")
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        paused = False
        screenshot_count = 0
        frame_count = 0
        action_count = 0
        current_decision = None
        current_analysis = None
        
        for frame in self.capture.capture_stream(duration=duration):
            frame_count += 1
            
            if not paused:
                current_analysis = self.understanding.analyze_screen(frame)
                current_decision = self.vtuber.analyze_and_act(
                    screen_summary=current_analysis['summary'],
                    user_task=task
                )
                
                if current_analysis['object_count'] > 0:
                    print(f"\n[{frame_count}] {current_analysis['object_count']} objects | {current_decision['vtuber_speech'][:40]}...")
            
            if current_analysis and current_decision:
                # Create display
                frame_with_detections = self.draw_detections(frame, current_analysis)
                panel = self.create_info_panel(400, 640, current_analysis, current_decision)
                display = np.hstack([frame_with_detections, panel])
                
                # Status bar
                status_bar = np.zeros((40, display.shape[1], 3), dtype=np.uint8)
                status_bar[:] = (50, 50, 50)
                
                status = f"Frame: {frame_count} | Actions: {action_count} | "
                status += "PAUSED" if paused else "RUNNING"
                cv2.putText(status_bar, status, (10, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.putText(status_bar, "Q:Quit E:Execute P:Pause S:Save", 
                           (display.shape[1] - 350, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
                # Combine
                final_display = np.vstack([display, status_bar])
                cv2.imshow(f"{self.vtuber_name}'s Vision", final_display)
            
            # Keyboard controls
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Quitting...")
                break
            elif key == ord('e'):
                if current_decision and current_decision['action_type'] in ['click', 'type']:
                    print(f"\n🎯 Executing: {current_decision['action_type']}")
                    if self.controller.execute_decision(current_decision):
                        action_count += 1
                        print(f"✅ Action #{action_count} complete!")
            elif key == ord('p'):
                paused = not paused
                print(f"\n{'⏸️  PAUSED' if paused else '▶️  RESUMED'}")
            elif key == ord('s'):
                filename = f"mimi_view_{screenshot_count:03d}.jpg"
                cv2.imwrite(filename, final_display)
                print(f"\n📸 Saved: {filename}")
                screenshot_count += 1
        
        cv2.destroyAllWindows()
        
        print()
        print("="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)
        print(f"Frames: {frame_count}")
        print(f"Actions: {action_count}")
        print(f"Screenshots: {screenshot_count}")
        print(f"\n💬 {self.vtuber_name}: Thanks for watching! Bye bye~! ♡")
        print("="*70)


# Run it!
if __name__ == "__main__":
    mimi = VisualMimiAssistant(
        vtuber_name="Mimi",
        personality="cheerful",
        safety_mode=True
    )
    
    mimi.run(
        task="look at the screen and identify interesting things",
        duration=300
    )