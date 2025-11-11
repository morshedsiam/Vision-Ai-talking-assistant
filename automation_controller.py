# automation_controller.py
import pyautogui
import time
import math

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.1      # Small delay between actions

class AutomationController:
    """
    Controls mouse and keyboard based on AI decisions
    Safe and smooth automation
    """
    
    def __init__(self, screen_size=(1920, 1080), safety_mode=True):
        """
        Initialize automation controller
        
        Args:
            screen_size: Your monitor resolution (width, height)
            safety_mode: If True, requires confirmation before actions
        """
        self.screen_width, self.screen_height = screen_size
        self.safety_mode = safety_mode
        self.last_action_time = 0
        self.min_action_delay = 0.5  # Minimum seconds between actions
        
        print("🖱️ Automation Controller initialized")
        print(f"   Screen size: {screen_size}")
        print(f"   Safety mode: {'ON' if safety_mode else 'OFF'}")
        print(f"   Failsafe: Move mouse to top-left corner to abort!")
        print()
    
    def scale_coordinates(self, x, y, from_size=(640, 640)):
        """
        Scale coordinates from detection size to actual screen size
        
        Args:
            x, y: Coordinates in detection image (640x640)
            from_size: Size of detection image
            
        Returns:
            (scaled_x, scaled_y) for actual screen
        """
        from_w, from_h = from_size
        
        # Scale from detection resolution to screen resolution
        scaled_x = int((x / from_w) * self.screen_width)
        scaled_y = int((y / from_h) * self.screen_height)
        
        return scaled_x, scaled_y
    
    def smooth_move_mouse(self, x, y, duration=0.5):
        """
        Smoothly move mouse to position
        
        Args:
            x, y: Target coordinates
            duration: Movement duration (seconds)
        """
        # Get current position
        current_x, current_y = pyautogui.position()
        
        # Calculate distance
        distance = math.sqrt((x - current_x)**2 + (y - current_y)**2)
        
        # Adjust duration based on distance
        adjusted_duration = min(duration, distance / 1000)
        
        # Move smoothly
        pyautogui.moveTo(x, y, duration=adjusted_duration, tween=pyautogui.easeOutQuad)
        
        return current_x, current_y
    
    def click_at(self, x, y, button='left', clicks=1, smooth=True):
        """
        Click at specified position
        
        Args:
            x, y: Click coordinates
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks (1=single, 2=double)
            smooth: Use smooth movement
        """
        # Check action delay
        if not self._check_action_delay():
            print("⚠️  Action too fast! Waiting...")
            time.sleep(self.min_action_delay)
        
        print(f"🖱️  Clicking at ({x}, {y}) - {button} button")
        
        if smooth:
            self.smooth_move_mouse(x, y)
        else:
            pyautogui.moveTo(x, y)
        
        time.sleep(0.1)
        pyautogui.click(button=button, clicks=clicks)
        
        self.last_action_time = time.time()
        
        return True
    
    def type_text(self, text, interval=0.05):
        """
        Type text with human-like timing
        
        Args:
            text: Text to type
            interval: Seconds between keystrokes
        """
        if not self._check_action_delay():
            time.sleep(self.min_action_delay)
        
        print(f"⌨️  Typing: '{text}'")
        
        pyautogui.write(text, interval=interval)
        
        self.last_action_time = time.time()
        
        return True
    
    def press_key(self, key):
        """
        Press a single key or key combination
        
        Args:
            key: Key name (e.g., 'enter', 'ctrl+c', 'alt+tab')
        """
        if not self._check_action_delay():
            time.sleep(self.min_action_delay)
        
        print(f"⌨️  Pressing: {key}")
        
        if '+' in key:
            # Key combination (e.g., 'ctrl+c')
            keys = key.split('+')
            pyautogui.hotkey(*keys)
        else:
            # Single key
            pyautogui.press(key)
        
        self.last_action_time = time.time()
        
        return True
    
    def execute_decision(self, decision, detection_size=(640, 640)):
        """
        Execute AI decision
        
        Args:
            decision: Dict from VTuberAI.analyze_and_act()
            detection_size: Size of detection image
            
        Returns:
            bool: Success
        """
        action_type = decision.get('action_type', 'wait')
        
        print(f"\n🎯 Executing action: {action_type.upper()}")
        
        if action_type == 'click':
            coords = decision.get('coordinates')
            if coords:
                # Scale from detection size to screen size
                x, y = self.scale_coordinates(coords[0], coords[1], detection_size)
                
                # Safety check
                if self.safety_mode:
                    print(f"   Target: {decision.get('target')}")
                    print(f"   Position: ({x}, {y})")
                    confirm = input("   Proceed? (y/n): ").lower()
                    if confirm != 'y':
                        print("   ❌ Action cancelled by user")
                        return False
                
                self.click_at(x, y)
                return True
            else:
                print("   ❌ No coordinates provided")
                return False
        
        elif action_type == 'type':
            text = decision.get('keyboard_input')
            if text:
                if self.safety_mode:
                    print(f"   Will type: '{text}'")
                    confirm = input("   Proceed? (y/n): ").lower()
                    if confirm != 'y':
                        print("   ❌ Action cancelled")
                        return False
                
                self.type_text(text)
                return True
            else:
                print("   ❌ No text to type")
                return False
        
        elif action_type == 'wait':
            print("   ⏸️  Waiting... (no action needed)")
            return True
        
        elif action_type == 'talk':
            print("   💬 Just talking (no automation)")
            return True
        
        else:
            print(f"   ❓ Unknown action type: {action_type}")
            return False
    
    def _check_action_delay(self):
        """Check if enough time has passed since last action"""
        elapsed = time.time() - self.last_action_time
        return elapsed >= self.min_action_delay
    
    def get_screen_size(self):
        """Get actual screen size"""
        return pyautogui.size()


