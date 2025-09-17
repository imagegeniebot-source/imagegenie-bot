# test_local.py - Test avec Google AI Studio
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Charger les variables d'environnement
load_dotenv()

# Configurer Google AI Studio
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def test_google_ai_studio():
    """Test de connexion à Google AI Studio"""
    print("🎨 Test de Google AI Studio...")
    
    try:
        # Lister les modèles disponibles
        print("\n📋 Modèles disponibles:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Test avec Gemini Pro (texte)
        print("\n💬 Test génération de texte...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Dis bonjour en français")
        print(f"Réponse: {response.text}")
        
        # Test pour génération d'image avec Imagen
        # Note: Imagen n'est pas encore disponible directement via cette API
        # On utilisera une approche alternative
        
        print("\n✅ Google AI Studio connecté avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("\n💡 Vérifiez votre clé API sur https://makersuite.google.com/app/apikey")
        return False

def test_image_generation_prompt():
    """Test de création de prompt pour image"""
    print("\n🖼️ Test de génération de prompt d'image...")
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Utiliser Gemini pour améliorer les prompts
        prompt = "un chat sur la lune"
        
        enhanced_prompt_request = f"""
        Améliore ce prompt pour génération d'image. Rends-le plus détaillé et précis.
        Prompt original: {prompt}
        
        Réponds uniquement avec le prompt amélioré, sans explications.
        """
        
        response = model.generate_content(enhanced_prompt_request)
        enhanced_prompt = response.text.strip()
        
        print(f"Prompt original: {prompt}")
        print(f"Prompt amélioré: {enhanced_prompt}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("TEST GOOGLE AI STUDIO")
    print("="*50)
    
    # Vérifier la clé API
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY non trouvée dans .env")
        print("👉 Obtenez votre clé sur: https://makersuite.google.com/app/apikey")
    else:
        print("✅ Clé API trouvée")
        
        # Tester la connexion
        if test_google_ai_studio():
            test_image_generation_prompt()
            print("\n🎉 Configuration réussie!")
        else:
            print("\n⚠️ Vérifiez votre configuration")