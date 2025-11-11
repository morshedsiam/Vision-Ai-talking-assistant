# clip_captioner.py
import clip
import torch
from PIL import Image
import numpy as np

class CLIPScreenCaptioner:
    """
    Use CLIP to classify screen scenes into predefined categories
    Fast and lightweight for real-time use
    """
    
    def __init__(self, device='cuda'):
        """Load CLIP model"""
        print("📦 Loading CLIP model...")
        self.device = device
        self.model, self.preprocess = clip.load("ViT-B/32", device=device)
        print(f"✅ CLIP loaded on {device}")
        
        # Predefined scene descriptions
        self.scene_templates = [
            "a screenshot of a WhatsApp chat conversation",
            "a screenshot of a file explorer with folders and files",
            "a screenshot of a web browser with search bar",
            "a screenshot of a desktop with icons",
            "a screenshot of a video player",
            "a screenshot of a code editor or terminal",
            "a screenshot of social media application",
            "a screenshot of email application",
            "a screenshot of settings menu",
            "a screenshot of empty desktop wallpaper",
            "a screenshot of gaming application",
            "a screenshot of document viewer or PDF reader"
        ]
        
        # Precompute text embeddings for speed
        print("🔄 Encoding scene templates...")
        self.text_features = self._encode_texts(self.scene_templates)
        print("✅ Ready for captioning!\n")
    
    def _encode_texts(self, texts):
        """Encode text prompts into embeddings"""
        text_tokens = clip.tokenize(texts).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features
    
    def caption_frame(self, frame, top_k=3):
        """
        Generate caption for a screen frame
        
        Args:
            frame: numpy array (H, W, 3) RGB image
            top_k: Return top K most likely descriptions
            
        Returns:
            dict: {
                'primary': str,  # Most likely description
                'top_k': list,   # Top K descriptions with scores
                'all_scores': dict  # All descriptions with scores
            }
        """
        # Convert numpy to PIL Image
        if isinstance(frame, np.ndarray):
            frame = Image.fromarray(frame)
        
        # Preprocess image
        image_input = self.preprocess(frame).unsqueeze(0).to(self.device)
        
        # Encode image
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        
        # Calculate similarity
        similarity = (100.0 * image_features @ self.text_features.T).softmax(dim=-1)
        values, indices = similarity[0].topk(top_k)
        
        # Build results
        top_descriptions = []
        all_scores = {}
        
        for i, (value, index) in enumerate(zip(values, indices)):
            desc = self.scene_templates[index]
            score = value.item()
            top_descriptions.append({
                'description': desc,
                'confidence': round(score, 3)
            })
        
        # All scores
        for i, template in enumerate(self.scene_templates):
            all_scores[template] = round(similarity[0][i].item(), 3)
        
        return {
            'primary': top_descriptions[0]['description'],
            'confidence': top_descriptions[0]['confidence'],
            'top_k': top_descriptions,
            'all_scores': all_scores
        }
    
    def get_simple_caption(self, frame):
        """
        Get a simple one-line caption
        
        Returns: str
        """
        result = self.caption_frame(frame, top_k=1)
        return result['primary']


# Test the captioner
if __name__ == "__main__":
    from screen_capture import ScreenCapture
    
    print("🎬 Starting CLIP screen captioning test...\n")
    
    # Initialize
    captioner = CLIPScreenCaptioner(device='cuda')
    capture = ScreenCapture(target_fps=5, resize=(640, 640))  # Slower FPS for testing
    
    print("📺 Captioning your screen for 20 seconds...")
    print("Try opening different apps to see different captions!\n")
    
    frame_count = 0
    
    for frame in capture.capture_stream(duration=20):
        frame_count += 1
        
        # Generate caption
        result = captioner.caption_frame(frame, top_k=3)
        
        print(f"\n📸 Frame {frame_count}:")
        print(f"   Primary: {result['primary']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Top 3:")
        for i, desc in enumerate(result['top_k'], 1):
            print(f"      {i}. {desc['description']} ({desc['confidence']:.1%})")
        print("-" * 70)
    
    print("\n✅ CLIP captioning test complete!")