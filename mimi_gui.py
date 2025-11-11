# mimi_gui.py - Beautiful chat GUI for Mimi!
import tkinter as tk
from tkinter import scrolledtext, ttk
from screen_understanding import ScreenUnderstanding
from vtuber_ai_ollama import VTuberAI
from automation_controller import AutomationController
from screen_capture import ScreenCapture
from voice_controller import VoiceController
import pyautogui
import time
import threading
from queue import Queue
import subprocess
import webbrowser
import random

class MimiChatGUI:
    """Beautiful chat interface for Mimi"""
    
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("💬 Chat with Mimi")
        self.root.geometry("600x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize Mimi's brain
        print("🌸 Initializing Mimi...")
        screen_size = pyautogui.size()
        
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name="Mimi", personality="cheerful")
        self.controller = AutomationController(screen_size=screen_size, safety_mode=False)
        self.capture = ScreenCapture(target_fps=10, resize=(640, 640))
        self.voice = VoiceController(voice_id=None, rate=170, volume=0.9)
        
        self.vtuber_name = "Mimi"
        self.enable_voice = True
        
        # State
        self.current_analysis = None
        self.latest_frame = None
        self.conversation_history = []
        self.lock = threading.Lock()
        
        # Screen monitoring
        self.ai_queue = Queue(maxsize=20)
        self.ai_busy = False
        self.ai_thread_running = True
        
        # Change detection
        self.last_objects_sig = ""
        self.last_scene = ""
        self.last_random_comment_time = time.time()
        self.last_question_time = time.time()
        
        # Random topics
        self.random_topics = [
            "Master, what are you working on? I'm curious! (◕‿◕✿)",
            "Nya~! Want to take a break? I can search for some funny videos!",
            "How are you feeling today? ♡",
            "Should we listen to some music? I can open Spotify for you~",
            "You've been staring at the screen for a while! Need anything? ✨",
        ]
        
        self.create_gui()
        self.start_background_threads()
        
        # Initial greeting
        self.add_message("Mimi", "Hi Master! I'm Mimi! ✨ I'm watching your screen and ready to chat! How can I help you today? ♡")
        self.speak("Hi Master! I'm Mimi! I'm watching your screen and ready to chat! How can I help you today?")
        
        print("✅ Mimi GUI ready!")
    
    def create_gui(self):
        """Create the chat interface"""
        
        # Title frame
        title_frame = tk.Frame(self.root, bg='#ff69b4', height=60)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        
        title_label = tk.Label(
            title_frame, 
            text="💖 Mimi - Your AI VTuber Assistant 💖",
            font=('Arial', 16, 'bold'),
            bg='#ff69b4',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Status frame
        self.status_frame = tk.Frame(self.root, bg='#e0e0e0', height=30)
        self.status_frame.pack(fill=tk.X, side=tk.TOP)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="👁️ Watching screen... | 🎤 Voice: ON",
            font=('Arial', 9),
            bg='#e0e0e0',
            fg='#666'
        )
        self.status_label.pack(pady=5)
        
        # Chat display area
        chat_frame = tk.Frame(self.root, bg='white')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#ffffff',
            fg='#333',
            state=tk.DISABLED,
            spacing3=8
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colored messages
        self.chat_display.tag_config('mimi', foreground='#ff1493', font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('user', foreground='#1e90ff', font=('Arial', 11, 'bold'))
        self.chat_display.tag_config('system', foreground='#888', font=('Arial', 10, 'italic'))
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        # Text input
        self.message_entry = tk.Entry(
            input_frame,
            font=('Arial', 12),
            bg='white',
            fg='#333',
            relief=tk.FLAT,
            borderwidth=2
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=8, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message_event)
        self.message_entry.focus()
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send 💬",
            font=('Arial', 11, 'bold'),
            bg='#ff69b4',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.send_message,
            padx=20,
            pady=8
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Voice toggle button
        self.voice_button = tk.Button(
            input_frame,
            text="🔊",
            font=('Arial', 14),
            bg='#90ee90',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.toggle_voice,
            width=3
        )
        self.voice_button.pack(side=tk.RIGHT, padx=(0, 5))
    
    def add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M")
        
        if sender == "Mimi":
            self.chat_display.insert(tk.END, f"💖 {sender} ", 'mimi')
            self.chat_display.insert(tk.END, f"({timestamp})\n", 'system')
            self.chat_display.insert(tk.END, f"{message}\n\n")
        elif sender == "You":
            self.chat_display.insert(tk.END, f"👤 {sender} ", 'user')
            self.chat_display.insert(tk.END, f"({timestamp})\n", 'system')
            self.chat_display.insert(tk.END, f"{message}\n\n")
        else:
            self.chat_display.insert(tk.END, f"{message}\n", 'system')
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message_event(self, event):
        """Handle Enter key press"""
        self.send_message()
    
    def send_message(self):
        """Send user message"""
        message = self.message_entry.get().strip()
        
        if not message:
            return
        
        # Clear input
        self.message_entry.delete(0, tk.END)
        
        # Display user message
        self.add_message("You", message)
        
        # Process in background
        threading.Thread(target=self.process_user_message, args=(message,), daemon=True).start()
    
    def process_user_message(self, user_input):
        """Process user message and respond"""
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            self.add_message("Mimi", "Bye bye, Master! See you later~ ♡")
            self.speak("Bye bye, Master! See you later!")
            time.sleep(2)
            self.root.quit()
            return
        
        # Update status
        self.update_status("🤔 Thinking...")
        
        # Parse commands
        cmd_type, cmd_param = self.parse_user_command(user_input)
        
        response = None
        
        if cmd_type == 'open_youtube':
            webbrowser.open('https://www.youtube.com')
            response = "Opening YouTube for you, Master! ✨"
        
        elif cmd_type == 'search_youtube':
            url = f"https://www.youtube.com/results?search_query={cmd_param.replace(' ', '+')}"
            webbrowser.open(url)
            response = f"Searching YouTube for '{cmd_param}'! Let me find that~ ♡"
        
        elif cmd_type == 'open_app':
            self.open_application(cmd_param)
            response = f"Opening {cmd_param}! Nya~"
        
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
                screen_context = "Screen not analyzed yet."
            
            prompt = f"""{self.vtuber.system_prompt}

SCREEN: {screen_context}

CONVERSATION:
{chr(10).join(self.conversation_history[-5:])}
User: {user_input}

Respond naturally as {self.vtuber_name}! Keep it short (1-2 sentences) and sweet!

{self.vtuber_name}:"""
            
            response = self.vtuber._generate(prompt, max_tokens=100).strip()
            if ':' in response:
                response = response.split(':', 1)[1].strip()
        
        # Display and speak response
        if response:
            self.add_message("Mimi", response)
            self.speak(response)
            
            self.conversation_history.append(f"User: {user_input}")
            self.conversation_history.append(f"Mimi: {response}")
        
        self.update_status("👁️ Watching screen... | 🎤 Voice: " + ("ON" if self.enable_voice else "OFF"))
    
    def parse_user_command(self, text):
        """Parse commands from text - FIXED VERSION"""
        text_lower = text.lower()
        
        # Open YouTube
        if 'youtube' in text_lower and ('open' in text_lower or 'go' in text_lower):
            return ('open_youtube', None)
        
        # Search YouTube - EXPANDED!
        if 'youtube' in text_lower and ('search' in text_lower or 'find' in text_lower):
            keywords = ['search youtube for', 'find on youtube', 'search for', 'find', 'search']
            for kw in keywords:
                if kw in text_lower:
                    query = text.split(kw, 1)[1].strip()
                    if query:
                        return ('search_youtube', query)
        
        # Default "search X" to YouTube
        if 'search for' in text_lower:
            query = text.split('search for', 1)[1].strip()
            if query:
                return ('search_youtube', query)
        
        if text_lower.startswith('search '):
            query = text.split('search ', 1)[1].strip()
            if query and 'box' not in query and 'button' not in query:
                return ('search_youtube', query)
        
        # "find X" defaults to YouTube
        if text_lower.startswith('find '):
            query = text.split('find ', 1)[1].strip()
            if query and 'box' not in query and 'button' not in query:
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
        if 'type' in text_lower and text_lower.startswith('type '):
            text_to_type = text.split('type', 1)[1].strip()
            return ('type', text_to_type)
        
        return (None, None)
    
    def open_application(self, app_name):
        """Open application"""
        apps = {
            'chrome': 'chrome.exe',
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
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
        """Click detected object"""
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
    
    def speak(self, text):
        """Speak text"""
        if self.enable_voice:
            threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()
    
    def _speak_thread(self, text):
        """Background speech thread"""
        while self.voice.is_busy():
            time.sleep(0.1)
        self.voice.speak(text, block=True)
    
    def toggle_voice(self):
        """Toggle voice on/off"""
        self.enable_voice = not self.enable_voice
        
        if self.enable_voice:
            self.voice_button.config(bg='#90ee90', text='🔊')
            self.add_message("System", "🔊 Voice enabled")
        else:
            self.voice_button.config(bg='#ffcccb', text='🔇')
            self.add_message("System", "🔇 Voice muted")
        
        self.update_status("👁️ Watching screen... | 🎤 Voice: " + ("ON" if self.enable_voice else "OFF"))
    
    def update_status(self, text):
        """Update status bar"""
        self.status_label.config(text=text)
    
    def start_background_threads(self):
        """Start screen monitoring and AI worker"""
        
        # Screen monitoring thread
        screen_thread = threading.Thread(target=self.monitor_screen, daemon=True)
        screen_thread.start()
        
        # AI worker thread
        ai_thread = threading.Thread(target=self.ai_worker, daemon=True)
        ai_thread.start()
    
    def monitor_screen(self):
        """Monitor screen for changes"""
        for frame in self.capture.capture_stream(duration=999999):
            with self.lock:
                self.latest_frame = frame.copy()
            
            analysis = self.understanding.analyze_screen(frame)
            
            with self.lock:
                self.current_analysis = analysis
            
            # Check for changes
            if self.check_for_changes(analysis):
                if self.ai_queue.qsize() < 20:
                    self.ai_queue.put("screen changed")
    
    def check_for_changes(self, analysis):
        """Check if screen changed"""
        current_sig = self.get_objects_signature(analysis['objects'])
        current_scene = analysis['caption']
        
        if not self.last_objects_sig:
            self.last_objects_sig = current_sig
            self.last_scene = current_scene
            return True
        
        if current_sig != self.last_objects_sig or current_scene != self.last_scene:
            self.last_objects_sig = current_sig
            self.last_scene = current_scene
            return True
        
        return False
    
    def get_objects_signature(self, objects):
        """Get unique signature of objects"""
        sig_parts = []
        for obj in objects:
            name = obj['class_name']
            x = round(obj['center'][0] / 50) * 50
            y = round(obj['center'][1] / 50) * 50
            sig_parts.append(f"{name}@{x},{y}")
        return "|".join(sorted(sig_parts))
    
    def ai_worker(self):
        """Background AI worker"""
        while self.ai_thread_running:
            try:
                # Random comments
                if self.should_make_random_comment():
                    comment = random.choice(self.random_topics)
                    self.root.after(0, self.add_message, "Mimi", comment)
                    self.speak(comment)
                    time.sleep(1)
                    continue
                
                # Process screen changes
                task = self.ai_queue.get(timeout=5)
                
                with self.lock:
                    analysis = self.current_analysis
                
                if not analysis:
                    continue
                
                # Generate response
                response = self.generate_screen_response(analysis)
                
                if response:
                    self.root.after(0, self.add_message, "Mimi", response)
                    self.speak(response)
                
            except:
                pass
    
    def should_make_random_comment(self):
        """Should make random comment"""
        if time.time() - self.last_random_comment_time > random.randint(60, 120):
            self.last_random_comment_time = time.time()
            return random.random() < 0.3
        return False
    
    def generate_screen_response(self, analysis):
        """Generate response to screen change"""
        prompt = f"""{self.vtuber.system_prompt}

I see: {analysis['caption']}
{analysis['object_count']} objects detected.

React briefly and cutely to what you see! Just 1-2 sentences!

{self.vtuber_name}:"""
        
        response = self.vtuber._generate(prompt, max_tokens=80).strip()
        if ':' in response:
            response = response.split(':', 1)[1].strip()
        
        return response
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = MimiChatGUI()
    app.run()