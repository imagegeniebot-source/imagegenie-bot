# test_bot.py - Simule des commandes utilisateur
import os
from dotenv import load_dotenv
from app import handle_whatsapp_message, init_db

load_dotenv()

# Initialiser la DB
init_db()

# Ton numéro
phone = "22991132843"

print("🧪 TEST DU BOT EN LOCAL")
print("="*50)

# Test des commandes
tests = [
    "/start",
    "/solde", 
    "/image un logo pour restaurant africain",
    "/solde",
    "/aide",
    "/prix"
]

for test in tests:
    print(f"\n📱 Simulation: {test}")
    handle_whatsapp_message(phone, test)
    input("Appuie Enter pour continuer...")