import os
import asyncio
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN", "8625...") # Ton token reste bien en place ici

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

def lance_serveur_factice():
    """Crée un mini-serveur web pour empêcher Render de couper le bot"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Bot en cours d'execution...")

    port = int(os.environ.get("PORT", 8000))
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        print(f"Serveur factice activé sur le port {port}")
        httpd.serve_forever()

def main():
    """Lancement du bot Telegram de manière compatible avec Render"""
    # On lance le serveur factice en arrière-plan pour faire plaisir à Render
    threading.Thread(target=lance_serveur_factice, daemon=True).start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Le bot est démarré et aux aguets...")
    
    # run_polling géré correctement pour éviter le crash
    application.run_polling(close_loop=False, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
