import os
import asyncio
import requests
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = os.environ.get("CHAT_ID_CIBLE", "-1003960057728")
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}

# ID des championnats surveillés
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]
SEUILS_XG = {"0-0": 1.20, "1-0": 1.65, "0-1": 1.65, "1-1": 2.10, "2-1": 2.40, "1-2": 2.40, "2-2": 2.80}

bot = Bot(token=TOKEN)

async def verifier_matchs():
    logging.info("Le bot est toujours actif et en surveillance...")
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            if data and "response" in data:
                for match in data["response"]:
                    # Vérification du championnat
                    if match["league"]["id"] in IDS_CHAMPIONNATS:
                        # Extraction des données en toute sécurité
                        xg_val = 0.0
                        stats = match.get("statistics", [])
                        for s in stats:
                            if s.get("type") == "Expected Goals":
                                xg_val = float(s.get("value") or 0)
                        
                        minute = match["fixture"]["status"]["elapsed"]
                        score = f"{match['goals']['home']}-{match['goals']['away']}"
                        
                        # Vérification des seuils
                        if minute >= 75 and score in SEUILS_XG:
                            if xg_val >= SEUILS_XG[score]:
                                # Envoi alerte
                                await bot.send_message(chat_id=CHAT_ID_CIBLE, text=f"Alerte : {match['teams']['home']['name']} vs {match['teams']['away']['name']} | xG: {xg_val}")
        
        except Exception as e:
            logging.error(f"Erreur rencontrée : {e}")
        
        await asyncio.sleep(60) # Pause de 1 minute

if __name__ == "__main__":
    asyncio.run(verifier_matchs())
