import os
import asyncio
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

def main():
    """Lancement du bot Telegram en mode Worker standard"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("Le bot est démarré et aux aguets...")
    
    # Lancement classique en tâche de fond
    application.run_polling(close_loop=False, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
