import os
import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN", "8625843812:AAHbyKLK0R5PrywkG9hBadP87QNXQIxOE5k")

# Liste Blanche des Championnats validée ensemble
CHAMPIONNATS_ALERTE = [
    # Premières divisions (Classique)
    "Ligue 1", "Premier League", "LaLiga", "Serie A", "Bundesliga", 
    "Liga Portugal", "Eredivisie", "Pro League", "Süper Lig", "Super League",
    # Deuxièmes divisions
    "Ligue 2", "Championship", "2. Bundesliga", "LaLiga 2", "Serie B", "Liga Portugal 2",
    # Saison d'été & Coupes
    "MLS", "Série A (Brazil)", "Eliteserien", "Allsvenskan", "J1 League",
    "Champions League", "Europa League", "Conference League"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Message de bienvenue quand on lance le bot"""
    await update.message.reply_text(
        "⚽ Bot Paris Sportifs 'Late Goal' Actif !\n"
        "Je surveille les matchs à partir de la 75e minute selon tes critères."
    )

def main():
    """Lancement du bot Telegram"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Le bot est en cours d'exécution...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
