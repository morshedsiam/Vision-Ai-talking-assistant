# voice_controller.py - AGGRESSIVE FIX
import pyttsx3
import threading
import time

class VoiceController:
    """Voice controller with aggressive engine reset"""
    
    def __init__(self, voice_id=None, rate=160, volume=1.0):
        print("🔊 Initializing Voice Controller (Aggressive Mode)...")
        
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self.is_speaking = False
        self.speech_lock = threading.Lock()
        
        print(f"   Speed: {rate} WPM")
        print(f"   Volume: {volume * 100:.0f}%")
        print("✅ Voice ready!\n")
    
    def speak(self, text, block=False):
        """Speak with completely fresh engine"""
        if not text or len(text.strip()) == 0:
            return
        
        # Clean text
        clean_text = self._clean_text(text)
        
        if block:
            self._speak_blocking(clean_text)
        else:
            thread = threading.Thread(target=self._speak_blocking, args=(clean_text,), daemon=True)
            thread.start()
    
    def _speak_blocking(self, text):
        """Speak with FRESH engine instance every time"""
        with self.speech_lock:
            self.is_speaking = True
            engine = None
            
            try:
                print(f"🔊 Creating fresh TTS engine...")
                
                # CREATE COMPLETELY NEW ENGINE
                engine = pyttsx3.init()
                
                # Small delay for initialization
                time.sleep(0.1)
                
                # Get voices
                voices = engine.getProperty('voices')
                print(f"🔊 Found {len(voices)} voices")
                
                # Set voice
                if self.voice_id is not None and self.voice_id < len(voices):
                    engine.setProperty('voice', voices[self.voice_id].id)
                    print(f"🔊 Using voice: {voices[self.voice_id].name}")
                else:
                    # Try female voice
                    for i, voice in enumerate(voices):
                        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            print(f"🔊 Using voice: {voice.name}")
                            break
                
                # Set rate and volume
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                
                # Small delay after setting properties
                time.sleep(0.1)
                
                print(f"🔊 Speaking: \"{text[:50]}...\"")
                
                # Say the text
                engine.say(text)
                
                # CRITICAL: Run and wait
                engine.runAndWait()
                
                # CRITICAL: Stop engine explicitly
                engine.stop()
                
                # CRITICAL: Small delay before cleanup
                time.sleep(0.2)
                
                print(f"✅ Speech finished")
                
            except Exception as e:
                print(f"❌ Speech error: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                # CRITICAL: Clean up engine
                if engine:
                    try:
                        engine.stop()
                        del engine
                    except:
                        pass
                
                # Extra delay to ensure cleanup
                time.sleep(0.1)
                
                self.is_speaking = False
    
    def _clean_text(self, text):
        """Remove characters that break TTS"""
        replacements = {
            '~': '',
            '♡': '',
            '✨': '',
            '(◕‿◕✿)': '',
            '(｡♥‿♥｡)': '',
            '>///<': '',
            'Nya~': 'Nya',
            'Ehehe~': 'Ehehe',
            'Yay~': 'Yay',
        }
        
        clean = text
        for old, new in replacements.items():
            clean = clean.replace(old, new)
        
        return clean
    
    def is_busy(self):
        return self.is_speaking
    
    def stop(self):
        self.is_speaking = False


# Test with delays
if __name__ == "__main__":
    print("="*70)
    print("🎤 VOICE CONTROLLER TEST (AGGRESSIVE)")
    print("="*70)
    print()
    
    voice = VoiceController(rate=170, volume=0.9)
    
    test_phrases = [
        "First speech test",
        "Second speech test",
        "Third speech test",
        "Fourth speech test",
        "Fifth speech test"
    ]
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_phrases)}")
        print(f"{'='*70}")
        
        voice.speak(phrase, block=True)
        
        # IMPORTANT: Wait between speeches
        print(f"⏸️  Waiting 2 seconds before next speech...")
        time.sleep(2)
    
    print("\n" + "="*70)
    print("✅ Test complete!")
    print("="*70)