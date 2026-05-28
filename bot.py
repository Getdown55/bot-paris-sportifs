import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration - Ton token est en place
TOKEN = "8625843812:AAHbyKLK0R5PrywkG9hBadP87QNXQIxOE5k"

# Liste Blanche des Championnats validés
CHAMPIONNATS_ALERTE = [
    "Ligue 1", "Premier League", "LaLiga", "Serie A", "Bundesliga",
    "Liga Portugal", "Eredivisie", "Pro League", "Süper Lig", "Super League",
    "Ligue 2", "Championship", "2. Bundesliga", "LaLiga 2", "Serie B", "Liga Portugal 2",
    "MLS", "Série A (Brazil)", "Eliteserien", "Allsvenskan", "J1 League",
    "Champions League", "Europa League", "Conference League"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue quand on tape /start"""
    await update.message.reply_text(
        "⚽ Bot Paris Sportifs 'Late Value' activé !\n"
        "Je surveille les matchs à forte valeur pour toi."
    )

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Répond aux pings de Render pour lui dire que le bot va bien"""
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
        
    def log_message(self, format, *args):
        return

def run_health_server():
    """Lance le serveur web obligatoire pour Render"""
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

async def start_bot():
    """Initialise et lance le bot dans la boucle asynchrone principale"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # Initialisation moderne requise par les dernières versions
    await application.initialize()
    await application.start()
    
    print("Le bot est démarré et aux aguets...")
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Maintient le bot en vie indéfiniment
    while True:
        await asyncio.sleep(3600)

def main():
    # 1. Lance le serveur web de Render en arrière-plan
    threading.Thread(target=run_health_server, daemon=True).start()

    # 2. Crée et exécute proprement la boucle asynchrone pour le bot Telegram
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == '__main__':
    main()
