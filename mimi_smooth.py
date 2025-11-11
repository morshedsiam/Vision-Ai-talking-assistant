# mimi_smooth.py - FIXED: Processes ALL changes!
from screen_understanding import ScreenUnderstanding
from vtuber_ai_ollama import VTuberAI
from automation_controller import AutomationController
from screen_capture import ScreenCapture
from voice_controller import VoiceController
import cv2
import numpy as np
import pyautogui
import time
import threading
from queue import Queue

class SmoothMimiAssistant:
    """Mimi - Notices and talks about EVERY change!"""
    
    def __init__(self, vtuber_name="Mimi", personality="cheerful", 
                 safety_mode=True, enable_voice=True, voice_rate=170):
        print("🌸 Initializing Complete Mimi...\n")
        
        screen_size = pyautogui.size()
        
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name=vtuber_name, personality=personality)
        self.controller = AutomationController(screen_size=screen_size, safety_mode=safety_mode)
        self.capture = ScreenCapture(target_fps=10, resize=(640, 640))
        
        self.enable_voice = enable_voice
        if enable_voice:
            self.voice = VoiceController(voice_id=None, rate=voice_rate, volume=0.9)
        
        self.vtuber_name = vtuber_name
        self.safety_mode = safety_mode
        
        # Threading
        self.ai_queue = Queue(maxsize=5)  # Allow up to 5 queued changes!
        self.ai_thread = None
        self.ai_busy = False
        self.ai_thread_running = True
        
        # State
        self.current_analysis = None
        self.current_decision = None
        self.current_frame = None
        self.latest_frame = None
        self.lock = threading.Lock()
        
        # Change detection
        self.last_objects_sig = ""
        self.last_scene = ""
        self.pending_changes = 0  # Track how many changes are waiting
        
        self.colors = {
            'happy': (0, 255, 0),
            'excited': (0, 255, 255),
            'thinking': (255, 165, 0),
            'confused': (0, 165, 255),
            'proud': (255, 0, 255),
        }
        
        print(f"✅ {vtuber_name} ready! (Complete mode)\n")
    
    def ai_worker(self):
        """Background AI worker - processes ALL queued changes!"""
        print("🤖 AI worker started (processes all changes)")
        
        while self.ai_thread_running:
            try:
                # Wait for task
                task = self.ai_queue.get(timeout=1)
                
                if task is None:
                    break
                
                user_task = task
                
                self.ai_busy = True
                self.pending_changes -= 1  # Mark as processing
                
                # Get fresh frame
                with self.lock:
                    fresh_frame = self.latest_frame
                
                if fresh_frame is None:
                    self.ai_busy = False
                    continue
                
                # Re-analyze current screen
                print(f"\n🔍 [AI] Analyzing current screen... (Queue: {self.ai_queue.qsize()})")
                fresh_analysis = self.understanding.analyze_screen(fresh_frame)
                
                print(f"📊 [AI] Scene: {fresh_analysis['caption'][:50]}...")
                print(f"📊 [AI] Objects: {fresh_analysis['object_count']}")
                
                # Generate response
                print(f"🧠 [AI] Generating response...")
                decision = self.vtuber.analyze_and_act(
                    screen_summary=fresh_analysis['summary'],
                    user_task=user_task
                )
                
                dialogue = decision.get('vtuber_speech', '')
                print(f"💬 [AI] \"{dialogue[:60]}...\"")
                
                # Update state
                with self.lock:
                    self.current_analysis = fresh_analysis
                    self.current_decision = decision
                
                # Speak
                if self.enable_voice and dialogue:
                    print(f"🔊 [AI] Speaking...")
                    self.voice.speak(dialogue, block=True)
                    print(f"✅ [AI] Done!")
                
                # Check if more changes are queued
                if self.ai_queue.qsize() > 0:
                    print(f"⏭️  [AI] {self.ai_queue.qsize()} more changes waiting, continuing...")
                
                self.ai_queue.task_done()
                
            except Exception as e:
                if "Empty" not in str(e):
                    print(f"❌ [AI] Error: {e}")
            finally:
                self.ai_busy = False
        
        print("🤖 AI worker stopped")
    
    def get_objects_signature(self, objects):
        """Get object signature"""
        sig_parts = []
        for obj in objects:
            name = obj['class_name']
            x = round(obj['center'][0] / 50) * 50
            y = round(obj['center'][1] / 50) * 50
            sig_parts.append(f"{name}@{x},{y}")
        return "|".join(sorted(sig_parts))
    
    def check_for_changes(self, analysis):
        """Check ONLY for object changes"""
        current_sig = self.get_objects_signature(analysis['objects'])
        
        if not self.last_objects_sig:
            self.last_objects_sig = current_sig
            return True
        
        # ONLY check objects, ignore scene!
        objects_changed = current_sig != self.last_objects_sig
        
        if objects_changed:
            print(f"\n🔄 OBJECTS CHANGED!")
            print(f"   Objects: {len(analysis['objects'])}")
            self.last_objects_sig = current_sig
            return True
        
        return False
    
    def create_info_panel(self, width, height, analysis, decision, is_speaking, ai_busy, queue_size):
        """Create info panel"""
        panel = np.zeros((height, width, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)
        
        y_pos = 30
        
        # Title
        cv2.putText(panel, f"{self.vtuber_name}'s Vision", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 255), 2)
        
        # Queue indicator
        if queue_size > 0:
            cv2.circle(panel, (width - 30, 25), 10, (255, 165, 0), -1)
            cv2.putText(panel, f"QUEUE:{queue_size}", (width - 120, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 165, 0), 1)
        elif is_speaking:
            cv2.circle(panel, (width - 30, 25), 10, (0, 255, 0), -1)
            cv2.putText(panel, "SPEAKING", (width - 110, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        elif ai_busy:
            cv2.circle(panel, (width - 30, 25), 10, (255, 165, 0), -1)
            cv2.putText(panel, "THINKING", (width - 110, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 165, 0), 1)
        else:
            cv2.circle(panel, (width - 30, 25), 10, (100, 100, 100), -1)
            cv2.putText(panel, "WATCHING", (width - 110, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        y_pos += 40
        
        # Current view
        cv2.putText(panel, "NOW:", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 2)
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
        
        # Objects
        cv2.putText(panel, f"Objects: {analysis['object_count']}", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
        y_pos += 25
        
        object_types = {}
        for obj in analysis['objects']:
            name = obj['class_name']
            object_types[name] = object_types.get(name, 0) + 1
        
        for obj_name, count in list(object_types.items())[:4]:
            text = f"  • {obj_name}"
            if count > 1:
                text += f" ({count})"
            cv2.putText(panel, text, (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
            y_pos += 20
        
        y_pos += 20
        
        # Last comment
        if decision:
            cv2.putText(panel, "LAST SAID:", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 100), 1)
            y_pos += 25
            
            box_top = y_pos - 10
            box_bottom = min(y_pos + 180, height - 10)
            cv2.rectangle(panel, (5, box_top), (width - 5, box_bottom), (60, 40, 80), -1)
            cv2.rectangle(panel, (5, box_top), (width - 5, box_bottom), (150, 100, 200), 2)
            
            y_pos += 10
            
            dialogue = decision.get('vtuber_speech', '...')
            words = dialogue.split()
            lines = []
            current_line = ""
            
            for word in words:
                test = current_line + " " + word if current_line else word
                if len(test) <= 28:
                    current_line = test
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            for i, line in enumerate(lines[:6]):
                cv2.putText(panel, line, (15, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
                y_pos += 22
        
        return panel
    
    def draw_detections(self, frame, analysis):
        """Draw detections"""
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
            label = f"{obj['class_name']}"
            cv2.putText(frame_display, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            center_x, center_y = obj['center']
            cv2.circle(frame_display, (center_x, center_y), 5, color, -1)
        
        return frame_display
    
    def run(self, task="describe what you see", duration=300):
        print("="*70)
        print(f"🎤 {self.vtuber_name.upper()} - COMPLETE MODE")
        print("="*70)
        print()
        print("💡 Mimi will notice and talk about EVERY change!")
        print("💡 She queues changes that happen while speaking!")
        print()
        print("Controls: Q-Quit | V-Voice | P-Pause")
        print()
        print("Starting in 3 seconds...")
        time.sleep(3)
        
        # Start AI worker
        self.ai_thread = threading.Thread(target=self.ai_worker, daemon=True)
        self.ai_thread.start()
        
        paused = False
        frame_count = 0
        generation_count = 0
        
        try:
            for frame in self.capture.capture_stream(duration=duration):
                frame_count += 1
                
                if not paused:
                    # Update latest frame
                    with self.lock:
                        self.latest_frame = frame.copy()
                    
                    # Detect changes
                    quick_analysis = self.understanding.analyze_screen(frame)
                    
                    with self.lock:
                        self.current_analysis = quick_analysis
                        self.current_frame = frame
                    
                    # Check for changes
                    if self.check_for_changes(quick_analysis):
                        # Try to queue (even if busy!)
                        try:
                            # Check if queue not full
                            if self.ai_queue.qsize() < 5:
                                self.ai_queue.put(task, block=False)
                                self.pending_changes += 1
                                generation_count += 1
                                
                                if self.ai_busy:
                                    print(f"   ⏳ AI busy, queued for later (position #{self.ai_queue.qsize()})")
                                else:
                                    print(f"   📤 Queued immediately")
                            else:
                                print(f"   ⚠️  Queue full, skipping this change")
                        except:
                            print(f"   ⚠️  Could not queue")
                
                # Display
                with self.lock:
                    display_analysis = self.current_analysis
                    display_decision = self.current_decision
                    display_frame = self.current_frame
                
                if display_analysis and display_frame is not None:
                    is_speaking = self.enable_voice and self.voice.is_busy()
                    queue_size = self.ai_queue.qsize()
                    
                    frame_with_detections = self.draw_detections(display_frame, display_analysis)
                    panel = self.create_info_panel(400, 640, display_analysis, 
                                                   display_decision, is_speaking, self.ai_busy, queue_size)
                    display = np.hstack([frame_with_detections, panel])
                    
                    # Status
                    status_bar = np.zeros((40, display.shape[1], 3), dtype=np.uint8)
                    status_bar[:] = (50, 50, 50)
                    
                    status = f"F:{frame_count} | Responses:{generation_count} | Queue:{queue_size} | "
                    status += "AI:" + ("BUSY" if self.ai_busy else "READY") + " | "
                    status += ("PAUSED" if paused else "LIVE")
                    
                    cv2.putText(status_bar, status, (10, 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                    
                    final_display = np.vstack([display, status_bar])
                    cv2.imshow(f"{self.vtuber_name}", final_display)
                
                # Controls
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n👋 Quitting...")
                    break
                
                elif key == ord('v'):
                    self.enable_voice = not self.enable_voice
                    if not self.enable_voice:
                        self.voice.stop()
                    print(f"\n🔊 Voice: {'ON' if self.enable_voice else 'OFF'}")
                
                elif key == ord('p'):
                    paused = not paused
                    print(f"\n{'⏸️  PAUSED' if paused else '▶️  RESUMED'}")
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped")
        finally:
            self.ai_thread_running = False
            self.ai_queue.put(None)
            if self.ai_thread:
                self.ai_thread.join(timeout=2)
            cv2.destroyAllWindows()
        
        print()
        print(f"📊 Total responses: {generation_count}")
        print(f"💬 {self.vtuber_name}: Bye!")


if __name__ == "__main__":
    mimi = SmoothMimiAssistant(
        vtuber_name="Mimi",
        personality="cheerful",
        enable_voice=True,
        voice_rate=170
    )
    
    mimi.run(
        task="describe what you see on screen accurately",
        duration=600
    )