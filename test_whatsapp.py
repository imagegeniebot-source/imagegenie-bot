# test_whatsapp.py - Teste l'envoi de messages WhatsApp
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')

def send_test_message(to_number):
    """Envoie un message de test via WhatsApp"""
    
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": "🎉 Test réussi! ImageGenie Bot est connecté à WhatsApp!"
        }
    }
    
    print(f"📤 Envoi du message à {to_number}...")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("✅ Message envoyé avec succès!")
        print(f"Réponse: {response.json()}")
        return True
    else:
        print(f"❌ Erreur {response.status_code}")
        print(f"Détails: {response.text}")
        return False

def test_template_message(to_number):
    """Envoie un message template (hello_world)"""
    
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Template hello_world (pré-approuvé par Meta)
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US"
            }
        }
    }
    
    print(f"📤 Envoi du template à {to_number}...")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("✅ Template envoyé!")
        return True
    else:
        print(f"❌ Erreur: {response.text}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("TEST WHATSAPP API")
    print("="*50)
    
    # Vérifie les variables
    if not WHATSAPP_TOKEN:
        print("❌ WHATSAPP_TOKEN manquant dans .env")
        exit(1)
    
    if not PHONE_NUMBER_ID:
        print("❌ PHONE_NUMBER_ID manquant dans .env")
        exit(1)
    
    print("✅ Configuration trouvée")
    print(f"📱 Phone Number ID: {PHONE_NUMBER_ID}")
    print(f"🔑 Token: {WHATSAPP_TOKEN[:20]}...")
    
    # Demande le numéro de destination
    print("\n⚠️ IMPORTANT: Le numéro doit être dans la liste des testeurs")
    print("Format: code pays + numéro (sans + ni espaces)")
    print("Exemple Bénin: 22997000000")
    
    to_number = input("\n📱 Entre TON numéro WhatsApp: ")
    
    # Test 1: Template (plus fiable)
    print("\n1️⃣ Test avec template hello_world...")
    test_template_message(to_number)
    
    # Test 2: Message texte direct
    print("\n2️⃣ Test avec message texte...")
    send_test_message(to_number)