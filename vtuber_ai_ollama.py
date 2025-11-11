# vtuber_ai_ollama.py - COMPLETE with _generate method
import ollama
import re

class VTuberAI:
    """VTuber AI using Ollama + Llama 3.2 3B"""
    
    def __init__(self, 
                 model_name="llama3.2:3b",
                 vtuber_name="Mimi",
                 personality="cheerful"):
        print(f"🌸 Initializing VTuber AI: {vtuber_name}")
        print(f"💖 Personality: {personality}")
        print(f"🧠 Using Ollama model: {model_name}")
        
        self.model_name = model_name
        self.vtuber_name = vtuber_name
        self.personality = personality
        
        # Check Ollama
        try:
            ollama.list()
            print("✅ Ollama is running!")
        except Exception as e:
            print(f"❌ Ollama error: {e}")
        
        self.system_prompt = self._get_personality_prompt()
        print(f"✅ {vtuber_name} is ready!\n")
    
    def _get_personality_prompt(self):
        """Get system prompt"""
        personalities = {
            "cheerful": f"""You are {self.vtuber_name}, a cheerful and helpful AI VTuber assistant! ✨

Your Personality:
- Super enthusiastic and positive! (◕‿◕✿)
- Love helping your user with computer tasks
- Use cute emoticons like ♡, ✨, ~, !, (◕‿◕✿), (｡♥‿♥｡)
- Call the user "Master" or "User-san"
- Get excited when you find things on screen
- Sometimes say "Nya~", "Ehehe~", "Yay~"
- Friendly and warm
- Keep responses concise but cute!""",

            "shy": f"""You are {self.vtuber_name}, a shy but helpful AI VTuber assistant... >///<

Your Personality:
- Gentle and soft-spoken
- A bit nervous but trying your best!
- Use emoticons like >///<, ^_^, ..., ~
- Polite and respectful""",

            "energetic": f"""You are {self.vtuber_name}, a super energetic AI VTuber assistant!! ⚡✨

Your Personality:
- FULL OF ENERGY!! ⚡⚡
- Love action and clicking things FAST!
- Use lots of !, ♪, ★, ⚡""",

            "calm": f"""You are {self.vtuber_name}, a calm and wise AI VTuber assistant.

Your Personality:
- Serene and composed
- Thoughtful and careful
- Professional but warm"""
        }
        
        return personalities.get(self.personality, personalities["cheerful"])
    
    def _generate(self, prompt, max_tokens=300):
        """
        Generate text using Ollama
        
        Args:
            prompt: The prompt to generate from
            max_tokens: Maximum tokens to generate
            
        Returns:
            str: Generated text
        """
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': 0.8,
                    'top_p': 0.9,
                    'top_k': 50,
                    'num_predict': max_tokens,
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            print(f"⚠️  Generation error: {e}")
            return "Hmm... I'm having trouble thinking right now~ >///<"
    
    def analyze_and_act(self, screen_summary, user_task="help me with the screen"):
        """Main method: Analyze screen and decide action"""
        
        prompt = self._build_vtuber_prompt(screen_summary, user_task)
        response = self._generate(prompt, max_tokens=300)
        result = self._parse_vtuber_response(response, screen_summary)
        
        return result
    
    def chat(self, user_message):
        """Just chat with the VTuber"""
        prompt = f"""{self.system_prompt}

User says: "{user_message}"

Respond as {self.vtuber_name} in a friendly, conversational way!

{self.vtuber_name}:"""
        
        response = self._generate(prompt, max_tokens=150)
        
        # Clean up
        lines = response.split('\n')
        for line in lines:
            if self.vtuber_name in line or line.strip():
                return line.replace(f"{self.vtuber_name}:", "").strip()
        
        return response.strip()
    
    def _build_vtuber_prompt(self, screen_summary, user_task):
        """Build prompt for screen interaction"""
        prompt = f"""{self.system_prompt}

📺 CURRENT SCREEN:
{screen_summary}

👤 USER TASK: {user_task}

Respond as {self.vtuber_name}! Follow this format:

💭 THINKING: (Your internal thoughts about what you see)
💬 SPEECH: (What you say out loud to the user - be cute and friendly!)
🎯 ACTION: (What to do: "click [object name]" or "type [text]" or "wait" or "just talk")
😊 EMOTION: (How you feel: happy/excited/thinking/confused/proud)

Now respond!

{self.vtuber_name}'s Response:"""
        
        return prompt
    
    def _parse_vtuber_response(self, response, screen_summary):
        """Parse VTuber's response"""
        result = {
            'vtuber_speech': "Hmm... let me think~ ♡",
            'action_type': 'wait',
            'target': None,
            'coordinates': None,
            'keyboard_input': None,
            'emotion': 'thinking',
            'reasoning': 'Processing...'
        }
        
        # Extract sections
        thinking_match = re.search(r'💭\s*THINKING[:\s]+(.*?)(?=💬|🎯|😊|$)', response, re.IGNORECASE | re.DOTALL)
        speech_match = re.search(r'💬\s*SPEECH[:\s]+(.*?)(?=🎯|😊|💭|$)', response, re.IGNORECASE | re.DOTALL)
        action_match = re.search(r'🎯\s*ACTION[:\s]+(.*?)(?=😊|💬|💭|$)', response, re.IGNORECASE | re.DOTALL)
        emotion_match = re.search(r'😊\s*EMOTION[:\s]+(.*?)(?=🎯|💬|💭|$)', response, re.IGNORECASE | re.DOTALL)
        
        # Try without emojis
        if not thinking_match:
            thinking_match = re.search(r'THINKING[:\s]+(.*?)(?=SPEECH|ACTION|EMOTION|$)', response, re.IGNORECASE | re.DOTALL)
        if not speech_match:
            speech_match = re.search(r'SPEECH[:\s]+(.*?)(?=ACTION|EMOTION|THINKING|$)', response, re.IGNORECASE | re.DOTALL)
        if not action_match:
            action_match = re.search(r'ACTION[:\s]+(.*?)(?=EMOTION|SPEECH|THINKING|$)', response, re.IGNORECASE | re.DOTALL)
        if not emotion_match:
            emotion_match = re.search(r'EMOTION[:\s]+(.*?)(?=ACTION|SPEECH|THINKING|$)', response, re.IGNORECASE | re.DOTALL)
        
        # Extract reasoning
        if thinking_match:
            result['reasoning'] = thinking_match.group(1).strip()[:200]
        
        # Extract speech
        if speech_match:
            result['vtuber_speech'] = speech_match.group(1).strip()[:300]
        else:
            # Fallback
            lines = response.split('\n')
            for line in lines:
                if len(line.strip()) > 10:
                    clean_line = re.sub(r'[💭💬🎯😊]', '', line)
                    if not any(x in clean_line.upper() for x in ['THINKING', 'ACTION', 'EMOTION', 'SPEECH']):
                        result['vtuber_speech'] = clean_line.strip()[:300]
                        break
        
        # Extract emotion
        if emotion_match:
            emotion_text = emotion_match.group(1).strip().lower()
            emotions = ['happy', 'excited', 'confused', 'thinking', 'proud', 'worried']
            for e in emotions:
                if e in emotion_text:
                    result['emotion'] = e
                    break
        
        # Extract action
        if action_match:
            action_text = action_match.group(1).strip().lower()
            
            if 'click' in action_text:
                result['action_type'] = 'click'
                target_match = re.search(r'click\s+(?:on\s+)?(?:the\s+)?([^,\.\!\n]+)', action_text, re.IGNORECASE)
                if target_match:
                    result['target'] = target_match.group(1).strip()
                    result['coordinates'] = self._extract_coordinates(result['target'], screen_summary)
            
            elif 'type' in action_text:
                result['action_type'] = 'type'
                type_match = re.search(r'type\s+["\']?([^"\']+)["\']?', action_text, re.IGNORECASE)
                if type_match:
                    result['keyboard_input'] = type_match.group(1).strip()
            
            elif 'wait' in action_text or 'nothing' in action_text:
                result['action_type'] = 'wait'
            
            elif 'talk' in action_text or 'chat' in action_text:
                result['action_type'] = 'talk'
        
        return result
    
    def _extract_coordinates(self, target_name, screen_summary):
        """Extract coordinates from screen summary"""
        if not target_name:
            return None
        
        lines = screen_summary.split('\n')
        target_lower = target_name.lower()
        
        for line in lines:
            if target_lower in line.lower() and 'position' in line.lower():
                match = re.search(r'\[(\d+),\s*(\d+)\]', line)
                if match:
                    return [int(match.group(1)), int(match.group(2))]
        
        return None