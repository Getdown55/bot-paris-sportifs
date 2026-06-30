import logging
import asyncio
from telegram import Bot

# Configure les logs pour qu'ils soient très verbeux
logging.basicConfig(level=logging.INFO)

async def main():
    logging.info("--- DÉBUT DU SCRIPT ---")
    try:
        token = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
        bot = Bot(token=token)
        await bot.send_message(chat_id="-1003960057728", text="Test de démarrage réussi !")
        logging.info("Message de test envoyé avec succès !")
    except Exception as e:
        logging.error(f"ERREUR CRITIQUE : {e}")

if __name__ == "__main__":
    asyncio.run(main())
