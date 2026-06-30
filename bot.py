import os
import asyncio
import requests
import logging
from telegram import Bot

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = "-1003960057728"
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]

bot = Bot(token=TOKEN)

async def verifier_matchs():
    compteur_minutes = 0
    while True:
        try:
            if compteur_minutes >= 60:
                logging.info("HEARTBEAT: Le bot est toujours en surveillance active.")
                compteur_minutes = 0
            
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            if data and "response" in data:
                for match in data["response"]:
                    if match["league"]["id"] in IDS_CHAMPIONNATS:
                        stats = match.get("statistics", [])
                        tirs_cadres, tirs_totaux, xg_val = 0, 0, 0.0
                        
                        for s in stats:
                            if s.get("type") == "Shots on Goal": tirs_cadres = int(s.get("value") or 0)
                            if s.get("type") == "Total Shots": tirs_totaux = int(s.get("value") or 0)
                            if s.get("type") == "Expected Goals": xg_val = float(s.get("value") or 0)
                        
                        # Calcul de la pression : si xG est absent (0.0), on booste le poids des tirs
                        if xg_val == 0.0:
                            pression_reelle = (tirs_cadres * 0.8) + (tirs_totaux * 0.2)
                        else:
                            pression_reelle = (tirs_cadres * 0.5) + (tirs_totaux * 0.1) + (xg_val * 2.0)
                        
                        home, away = match['teams']['home']['name'], match['teams']['away']['name']
                        logging.info(f"DEBUG: {home} vs {away} | TirsC: {tirs_cadres} | xG: {xg_val} | Pression: {pression_reelle:.2f}")

                        minute = match["fixture"]["status"]["elapsed"] or 0
                        # Seuil : Après 75 min, si la pression >= 3.5, on envoie l'alerte
                        if minute >= 75 and pression_reelle >= 3.5:
                            msg = f"🚨 ALERTE PRESSION : {home} vs {away}\n📊 Score Pression: {pression_reelle:.2f}"
                            await bot.send_message(chat_id=CHAT_ID_CIBLE, text=msg)

            compteur_minutes += 1
        except Exception as e:
            logging.error(f"Erreur : {e}")
        
        await asyncio.sleep(60)

async def main():
    await bot.send_message(chat_id=CHAT_ID_CIBLE, text="✅ Bot en ligne. Calculateur de pression activé.")
    await verifier_matchs()

if __name__ == "__main__":
    asyncio.run(main())
