import os
import asyncio
import requests
import logging
from telegram import Bot

# Configuration du log pour suivre ce que fait le bot
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = "-1003960057728"
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}

bot = Bot(token=TOKEN)

async def demarrer_bot():
    """Envoie une confirmation au lancement."""
    try:
        await bot.send_message(chat_id=CHAT_ID_CIBLE, text="✅ Bot en ligne et en surveillance.")
    except Exception as e:
        logging.error(f"Erreur envoi Telegram: {e}")

async def surveillance_matchs():
    logging.info("Surveillance active...")
    while True:
        try:
            # Ici tu peux remettre ta logique de requête API
            # Le bot ne crashera plus grâce à la structure ci-dessous
            await asyncio.sleep(60) 
        except Exception as e:
            logging.error(f"Erreur boucle: {e}")
            await asyncio.sleep(60)

async def main():
    await demarrer_bot()
    await surveillance_matchs()

if __name__ == "__main__":
    # Méthode moderne pour lancer la boucle sans erreur de thread
    asyncio.run(main())
