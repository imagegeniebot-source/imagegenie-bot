# image_generator.py - Génération d'images avec Google AI
import os
import requests
import json
import base64
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.text_model = genai.GenerativeModel('gemini-pro')
        
    def enhance_prompt(self, prompt):
        """Améliore le prompt avec Gemini Pro"""
        try:
            enhancement_request = f"""
            Transform this request into a detailed image generation prompt.
            Add artistic style, lighting, colors, and composition details.
            Keep it under 100 words.
            Request: {prompt}
            
            Reply only with the enhanced prompt.
            """
            
            response = self.text_model.generate_content(enhancement_request)
            return response.text.strip()
        except:
            return prompt  # Retourne l'original si erreur
    
    def generate_image_url(self, prompt):
        """
        Pour le MVP, on utilise une approche alternative
        car Imagen 3 nécessite Vertex AI (plus complexe)
        """
        
        # Option 1: Utiliser un service de placeholder pour le MVP
        # (Remplace par Imagen quand tu auras Vertex AI configuré)
        
        import hashlib
        import urllib.parse
        
        # Améliorer le prompt
        enhanced_prompt = self.enhance_prompt(prompt)
        
        # Pour le MVP : générer une URL unique basée sur le prompt
        # (Remplacera par vraie génération plus tard)
        prompt_hash = hashlib.md5(enhanced_prompt.encode()).hexdigest()[:8]
        
        # Services de placeholder gratuits pour tester
        # Option 1: Lorem Picsum (images aléatoires)
        image_url = f"https://picsum.photos/seed/{prompt_hash}/512/512"
        
        # Option 2: Placeholder avec texte
        # text = urllib.parse.quote(prompt[:30])
        # image_url = f"https://via.placeholder.com/512x512/7F5AF0/ffffff?text={text}"
        
        return {
            "success": True,
            "url": image_url,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "message": "Image générée (placeholder pour MVP)"
        }
    
    def generate_with_dalle(self, prompt):
        """
        Alternative: Si tu veux utiliser DALL-E via une API tierce
        (nécessite une clé OpenAI)
        """
        # Pour plus tard si tu veux
        pass

# Test du générateur
if __name__ == "__main__":
    print("="*50)
    print("TEST GÉNÉRATEUR D'IMAGES")
    print("="*50)
    
    generator = ImageGenerator()
    
    # Test 1: Enhancement de prompt
    test_prompt = "un logo pour restaurant africain"
    print(f"\n📝 Prompt original: {test_prompt}")
    
    enhanced = generator.enhance_prompt(test_prompt)
    print(f"✨ Prompt amélioré: {enhanced}")
    
    # Test 2: Génération d'image
    print("\n🎨 Génération d'image...")
    result = generator.generate_image_url(test_prompt)
    
    if result["success"]:
        print(f"✅ Succès!")
        print(f"🔗 URL: {result['url']}")
        print(f"💬 {result['message']}")
    else:
        print(f"❌ Erreur: {result.get('message')}")