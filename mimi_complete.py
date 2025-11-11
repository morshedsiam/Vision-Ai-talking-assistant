# mimi_complete.py - Full natural conversational Mimi with screen awareness!
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
import subprocess
import webbrowser
import random

class CompleteMimi:
    """
    Natural AI companion who:
    - Automatically watches screen and reacts to changes
    - Initiates conversations and asks questions
    - Talks about random topics
    - Executes commands (open YouTube, search, click, type)
    - Has personality and memory
    """
    
    def __init__(self, vtuber_name="Mimi", personality="cheerful", enable_voice=True):
        print("🌸 Initializing Complete Mimi System...\n")
        
        screen_size = pyautogui.size()
        
        # Core components
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name=vtuber_name, personality=personality)
        self.controller = AutomationController(screen_size=screen_size, safety_mode=False)
        self.capture = ScreenCapture(target_fps=10, resize=(640, 640))
        
        self.enable_voice = enable_voice
        if enable_voice:
            self.voice = VoiceController(voice_id=None, rate=170, volume=0.9)
        
        self.vtuber_name = vtuber_name
        
        # Conversation system
        self.conversation_history = []
        self.topics_discussed = []
        
        # Screen monitoring
        self.ai_queue = Queue(maxsize=20)
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
        
        # Conversation timing
        self.last_speech_time = time.time()
        self.last_question_time = time.time()
        self.last_random_comment_time = time.time()
        
        # Random topics Mimi can talk about
        self.random_topics = [
            "Master, what are you working on? I'm curious! (◕‿◕✿)",
            "Nya~! Do you want to take a break? I can search for some funny videos if you want!",
            "Ehehe~ I'm watching everything you do! Not in a creepy way though... >///<",
            "Hey Master! How are you feeling today? ♡",
            "I've been thinking... do you have any fun plans later? ✨",
            "Ooh! Should we listen to some music? I can open Spotify for you~",
            "Master-san, you've been staring at the screen for a while! Want me to find something fun?",
            "Random question: What's your favorite color? Mine is pink! 🌸",
            "Are you hungry? Maybe I should remind you to eat~ You need to stay healthy! ♡",
            "I wonder what the weather is like outside... Should we check?",
        ]
        
        self.colors = {
            'happy': (0, 255, 0),
            'excited': (0, 255, 255),
            'thinking': (255, 165, 0),
            'confused': (0, 165, 255),
            'proud': (255, 0, 255),
        }
        
        print(f"✅ {vtuber_name} is fully ready!\n")
    
    # ==================== ACTION METHODS ====================
    
    def open_youtube(self):
        """Open YouTube"""
        print("🎬 Opening YouTube...")
        webbrowser.open('https://www.youtube.com')
        time.sleep(2)
        return True
    
    def search_youtube(self, query):
        """Search YouTube"""
        print(f"🔍 Searching YouTube: {query}")
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        time.sleep(2)
        return True
    
    def open_application(self, app_name):
        """Open application"""
        print(f"📱 Opening {app_name}...")
        
        apps = {
            'chrome': 'chrome.exe',
            'browser': 'chrome.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'explorer': 'explorer.exe',
            'discord': 'discord.exe',
            'spotify': 'spotify.exe',
        }
        
        for key, exe in apps.items():
            if key in app_name.lower():
                try:
                    subprocess.Popen(exe)
                    return True
                except:
                    pass
        
        return False
    
    def click_detected_object(self, object_name):
        """Click on detected object"""
        with self.lock:
            if not self.current_analysis:
                return False
            
            for obj in self.current_analysis['objects']:
                if object_name.lower() in obj['class_name'].lower():
                    x, y = self.controller.scale_coordinates(
                        obj['center'][0], obj['center'][1]
                    )
                    self.controller.click_at(x, y)
                    return True
        return False
    
    # ==================== CONVERSATION METHODS ====================
    
    def should_make_random_comment(self):
        """Decide if Mimi should say something random"""
        current_time = time.time()
        
        # Random comment every 45-90 seconds
        time_since_last = current_time - self.last_random_comment_time
        random_interval = random.randint(45, 90)
        
        if time_since_last > random_interval:
            # 40% chance to actually comment
            if random.random() < 0.4:
                self.last_random_comment_time = current_time
                return True
        
        return False
    
    def should_ask_screen_question(self, analysis):
        """Ask question about what's on screen"""
        current_time = time.time()
        
        # Ask about screen every 60 seconds
        if current_time - self.last_question_time < 60:
            return False
        
        # Only if something interesting on screen
        if analysis['object_count'] >= 3:
            self.last_question_time = current_time
            return True
        
        return False
    
    def generate_random_comment(self):
        """Generate random conversational comment"""
        return random.choice(self.random_topics)
    
    def generate_screen_question(self, analysis):
        """Ask question about screen"""
        prompts = [
            f"I see {analysis['caption']}. What are you looking for, Master?",
            f"Ooh! I notice {analysis['object_count']} things on screen. What are you doing? ♡",
            f"Master, I see you're looking at something interesting~ Want me to help with anything?",
            f"Nya~! I can see {', '.join(set([o['class_name'] for o in analysis['objects'][:3]]))}. Need help clicking something?",
        ]
        return random.choice(prompts)
    
    def generate_screen_aware_response(self, screen_summary):
        """Generate natural response to screen changes"""
        
        prompt = f"""{self.vtuber.system_prompt}

CURRENT SCREEN:
{screen_summary}

RECENT CONVERSATION:
{chr(10).join(self.conversation_history[-3:]) if self.conversation_history else "No recent conversation"}

React to what you see on screen naturally! You can:
- Comment on what appeared/changed
- Offer to help (search YouTube, open apps, click things)
- Ask what the user is doing
- Make a casual observation
- Express curiosity

Keep it SHORT (1-2 sentences), NATURAL, and IN CHARACTER!

{self.vtuber_name}:"""
        
        response = self.vtuber._generate(prompt, max_tokens=100).strip()
        
        # Clean up
        if ':' in response:
            response = response.split(':', 1)[1].strip()
        
        return response
    
    def parse_user_command(self, text):
        """
        Parse natural language for commands
        Returns: (command_type, parameters)
        """
        text_lower = text.lower()
        
        # Open YouTube
        if 'youtube' in text_lower and ('open' in text_lower or 'go' in text_lower):
            return ('open_youtube', None)
        
        # Search YouTube
        if 'youtube' in text_lower and ('search' in text_lower or 'find' in text_lower):
            # Extract query
            keywords = ['search youtube for', 'find on youtube', 'search for', 'find']
            for kw in keywords:
                if kw in text_lower:
                    query = text.split(kw, 1)[1].strip()
                    return ('search_youtube', query)
        
        # Open app
        if 'open' in text_lower:
            words = text.split()
            if 'open' in words:
                idx = words.index('open')
                if idx + 1 < len(words):
                    return ('open_app', words[idx + 1])
        
        # Click
        if 'click' in text_lower:
            if 'click on' in text_lower:
                obj = text.split('click on', 1)[1].strip()
            elif 'click the' in text_lower:
                obj = text.split('click the', 1)[1].strip()
            else:
                obj = text.split('click', 1)[1].strip()
            return ('click', obj)
        
        # Type
        if 'type' in text_lower:
            text_to_type = text.split('type', 1)[1].strip()
            return ('type', text_to_type)
        
        return (None, None)
    
    # ==================== AI WORKER ====================
    
    def ai_worker(self):
        """Background AI - processes screen changes and random thoughts"""
        print("🤖 AI worker started")
        
        while self.ai_thread_running:
            try:
                # Check for random comments first
                if self.should_make_random_comment() and self.ai_queue.empty():
                    comment = self.generate_random_comment()
                    print(f"\n💭 {self.vtuber_name} (random thought): {comment}")
                    
                    if self.enable_voice:
                        while self.voice.is_busy():
                            time.sleep(0.1)
                        self.voice.speak(comment, block=True)
                    
                    self.conversation_history.append(f"{self.vtuber_name}: {comment}")
                    continue
                
                # Process screen changes
                task = self.ai_queue.get(timeout=1)
                
                if task is None:
                    break
                
                user_task = task
                self.ai_busy = True
                
                # Get fresh analysis
                with self.lock:
                    fresh_frame = self.latest_frame
                
                if fresh_frame is None:
                    self.ai_busy = False
                    continue
                
                print(f"\n🔍 [AI] Analyzing screen...")
                fresh_analysis = self.understanding.analyze_screen(fresh_frame)
                
                # Check if should ask question about screen
                if self.should_ask_screen_question(fresh_analysis):
                    question = self.generate_screen_question(fresh_analysis)
                    
                    with self.lock:
                        self.current_analysis = fresh_analysis
                    
                    print(f"❓ {self.vtuber_name}: {question}")
                    
                    if self.enable_voice:
                        while self.voice.is_busy():
                            time.sleep(0.1)
                        self.voice.speak(question, block=True)
                    
                    self.conversation_history.append(f"{self.vtuber_name}: {question}")
                    
                else:
                    # Normal screen reaction
                    response = self.generate_screen_aware_response(fresh_analysis['summary'])
                    
                    with self.lock:
                        self.current_analysis = fresh_analysis
                    
                    print(f"💬 {self.vtuber_name}: {response}")
                    
                    if self.enable_voice:
                        while self.voice.is_busy():
                            time.sleep(0.1)
                        self.voice.speak(response, block=True)
                    
                    self.conversation_history.append(f"{self.vtuber_name}: {response}")
                
                self.ai_queue.task_done()
                
            except Exception as e:
                if "Empty" not in str(e):
                    print(f"❌ [AI] Error: {e}")
            finally:
                self.ai_busy = False
        
        print("🤖 AI worker stopped")
    
    # ==================== CHANGE DETECTION ====================
    
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
        """Check if screen changed"""
        current_sig = self.get_objects_signature(analysis['objects'])
        current_scene = analysis['caption']
        
        if not self.last_objects_sig:
            self.last_objects_sig = current_sig
            self.last_scene = current_scene
            return True
        
        objects_changed = current_sig != self.last_objects_sig
        scene_changed = current_scene != self.last_scene
        
        if objects_changed or scene_changed:
            print(f"\n🔄 CHANGE DETECTED!")
            self.last_objects_sig = current_sig
            self.last_scene = current_scene
            return True
        
        return False
    
    # ==================== USER INPUT HANDLER ====================
    
    def handle_user_input(self):
        """Thread to handle user text input"""
        print("\n💬 You can type to Mimi anytime!")
        print("Commands: 'open youtube', 'search youtube for X', 'click X', etc.")
        print("Or just chat naturally!\n")
        
        while self.ai_thread_running:
            try:
                user_input = input()
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    print(f"\n{self.vtuber_name}: Bye bye, Master! ♡")
                    self.ai_thread_running = False
                    break
                
                print(f"\nYou: {user_input}")
                
                # Parse command
                cmd_type, cmd_param = self.parse_user_command(user_input)
                
                response = None
                
                if cmd_type == 'open_youtube':
                    self.open_youtube()
                    response = "Opening YouTube for you, Master! ✨"
                
                elif cmd_type == 'search_youtube':
                    self.search_youtube(cmd_param)
                    response = f"Searching YouTube for '{cmd_param}'! Let me find that~ ♡"
                
                elif cmd_type == 'open_app':
                    success = self.open_application(cmd_param)
                    response = f"Opening {cmd_param}! Nya~" if success else f"Hmm, I don't know how to open {cmd_param}... >///<"
                
                elif cmd_type == 'click':
                    success = self.click_detected_object(cmd_param)
                    response = f"Clicking on {cmd_param}! Done~ ♡" if success else f"I can't find {cmd_param} on screen... Sorry! >///<"
                
                elif cmd_type == 'type':
                    pyautogui.write(cmd_param, interval=0.05)
                    response = f"Typing that for you! ✨"
                
                else:
                    # Natural conversation
                    with self.lock:
                        analysis = self.current_analysis
                    
                    if analysis:
                        screen_context = f"Screen shows: {analysis['caption']}. {analysis['object_count']} objects."
                    else:
                        screen_context = "Screen information not available."
                    
                    prompt = f"""{self.vtuber.system_prompt}

SCREEN: {screen_context}

CONVERSATION:
{chr(10).join(self.conversation_history[-5:])}
User: {user_input}

Respond naturally as {self.vtuber_name}! Short and sweet!

{self.vtuber_name}:"""
                    
                    response = self.vtuber._generate(prompt, max_tokens=100).strip()
                    if ':' in response:
                        response = response.split(':', 1)[1].strip()
                
                # Respond
                if response:
                    print(f"{self.vtuber_name}: {response}\n")
                    
                    if self.enable_voice:
                        while self.voice.is_busy():
                            time.sleep(0.1)
                        self.voice.speak(response, block=False)
                    
                    self.conversation_history.append(f"User: {user_input}")
                    self.conversation_history.append(f"{self.vtuber_name}: {response}")
                
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    # ==================== MAIN RUN ====================
    
    def run(self, duration=99999):
        """Run complete Mimi system"""
        print("="*70)
        print(f"🌸 {self.vtuber_name.upper()} - COMPLETE NATURAL ASSISTANT")
        print("="*70)
        print()
        print("✨ Mimi will:")
        print("  • Watch your screen automatically")
        print("  • Comment on changes")
        print("  • Ask you questions")
        print("  • Chat about random topics")
        print("  • Execute your commands")
        print()
        print("Type 'quit' to exit")
        print("="*70)
        print()
        
        # Start AI worker
        self.ai_thread = threading.Thread(target=self.ai_worker, daemon=True)
        self.ai_thread.start()
        
        # Start user input handler
        input_thread = threading.Thread(target=self.handle_user_input, daemon=True)
        input_thread.start()
        
        # Initial greeting
        greeting = f"Hi Master! I'm {self.vtuber_name}! I'm watching your screen and ready to chat! What would you like to do? ♡"
        print(f"{self.vtuber_name}: {greeting}\n")
        if self.enable_voice:
            self.voice.speak(greeting, block=False)
        
        frame_count = 0
        
        try:
            for frame in self.capture.capture_stream(duration=duration):
                if not self.ai_thread_running:
                    break
                
                frame_count += 1
                
                # Update latest frame
                with self.lock:
                    self.latest_frame = frame.copy()
                
                # Quick analysis
                analysis = self.understanding.analyze_screen(frame)
                
                with self.lock:
                    self.current_analysis = analysis
                
                # Check for changes
                if self.check_for_changes(analysis):
                    if self.ai_queue.qsize() < 20:
                        self.ai_queue.put("describe what changed")
        
        except KeyboardInterrupt:
            print("\n⏹️  Stopped")
        finally:
            self.ai_thread_running = False
            self.ai_queue.put(None)
            if self.ai_thread:
                self.ai_thread.join(timeout=2)
        
        print(f"\n💬 {self.vtuber_name}: Thanks for spending time with me! Bye bye~! ♡")


if __name__ == "__main__":
    mimi = CompleteMimi(
        vtuber_name="Mimi",
        personality="cheerful",
        enable_voice=True
    )
    
    mimi.run()