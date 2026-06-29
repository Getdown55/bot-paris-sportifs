import os
import asyncio
import requests
import logging
from telegram import Bot

# Configuration du log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = "-1003960057728"
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}

bot = Bot(token=TOKEN)

async def demarrage():
    # Envoi du message de confirmation dès le lancement
    try:
        await bot.send_message(chat_id=CHAT_ID_CIBLE, text="✅ Bot actif et en surveillance...")
    except Exception as e:
        logging.error(f"Impossible d'envoyer le message de démarrage : {e}")

async def verifier_matchs():
    logging.info("Le bot est en surveillance...")
    while True:
        try:
            # Ton code de surveillance ici
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Erreur : {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demarrage())
    loop.run_until_complete(verifier_matchs())
