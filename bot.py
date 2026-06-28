import os
import asyncio
import requests
import time
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = os.environ.get("CHAT_ID_CIBLE", "-1003960057728")

# Liste élargie des championnats (assure-toi que l'ID de la compétition est dedans)
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]
# Seuils abaissés de 0.10 pour être plus réactif
SEUILS_XG = {"0-0": 1.10, "1-0": 1.55, "0-1": 1.55, "1-1": 2.00, "2-1": 2.30, "1-2": 2.30, "2-2": 2.70}
MATCHS_ALERTES = set()

bot = Bot(token=TOKEN)

async def verifier_matchs():
    logging.info("Patrouille lancée en MODE DÉTECTIVE.")
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if data and "response" in data:
                for match in data["response"]:
                    # DÉTECTIVE : On logue chaque match surveillé
                    home = match['teams']['home']['name']
                    away = match['teams']['away']['name']
                    league_id = match.get("league", {}).get("id")
                    
                    if league_id in IDS_CHAMPIONNATS:
                        minute = match.get("fixture", {}).get("status", {}).get("elapsed")
                        if minute is None: continue
                        
                        stats = match.get("statistics", [])
                        xg_api = 0.0
                        for s in stats:
                            if s.get("type") == "Expected Goals":
                                xg_api = float(s.get("home", 0) or 0) + float(s.get("away", 0) or 0)
                        
                        # DÉTECTIVE : Log pour voir ce que le bot calcule réellement
                        logging.info(f"Analyse: {home} vs {away} | Minute: {minute} | xG calculé: {xg_api}")

                        if 75 <= int(minute) <= 90:
                            score = f"{match['goals']['home']}-{match['goals']['away']}"
                            if score in SEUILS_XG and xg_api >= SEUILS_XG[score]:
                                if str(match['fixture']['id']) not in MATCHS_ALERTES:
                                    msg = f"🚨 ALERTE : {home} vs {away}\n📊 Score : {score} | xG : {xg_api:.2f}"
                                    await bot.send_message(chat_id=CHAT_ID_CIBLE, text=msg)
                                    MATCHS_ALERTES.add(str(match['fixture']['id']))
        except Exception as e:
            logging.error(f"Erreur boucle : {e}")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(verifier_matchs())
