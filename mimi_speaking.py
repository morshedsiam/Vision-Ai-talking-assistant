# mimi_speaking.py - SMART OBJECT CHANGE DETECTION
from screen_understanding import ScreenUnderstanding
from vtuber_ai_ollama import VTuberAI
from automation_controller import AutomationController
from screen_capture import ScreenCapture
from voice_controller import VoiceController
import cv2
import numpy as np
import pyautogui
import time

class SpeakingMimiAssistant:
    """Mimi - Only generates & speaks when OBJECTS actually change!"""
    
    def __init__(self, vtuber_name="Mimi", personality="cheerful", 
                 safety_mode=True, enable_voice=True, voice_rate=170):
        print("🌸 Initializing Smart Speaking Mimi...\n")
        
        screen_size = pyautogui.size()
        
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name=vtuber_name, personality=personality)
        self.controller = AutomationController(screen_size=screen_size, safety_mode=safety_mode)
        self.capture = ScreenCapture(target_fps=5, resize=(640, 640))
        
        self.enable_voice = enable_voice
        if enable_voice:
            self.voice = VoiceController(voice_id=None, rate=voice_rate, volume=0.9)
        
        self.vtuber_name = vtuber_name
        self.safety_mode = safety_mode
        
        # Track detected objects (this is the key!)
        self.last_detected_objects = None # Set of object class names
        self.last_scene = None
        self.last_decision = None
        self.last_analysis = None
        
        self.colors = {
            'happy': (0, 255, 0),
            'excited': (0, 255, 255),
            'thinking': (255, 165, 0),
            'confused': (0, 165, 255),
            'proud': (255, 0, 255),
        }
        
        print(f"✅ {vtuber_name} ready!")
        print(f"💡 Will generate text ONLY when objects change!\n")
    
    def get_object_signature(self, analysis):
        """
        Create a unique signature of detected objects
        Returns set of (class_name, approximate_position) tuples
        """
        signature = set()
        
        for obj in analysis['objects']:
            # Use class name and rough position
            class_name = obj['class_name']
            # Round position to nearest 100 pixels to avoid tiny movements
            x = round(obj['center'][0] / 100) * 100
            y = round(obj['center'][1] / 100) * 100
            
            signature.add((class_name, x, y))
        
        return signature
    
    def objects_changed(self, current_analysis):
        """
        Check if objects have meaningfully changed
        Returns True if:
        - New objects appeared
        - Objects disappeared
        - Scene changed significantly
        """
        current_objects = self.get_object_signature(current_analysis)
        current_scene = current_analysis['caption']
        
        # First run - always trigger
        if self.last_detected_objects is None:
            self.last_detected_objects = current_objects
            self.last_scene = current_scene
            return True
        
        # Check if objects changed
        objects_added = current_objects - self.last_detected_objects
        objects_removed = self.last_detected_objects - current_objects
        
        # Check if scene changed significantly
        scene_changed = current_scene != self.last_scene
        
        # Trigger if:
        # 1. New objects appeared
        # 2. Objects disappeared
        # 3. Scene description changed
        changed = len(objects_added) > 0 or len(objects_removed) > 0 or scene_changed
        
        if changed:
            # Update state
            self.last_detected_objects = current_objects
            self.last_scene = current_scene
            
            # Print what changed (for debugging)
            if objects_added:
                print(f"🆕 New objects: {[obj[0] for obj in objects_added]}")
            if objects_removed:
                print(f"❌ Removed objects: {[obj[0] for obj in objects_removed]}")
            if scene_changed:
                print(f"🎬 Scene changed: {current_scene}")
        
        return changed
    
    def create_info_panel(self, width, height, analysis, decision, is_speaking=False):
        """Create info panel"""
        panel = np.zeros((height, width, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)
        
        y_pos = 30
        
        # Title
        cv2.putText(panel, f"{self.vtuber_name}'s Vision", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 255), 2)
        
        # Speaking indicator
        if is_speaking:
            cv2.circle(panel, (width - 30, 25), 10, (0, 255, 0), -1)
            cv2.putText(panel, "SPEAKING", (width - 110, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        y_pos += 40
        
        # Scene
        cv2.putText(panel, "SCENE:", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
        y_pos += 25
        
        caption = analysis['caption']
        if len(caption) > 35:
            cv2.putText(panel, caption[:35], (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 20
            cv2.putText(panel, caption[35:70], (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 20
        else:
            cv2.putText(panel, caption, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 25
        
        y_pos += 10
        
        # Detected objects list
        cv2.putText(panel, f"DETECTED ({analysis['object_count']}):", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
        y_pos += 25
        
        # List unique object types
        object_types = {}
        for obj in analysis['objects']:
            name = obj['class_name']
            object_types[name] = object_types.get(name, 0) + 1
        
        for obj_name, count in list(object_types.items())[:5]:  # Max 5 types
            text = f"  {obj_name}"
            if count > 1:
                text += f" x{count}"
            cv2.putText(panel, text, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 20
        
        y_pos += 10
        
        # Clickable count
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
        y_pos += 25
        
        if decision.get('target'):
            cv2.putText(panel, f"Target: {decision['target'][:30]}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_pos += 20
        
        y_pos += 15
        
        # Dialogue box
        box_top = y_pos - 10
        box_bottom = min(y_pos + 150, height - 10)
        cv2.rectangle(panel, (5, box_top), (width - 5, box_bottom), (60, 40, 80), -1)
        cv2.rectangle(panel, (5, box_top), (width - 5, box_bottom), (150, 100, 200), 2)
        
        cv2.putText(panel, f"{self.vtuber_name} says:", (15, y_pos + 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 255), 2)
        y_pos += 35
        
        # Dialogue
        dialogue = decision.get('vtuber_speech', '...')
        words = dialogue.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) <= 28:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:5]):
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
            
            cv2.rectangle(frame_display, (x1, y1), (x2, y2), color, 2)
            
            label = f"{obj['class_name']} {obj['confidence']:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame_display, (x1, y1 - h - 10), (x1 + w, y1), color, -1)
            cv2.putText(frame_display, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            center_x, center_y = obj['center']
            cv2.circle(frame_display, (center_x, center_y), 5, color, -1)
            
            if obj in analysis['clickable_objects']:
                cv2.circle(frame_display, (center_x, center_y), 20, (0, 255, 0), 3)
                cv2.putText(frame_display, "CLICK", (center_x - 25, center_y - 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame_display
    
    def run(self, task="help me with the screen", duration=300, check_interval=2.0):
        """
        Run smart speaking assistant
        
        Args:
            task: What Mimi should do
            duration: How long to run
            check_interval: How often to check for changes (seconds)
        """
        print("="*70)
        print(f"🎤 {self.vtuber_name.upper()} - SMART OBJECT DETECTION")
        print("="*70)
        print()
        print("Controls:")
        print("  Q - Quit")
        print("  E - Execute action")
        print("  P - Pause/Resume")
        print("  S - Screenshot")
        print("  V - Toggle voice")
        print()
        print(f"Task: {task}")
        print(f"Check interval: {check_interval}s")
        print()
        print("💡 Generates text ONLY when objects change!")
        print("💡 Open/close windows to trigger speech!")
        print()
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        paused = False
        screenshot_count = 0
        frame_count = 0
        action_count = 0
        generation_count = 0
        last_check_time = 0
        
        for frame in self.capture.capture_stream(duration=duration):
            frame_count += 1
            current_time = time.time()
            
            # Check for changes periodically
            if not paused and (current_time - last_check_time >= check_interval):
                # Analyze current screen
                current_analysis = self.understanding.analyze_screen(frame)
                
                # Check if objects changed
                if self.objects_changed(current_analysis):
                    print(f"\n🔄 OBJECTS CHANGED! Generating response...")
                    
                    # Generate NEW response
                    current_decision = self.vtuber.analyze_and_act(
                        screen_summary=current_analysis['summary'],
                        user_task=task
                    )
                    
                    generation_count += 1
                    dialogue = current_decision.get('vtuber_speech', '')
                    
                    print(f"💬 Mimi: {dialogue}")
                    
                    # Speak it
                    if self.enable_voice:
                        # Wait for previous speech to finish
                        while self.voice.is_busy():
                            time.sleep(0.1)
                        self.voice.speak(dialogue, block=False)
                    
                    # Save this decision
                    self.last_decision = current_decision
                    self.last_analysis = current_analysis
                else:
                    # No change - keep showing old decision
                    if frame_count % 30 == 0:
                        print(".", end="", flush=True)
                
                last_check_time = current_time
            
            # Always display (use last decision if no new one)
            if self.last_analysis and self.last_decision:
                is_speaking = self.enable_voice and self.voice.is_busy()
                
                frame_with_detections = self.draw_detections(frame, self.last_analysis)
                panel = self.create_info_panel(400, 640, self.last_analysis, self.last_decision, is_speaking)
                display = np.hstack([frame_with_detections, panel])
                
                # Status bar
                status_bar = np.zeros((40, display.shape[1], 3), dtype=np.uint8)
                status_bar[:] = (50, 50, 50)
                
                status = f"Frame: {frame_count} | Generations: {generation_count} | Actions: {action_count} | "
                status += "Voice: " + ("ON" if self.enable_voice else "OFF") + " | "
                status += ("PAUSED" if paused else "RUNNING")
                
                cv2.putText(status_bar, status, (10, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                
                cv2.putText(status_bar, "Q:Quit E:Exec P:Pause V:Voice S:Save", 
                           (display.shape[1] - 380, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
                
                final_display = np.vstack([display, status_bar])
                cv2.imshow(f"{self.vtuber_name}'s Vision", final_display)
            
            # Controls
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n\n👋 Quitting...")
                if self.enable_voice:
                    self.voice.stop()
                break
            
            elif key == ord('e'):
                if self.last_decision and self.last_decision['action_type'] in ['click', 'type']:
                    print(f"\n🎯 Executing: {self.last_decision['action_type']}")
                    if self.controller.execute_decision(self.last_decision):
                        action_count += 1
                        print(f"✅ Action #{action_count}")
            
            elif key == ord('p'):
                paused = not paused
                print(f"\n{'⏸️  PAUSED' if paused else '▶️  RESUMED'}")
            
            elif key == ord('v'):
                self.enable_voice = not self.enable_voice
                if not self.enable_voice and hasattr(self, 'voice'):
                    self.voice.stop()
                print(f"\n🔊 Voice: {'ON' if self.enable_voice else 'OFF'}")
            
            elif key == ord('s'):
                if self.last_analysis and self.last_decision:
                    filename = f"mimi_{screenshot_count:03d}.jpg"
                    cv2.imwrite(filename, final_display)
                    print(f"\n📸 Saved: {filename}")
                    screenshot_count += 1
        
        cv2.destroyAllWindows()
        
        print()
        print("="*70)
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"Frames processed: {frame_count}")
        print(f"Text generations: {generation_count}")
        print(f"Actions executed: {action_count}")
        print(f"Screenshots: {screenshot_count}")
        print()
        print(f"💬 {self.vtuber_name}: Bye bye~! ♡")
        print("="*70)


if __name__ == "__main__":
    mimi = SpeakingMimiAssistant(
        vtuber_name="Mimi",
        personality="cheerful",
        safety_mode=True,
        enable_voice=True,
        voice_rate=170
    )
    
    mimi.run(
        task="watch the screen and react when objects appear or disappear",
        duration=600,        # 10 minutes
        check_interval=2.0   # Check every 2 seconds
    )