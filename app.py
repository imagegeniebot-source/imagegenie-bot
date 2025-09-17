# app.py - Version complète avec WhatsApp fonctionnel
import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import json
import hashlib
import requests

# Charger config
load_dotenv()

app = Flask(__name__)

# Configuration
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "imagegenie2024")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
DEBUG_MODE = os.getenv("DEBUG_MODE", "True") == "True"

# Configurer Google AI Studio
genai.configure(api_key=GOOGLE_API_KEY)
text_model = genai.GenerativeModel('gemini-pro')

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect('imagegenie.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            tokens INTEGER DEFAULT 1,
            total_generated INTEGER DEFAULT 0,
            created_at TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            prompt TEXT,
            enhanced_prompt TEXT,
            image_url TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def send_whatsapp_message(to_number, message):
    """Envoie un message WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if DEBUG_MODE:
        print(f"📤 Message envoyé: {response.status_code}")
    
    return response.status_code == 200

def send_whatsapp_image(to_number, image_url, caption=""):
    """Envoie une image WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if DEBUG_MODE:
        print(f"📤 Image envoyée: {response.status_code}")
    
    return response.status_code == 200

def enhance_prompt(prompt):
    """Améliore le prompt avec Gemini Pro"""
    try:
        request = f"""
        Améliore ce prompt pour génération d'image. 
        Ajoute des détails artistiques, éclairage, couleurs.
        Maximum 100 mots. Réponds uniquement avec le prompt amélioré.
        
        Prompt: {prompt}
        """
        
        response = text_model.generate_content(request)
        return response.text.strip()
    except Exception as e:
        print(f"Erreur enhancement: {e}")
        return prompt

def generate_image(prompt, phone):
    """Génère une image (placeholder pour MVP)"""
    try:
        # Vérifier/créer utilisateur
        conn = sqlite3.connect('imagegenie.db')
        c = conn.cursor()
        
        # Créer utilisateur si n'existe pas
        c.execute("INSERT OR IGNORE INTO users (phone, tokens, created_at) VALUES (?, 1, ?)",
                  (phone, datetime.now()))
        conn.commit()
        
        # Vérifier les tokens
        c.execute("SELECT tokens FROM users WHERE phone = ?", (phone,))
        result = c.fetchone()
        tokens = result[0]
        
        if tokens < 1:
            conn.close()
            return {
                "success": False,
                "message": "❌ Crédit insuffisant! Vous avez 0 token.\n\n💡 Tapez /recharge pour acheter des tokens"
            }
        
        # Améliorer le prompt
        enhanced = enhance_prompt(prompt)
        
        # Générer une URL unique (placeholder pour MVP)
        prompt_hash = hashlib.md5(enhanced.encode()).hexdigest()[:8]
        image_url = f"https://picsum.photos/seed/{prompt_hash}/512/512"
        
        # Décrémenter tokens et sauvegarder
        c.execute("UPDATE users SET tokens = tokens - 1, total_generated = total_generated + 1 WHERE phone = ?", (phone,))
        
        c.execute("""
            INSERT INTO generations (phone, prompt, enhanced_prompt, image_url, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (phone, prompt, enhanced, image_url, datetime.now()))
        
        conn.commit()
        
        # Récupérer le nouveau solde
        c.execute("SELECT tokens FROM users WHERE phone = ?", (phone,))
        new_tokens = c.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "image_url": image_url,
            "prompt": prompt,
            "enhanced_prompt": enhanced,
            "tokens_left": new_tokens
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erreur: {str(e)}"
        }

def handle_whatsapp_message(from_number, text):
    """Traite les messages WhatsApp entrants"""
    text = text.lower().strip()
    
    print(f"📥 Traitement: {from_number} -> {text}")
    
    # Commandes
    if text in ['/start', 'start', 'salut', 'hello', 'bonjour', 'bonsoir']:
        welcome = """🎨 *Bienvenue sur ImageGenie Bot!*

Je transforme vos idées en images avec l'IA! ✨

🎁 *Vous avez 1 token GRATUIT pour commencer!*

*Comment ça marche:*
Tapez: /image [votre description]

*Exemple:*
/image un logo moderne pour restaurant africain

*Commandes disponibles:*
/image - Générer une image
/solde - Voir vos tokens
/aide - Obtenir de l'aide
/prix - Voir les tarifs"""
        
        send_whatsapp_message(from_number, welcome)
    
    elif text.startswith('/image ') or text.startswith('image '):
        prompt = text.replace('/image ', '').replace('image ', '')
        
        if len(prompt) < 3:
            send_whatsapp_message(from_number, "❌ Description trop courte. Exemple: /image un chat sur la lune")
            return
        
        # Envoyer message d'attente
        send_whatsapp_message(from_number, "🎨 Génération en cours... (15 secondes)")
        
        # Générer l'image
        result = generate_image(prompt, from_number)
        
        if result['success']:
            # Envoyer l'image
            caption = f"✨ *Image générée avec succès!*\n\n📝 _Prompt: {result['prompt']}_\n💰 Tokens restants: {result['tokens_left']}"
            send_whatsapp_image(from_number, result['image_url'], caption)
            
            # Message de suivi
            if result['tokens_left'] == 0:
                send_whatsapp_message(from_number, "⚠️ Vous n'avez plus de tokens!\n\nTapez /recharge pour continuer")
        else:
            send_whatsapp_message(from_number, result['message'])
    
    elif text in ['/solde', 'solde', '/balance', 'balance']:
        # Vérifier le solde
        conn = sqlite3.connect('imagegenie.db')
        c = conn.cursor()
        
        # Créer utilisateur si n'existe pas
        c.execute("INSERT OR IGNORE INTO users (phone, tokens, created_at) VALUES (?, 1, ?)",
                  (from_number, datetime.now()))
        conn.commit()
        
        c.execute("SELECT tokens, total_generated FROM users WHERE phone=?", (from_number,))
        result = c.fetchone()
        tokens = result[0] if result else 1
        total = result[1] if result else 0
        conn.close()
        
        message = f"""💰 *Votre solde*

Tokens disponibles: {tokens}
Images générées: {total}

{'✅ Vous pouvez générer ' + str(tokens) + ' image(s)' if tokens > 0 else '❌ Crédit épuisé'}

Tapez /recharge pour acheter des tokens"""
        
        send_whatsapp_message(from_number, message)
    
    elif text in ['/aide', 'aide', '/help', 'help']:
        help_message = """📖 *Guide d'utilisation*

*Générer une image:*
/image [description]

*Exemples:*
• /image un coucher de soleil sur la plage
• /image logo moderne pour boutique
• /image portrait femme africaine souriante

*Autres commandes:*
• /solde - Voir vos tokens
• /prix - Voir les tarifs
• /recharge - Acheter des tokens

*Tips:*
- Soyez précis dans vos descriptions
- Mentionnez le style souhaité
- Ajoutez des couleurs

*Support:* Répondez avec votre question"""
        
        send_whatsapp_message(from_number, help_message)
    
    elif text in ['/prix', 'prix', '/price', 'price', '/tarif', 'tarif']:
        pricing = """💳 *Nos Tarifs*

📦 *Pack Découverte*
500 FCFA = 5 tokens

📦 *Pack Standard*
1000 FCFA = 12 tokens (+2 bonus!)

📦 *Pack Pro*
2500 FCFA = 35 tokens (+5 bonus!)

*1 token = 1 image*

Pour commander: /recharge"""
        
        send_whatsapp_message(from_number, pricing)
    
    elif text in ['/recharge', 'recharge', '/buy', 'buy', '/acheter']:
        recharge = """💳 *Recharge de Tokens*

*Étape 1:* Choisissez votre pack
• 500 F = 5 tokens
• 1000 F = 12 tokens  
• 2500 F = 35 tokens

*Étape 2:* Envoyez à
• MTN MoMo: 97 XX XX XX
• Moov Money: 95 XX XX XX

*Étape 3:* Envoyez votre reçu ici

⚡ Activation en 5 minutes!"""
        
        send_whatsapp_message(from_number, recharge)
    
    else:
        # Message non reconnu
        default = """❓ Je n'ai pas compris votre message.

*Pour générer une image:*
/image [votre description]

*Exemple:*
/image un chat mignon

Tapez /aide pour plus d'infos"""
        
        send_whatsapp_message(from_number, default)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "ImageGenie WhatsApp Bot",
        "version": "1.0",
        "ready": True
    })

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Webhook pour WhatsApp"""
    
    if request.method == 'GET':
        # Vérification du webhook
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('✅ Webhook vérifié!')
            return challenge, 200
        return 'Invalid', 403
    
    if request.method == 'POST':
        # Réception des messages
        data = request.json
        
        try:
            # Extraire le message
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            if 'messages' in value:
                message = value['messages'][0]
                from_number = message['from']
                msg_type = message['type']
                
                if msg_type == 'text':
                    text = message['text']['body']
                    
                    if DEBUG_MODE:
                        print(f"📱 Message de {from_number}: {text}")
                    
                    # Traiter le message
                    handle_whatsapp_message(from_number, text)
            
        except Exception as e:
            print(f"Erreur webhook: {e}")
        
        return 'OK', 200

if __name__ == '__main__':
    print("="*50)
    print("🚀 ImageGenie WhatsApp Bot")
    print("="*50)
    
    init_db()
    
    if DEBUG_MODE:
        print("🔧 Mode DEBUG activé")
        print("📍 URL locale: http://localhost:5000")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG_MODE)