# Test the automation controller
if __name__ == "__main__":
    print("="*70)
    print("🖱️ AUTOMATION CONTROLLER TEST")
    print("="*70)
    print()
    
    # Get actual screen size
    screen_size = pyautogui.size()
    print(f"📺 Detected screen size: {screen_size}")
    print()
    
    controller = AutomationController(
        screen_size=screen_size,
        safety_mode=True  # Safe for testing
    )
    
    print("="*70)
    print("🧪 TEST 1: Mouse Movement")
    print("="*70)
    print()
    
    # Test smooth mouse movement
    print("Moving mouse to center of screen...")
    center_x = screen_size[0] // 2
    center_y = screen_size[1] // 2
    controller.smooth_move_mouse(center_x, center_y, duration=1.0)
    print("✅ Mouse movement test complete!")
    time.sleep(1)
    
    print()
    print("="*70)
    print("🧪 TEST 2: Coordinate Scaling")
    print("="*70)
    print()
    
    # Test coordinate scaling
    test_coords = [
        ([320, 320], "Center of 640x640"),
        ([100, 100], "Top-left area"),
        ([540, 540], "Bottom-right area"),
    ]
    
    for coords, desc in test_coords:
        scaled = controller.scale_coordinates(coords[0], coords[1])
        print(f"{desc}:")
        print(f"  Detection: {coords}")
        print(f"  Scaled: {scaled}")
    
    print()
    print("="*70)
    print("🧪 TEST 3: Simulated AI Decision")
    print("="*70)
    print()
    
    # Test with fake AI decision
    fake_decision = {
        'vtuber_speech': "Let me click that for you~! ✨",
        'action_type': 'click',
        'target': 'Test Button',
        'coordinates': [320, 320],  # Center of detection image
        'emotion': 'happy'
    }
    
    print("Simulating AI decision to click center of screen...")
    print(f"💬 Mimi says: {fake_decision['vtuber_speech']}")
    
    success = controller.execute_decision(fake_decision)
    
    if success:
        print("✅ Decision executed successfully!")
    else:
        print("❌ Decision execution failed or cancelled")
    
    print()
    print("="*70)
    print("✅ Automation controller test complete!")
    print("="*70)