# mimi_sequential.py - NO OVERLAPPING! One thing at a time!
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
    """Mimi - Sequential processing (no overlaps!)"""
    
    def __init__(self, vtuber_name="Mimi", personality="cheerful", 
                 safety_mode=True, enable_voice=True, voice_rate=170):
        print("🌸 Initializing Sequential Mimi...\n")
        
        screen_size = pyautogui.size()
        
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name=vtuber_name, personality=personality)
        self.controller = AutomationController(screen_size=screen_size, safety_mode=safety_mode)
        self.capture = ScreenCapture(target_fps=2, resize=(640, 640))  # Slower FPS!
        
        self.enable_voice = enable_voice
        if enable_voice:
            self.voice = VoiceController(voice_id=None, rate=voice_rate, volume=0.9)
        
        self.vtuber_name = vtuber_name
        
        # State
        self.last_objects = []
        self.last_scene = ""
        self.is_busy = False  # IMPORTANT: Lock to prevent overlaps
        
        self.colors = {
            'happy': (0, 255, 0),
            'excited': (0, 255, 255),
            'thinking': (255, 165, 0),
            'confused': (0, 165, 255),
            'proud': (255, 0, 255),
        }
        
        print(f"✅ {vtuber_name} ready! (Sequential mode)\n")
    
    def objects_changed(self, current_objects, current_scene):
        """Check if objects changed"""
        # First run
        if not self.last_objects:
            self.last_objects = current_objects
            self.last_scene = current_scene
            return True
        
        # Compare
        current_names = sorted([obj['class_name'] for obj in current_objects])
        last_names = sorted([obj['class_name'] for obj in self.last_objects])
        
        objects_diff = current_names != last_names
        scene_diff = current_scene != self.last_scene
        
        if objects_diff or scene_diff:
            self.last_objects = current_objects
            self.last_scene = current_scene
            return True
        
        return False
    
    def create_simple_panel(self, width, height, info_text, status):
        """Simple info panel"""
        panel = np.zeros((height, width, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)
        
        y_pos = 30
        
        # Title
        cv2.putText(panel, f"{self.vtuber_name}'s Status", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 255), 2)
        y_pos += 50
        
        # Status
        status_color = (0, 255, 0) if status == "READY" else (255, 165, 0)
        cv2.putText(panel, f"Status: {status}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        y_pos += 50
        
        # Info text (word wrap)
        words = info_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test = current_line + " " + word if current_line else word
            if len(test) <= 35:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        for line in lines[:15]:  # Max 15 lines
            cv2.putText(panel, line, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            y_pos += 25
        
        return panel
    
    def draw_detections(self, frame, objects):
        """Draw detection boxes"""
        frame_display = cv2.cvtColor(frame.copy(), cv2.COLOR_RGB2BGR)
        
        colors = {
            0: (255, 0, 0), 1: (0, 255, 0), 2: (0, 0, 255),
            3: (255, 255, 0), 4: (255, 0, 255), 5: (0, 255, 255),
            6: (128, 0, 128), 7: (255, 128, 0), 8: (0, 128, 255),
        }
        
        for obj in objects:
            x1, y1, x2, y2 = obj['bbox']
            color = colors.get(obj['class_id'], (255, 255, 255))
            
            cv2.rectangle(frame_display, (x1, y1), (x2, y2), color, 2)
            
            label = f"{obj['class_name']}"
            cv2.putText(frame_display, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame_display
    
    def run(self, task="watch the screen", duration=300):
        print("="*70)
        print(f"🎤 {self.vtuber_name.upper()} - SEQUENTIAL MODE")
        print("="*70)
        print()
        print("💡 Processing happens ONE AT A TIME (no crashes!)")
        print()
        print("Controls:")
        print("  Q - Quit")
        print("  V - Toggle voice")
        print()
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        frame_count = 0
        generation_count = 0
        current_display_frame = None
        current_display_objects = []
        current_info_text = "Watching screen..."
        current_status = "READY"
        
        try:
            for frame in self.capture.capture_stream(duration=duration):
                frame_count += 1
                
                # Update display (always show something)
                if current_display_frame is not None:
                    frame_with_boxes = self.draw_detections(current_display_frame, current_display_objects)
                    panel = self.create_simple_panel(400, 640, current_info_text, current_status)
                    display = np.hstack([frame_with_boxes, panel])
                    
                    cv2.imshow(f"{self.vtuber_name}", display)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                elif key == ord('v'):
                    self.enable_voice = not self.enable_voice
                    print(f"\n🔊 Voice: {'ON' if self.enable_voice else 'OFF'}")
                
                # SEQUENTIAL PROCESSING (one at a time!)
                if not self.is_busy:
                    self.is_busy = True  # LOCK
                    current_status = "ANALYZING..."
                    
                    try:
                        # Step 1: Analyze screen
                        print(f"\n[{frame_count}] 🔍 Analyzing screen...")
                        analysis = self.understanding.analyze_screen(frame)
                        
                        current_objects = analysis['objects']
                        current_scene = analysis['caption']
                        
                        print(f"   Scene: {current_scene[:50]}")
                        print(f"   Objects: {len(current_objects)}")
                        
                        # Update display
                        current_display_frame = frame
                        current_display_objects = current_objects
                        
                        # Step 2: Check if changed
                        if self.objects_changed(current_objects, current_scene):
                            print(f"   🆕 CHANGE DETECTED!")
                            current_status = "THINKING..."
                            
                            # Step 3: Generate response (WAIT for it to finish!)
                            print(f"   🧠 Generating response...")
                            decision = self.vtuber.analyze_and_act(
                                screen_summary=analysis['summary'],
                                user_task=task
                            )
                            generation_count += 1
                            
                            dialogue = decision.get('vtuber_speech', '')
                            current_info_text = dialogue
                            
                            print(f"   💬 {dialogue}")
                            
                            # Step 4: Speak (WAIT for it to finish!)
                            if self.enable_voice and dialogue:
                                current_status = "SPEAKING..."
                                print(f"   🔊 Speaking...")
                                
                                # BLOCKING SPEECH (waits until done)
                                self.voice.speak(dialogue, block=True)
                                
                                print(f"   ✅ Speech complete")
                        else:
                            print(f"   ⏸️  No change detected")
                        
                        current_status = "READY"
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        current_status = "ERROR"
                    
                    finally:
                        self.is_busy = False  # UNLOCK
                        print(f"   ✅ Ready for next frame\n")
                
                # Small delay
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        cv2.destroyAllWindows()
        
        print()
        print("="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Frames: {frame_count}")
        print(f"Generations: {generation_count}")
        print(f"\n💬 {self.vtuber_name}: Bye bye~! ♡")


if __name__ == "__main__":
    mimi = SpeakingMimiAssistant(
        vtuber_name="Mimi",
        personality="cheerful",
        enable_voice=True,
        voice_rate=180
    )
    
    mimi.run(
        task="watch the screen and tell me when something appears or disappears",
        duration=600  # 10 minutes
    )