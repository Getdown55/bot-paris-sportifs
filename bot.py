import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration - Ton vrai token est directement intégré ici
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
        # Désactive les logs de requêtes pour ne pas polluer la console
        return

def run_health_server():
    """Lance le serveur web obligatoire pour Render sur le port demandé"""
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Serveur de contrôle activé sur le port {port}")
    server.serve_forever()

def main():
    """Lancement du bot Telegram compatible avec le plan Free de Render"""
    # 1. On lance le mini-serveur web dans un fil secondaire (thread)
    threading.Thread(target=run_health_server, daemon=True).start()

    # 2. On lance le bot Telegram avec ton token
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Le bot est démarré et aux aguets...")
    application.run_polling(close_loop=False, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
