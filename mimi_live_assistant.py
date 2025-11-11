# mimi_live_assistant.py
from screen_understanding import ScreenUnderstanding
from vtuber_ai_ollama import VTuberAI
from automation_controller import AutomationController
from screen_capture import ScreenCapture
import pyautogui
import time

class MimiLiveAssistant:
    """
    Complete VTuber AI Assistant that:
    1. Watches your screen
    2. Understands what's happening
    3. Decides what to do
    4. Actually controls mouse/keyboard
    5. Talks to you with personality!
    """
    
    def __init__(self, 
                 vtuber_name="Mimi",
                 personality="cheerful",
                 safety_mode=True,
                 auto_execute=False):
        """
        Initialize Mimi
        
        Args:
            vtuber_name: VTuber's name
            personality: 'cheerful', 'shy', 'energetic', 'calm'
            safety_mode: Ask before executing actions
            auto_execute: Automatically execute without asking
        """
        print("="*70)
        print(f"🌸 INITIALIZING {vtuber_name.upper()} - LIVE AI ASSISTANT")
        print("="*70)
        print()
        
        # Get screen size
        screen_size = pyautogui.size()
        print(f"📺 Screen: {screen_size}")
        print()
        
        # Initialize components
        print("Loading components...")
        self.understanding = ScreenUnderstanding()
        self.vtuber = VTuberAI(vtuber_name=vtuber_name, personality=personality)
        self.controller = AutomationController(
            screen_size=screen_size,
            safety_mode=safety_mode and not auto_execute
        )
        self.capture = ScreenCapture(target_fps=5, resize=(640, 640))
        
        self.auto_execute = auto_execute
        self.action_count = 0
        
        print(f"✅ {vtuber_name} is ready to help!\n")
    
    def run_interactive(self, task="help me with the screen", duration=60):
        """
        Run Mimi in interactive mode
        
        Args:
            task: What you want Mimi to help with
            duration: How long to run (seconds)
        """
        print("="*70)
        print(f"🎬 {self.vtuber.vtuber_name} IS NOW WATCHING YOUR SCREEN!")
        print("="*70)
        print()
        print(f"📋 Task: {task}")
        print(f"⏱️  Duration: {duration} seconds")
        print(f"🛡️  Safety mode: {'ON' if self.controller.safety_mode else 'OFF'}")
        print(f"🤖 Auto-execute: {'YES' if self.auto_execute else 'NO'}")
        print()
        print("⚠️  FAILSAFE: Move mouse to top-left corner to abort!")
        print()
        input("Press ENTER to start...")
        print()
        
        start_time = time.time()
        frame_count = 0
        
        try:
            for frame in self.capture.capture_stream(duration=duration):
                frame_count += 1
                elapsed = time.time() - start_time
                
                # Analyze screen
                analysis = self.understanding.analyze_screen(frame)
                
                # Only act if something interesting is found
                if analysis['object_count'] > 0 or frame_count % 10 == 0:
                    
                    # AI decides what to do
                    decision = self.vtuber.analyze_and_act(
                        screen_summary=analysis['summary'],
                        user_task=task
                    )
                    
                    # Display info
                    print("="*70)
                    print(f"⏱️  Time: {elapsed:.1f}s | Frame: {frame_count}")
                    print("="*70)
                    print(f"\n🖼️  Scene: {analysis['caption']}")
                    print(f"📊 Objects: {analysis['object_count']} | Clickable: {analysis['clickable_count']}")
                    
                    print(f"\n💭 {self.vtuber.vtuber_name}'s thoughts:")
                    print(f"   {decision['reasoning'][:100]}...")
                    
                    print(f"\n💬 {self.vtuber.vtuber_name} says:")
                    print(f"   \"{decision['vtuber_speech']}\"")
                    
                    print(f"\n😊 Emotion: {decision['emotion']}")
                    print(f"🎯 Planned action: {decision['action_type'].upper()}")
                    
                    # Execute action if needed
                    if decision['action_type'] in ['click', 'type']:
                        if self.auto_execute:
                            print("\n🤖 Auto-executing...")
                            success = self.controller.execute_decision(decision)
                        else:
                            print("\n⏸️  Action ready to execute")
                            execute = input("   Execute this action? (y/n): ").lower()
                            if execute == 'y':
                                success = self.controller.execute_decision(decision)
                            else:
                                print("   ⏭️  Skipped")
                                success = False
                        
                        if success:
                            self.action_count += 1
                            print(f"   ✅ Action #{self.action_count} completed!")
                    
                    print()
                
                # Small delay between analyses
                time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped by user")
        
        # Summary
        print()
        print("="*70)
        print("📊 SESSION SUMMARY")
        print("="*70)
        print(f"⏱️  Total time: {elapsed:.1f}s")
        print(f"📸 Frames analyzed: {frame_count}")
        print(f"🎯 Actions executed: {self.action_count}")
        print()
        print(f"💬 {self.vtuber.vtuber_name} says: \"Thanks for letting me help! Bye bye~! ♡\"")
        print("="*70)


# Run Mimi!
if __name__ == "__main__":
    # Initialize Mimi
    mimi = MimiLiveAssistant(
        vtuber_name="Mimi",
        personality="cheerful",
        safety_mode=True,      # Ask before each action
        auto_execute=False     # Don't auto-execute (safe for testing)
    )
    
    # Run with a task
    mimi.run_interactive(
        task="look at the screen and identify any clickable elements",
        duration=60  # Run for 1 minute
    )