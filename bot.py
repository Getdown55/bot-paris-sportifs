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

IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]
SEUILS_XG = {"0-0": 1.20, "1-0": 1.65, "0-1": 1.65, "1-1": 2.10, "2-1": 2.40, "1-2": 2.40, "2-2": 2.80}
MATCHS_ALERTES = set()

bot = Bot(token=TOKEN)

async def verifier_matchs():
    logging.info("Bot lancé : mode strict avec vérification de type.")
    while True:
        try:
            url_live = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url_live, headers=HEADERS, timeout=10)
            data = response.json()

            if data and "response" in data:
                for match in data["response"]:
                    fixture_id = match["fixture"]["id"]
                    if match["league"]["id"] in IDS_CHAMPIONNATS:
                        
                        url_stats = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
                        resp_stats = requests.get(url_stats, headers=HEADERS, timeout=10)
                        data_stats = resp_stats.json()
                        
                        xg_total = 0.0
                        # Lecture STRICTE : on ne prend que la valeur transmise par l'API
                        if data_stats.get("response"):
                            for team_stats in data_stats["response"]:
                                for s in team_stats.get("statistics", []):
                                    if s.get("type") == "Expected Goals":
                                        val = s.get("value")
                                        # On force la conversion : si ce n'est pas un nombre, ça ne plante pas, ça ignore
                                        try:
                                            xg_total += float(val) if val is not None else 0.0
                                        except (ValueError, TypeError):
                                            continue
                        
                        minute = match["fixture"]["status"]["elapsed"]
                        score = f"{match['goals']['home']}-{match['goals']['away']}"
                        
                        # DEBUG : pour voir ce qui se passe réellement
                        logging.info(f"MATCH: {match['teams']['home']['name']} vs {match['teams']['away']['name']} | Minute: {minute} | Score: {score} | xG Total API: {xg_total}")

                        if 75 <= minute <= 90 and score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                            if str(fixture_id) not in MATCHS_ALERTES:
                                msg = f"🚨 ALERTE : {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n📊 Score : {score} | xG : {xg_total:.2f}"
                                await bot.send_message(chat_id=CHAT_ID_CIBLE, text=msg)
                                MATCHS_ALERTES.add(str(fixture_id))
        except Exception as e:
            logging.error(f"Erreur technique : {e}")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(verifier_matchs())
