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

IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]
SEUILS_XG = {"0-0": 1.20, "1-0": 1.65, "0-1": 1.65, "1-1": 2.10, "2-1": 2.40, "1-2": 2.40, "2-2": 2.80}
MATCHS_ALERTES = set()

bot = Bot(token=TOKEN)

def recuperer_matchs_en_direct():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logging.error(f"Erreur API : {e}")
        return None

async def verifier_matchs():
    global MATCHS_ALERTES
    logging.info("Patrouille lancée avec sécurité renforcée.")
    derniere_fois_vie = time.time()
    
    while True:
        if time.time() - derniere_fois_vie >= 3600:
            logging.info("Le bot est toujours actif et en surveillance...")
            derniere_fois_vie = time.time()

        data = recuperer_matchs_en_direct()
        if data and "response" in data:
            for match in data["response"]:
                # Sécurité : on vérifie que les données de base existent
                league_id = match.get("league", {}).get("id")
                if league_id not in IDS_CHAMPIONNATS:
                    continue
                
                fixture_id = str(match.get("fixture", {}).get("id"))
                minute = match.get("fixture", {}).get("status", {}).get("elapsed")
                
                # Protection contre le plantage : si minute est None, on passe au match suivant
                if minute is None:
                    continue
                
                goals = match.get("goals", {})
                score = f"{goals.get('home', 0)}-{goals.get('away', 0)}"
                
                if 75 <= int(minute) <= 90 and fixture_id not in MATCHS_ALERTES:
                    stats = match.get("statistics", [])
                    # On sécurise aussi le calcul des stats
                    xg_api = 0.0
                    tirs_cadres = 0
                    for s in stats:
                        if s.get("type") == "Expected Goals":
                            xg_api = float(s.get("home", 0) or 0) + float(s.get("away", 0) or 0)
                        if s.get("type") == "Shots on Goal":
                            tirs_cadres = int(s.get("home", 0) or 0) + int(s.get("away", 0) or 0)
                            
                    xg_total = max(xg_api, tirs_cadres * 0.20)
                    
                    if score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                        msg = f"🚨 {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n📊 Score : {score} | xG : {xg_total:.2f}"
                        try:
                            await bot.send_message(chat_id=CHAT_ID_CIBLE, text=msg)
                            MATCHS_ALERTES.add(fixture_id)
                        except Exception as e:
                            logging.error(f"Erreur envoi Telegram : {e}")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(bot.send_message(chat_id=CHAT_ID_CIBLE, text="🚨 Bot redémarré et opérationnel !"))
    except: pass
    asyncio.run(verifier_matchs())
