import logging
import asyncio
import requests
from telegram import Bot

# --- CONFIGURATION ---
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
CHAT_ID = "-1003960057728"
HEADERS = {"x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", "x-rapidapi-host": "v3.football.api-sports.io"}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)

async def get_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json().get("response", [])
    except:
        return []

async def main():
    # Message unique de démarrage
    await bot.send_message(chat_id=CHAT_ID, text="✅ Bot en ligne. Surveillance xG activée.")
    
    compteur_log = 0
    while True:
        try:
            # Heartbeat discret dans les logs Render uniquement
            compteur_log += 1
            if compteur_log >= 60:
                logging.info("HEARTBEAT: Le bot est toujours en surveillance active.")
                compteur_log = 0

            url = "https://v3.football.api-sports.io/fixtures?live=all"
            data = requests.get(url, headers=HEADERS, timeout=10).json()

            for match in data.get("response", []):
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    score_home = match["goals"]["home"]
                    score_away = match["goals"]["away"]
                    
                    if minute >= 75:
                        stats = await get_stats(match["fixture"]["id"])
                        xg_total = 0.0
                        for team in stats:
                            for s in team.get("statistics", []):
                                if s["type"] == "Expected Goals":
                                    xg_total += float(s["value"] or 0)
                        
                        # Seuils dynamiques
                        seuil = 2.0 
                        if score_home == 0 and score_away == 0: seuil = 1.2
                        elif (score_home + score_away) == 1: seuil = 1.5
                        elif (score_home + score_away) == 2 and score_home == 1 and score_away == 1: seuil = 1.8
                        
                        if xg_total >= seuil:
                            await bot.send_message(chat_id=CHAT_ID, text=f"🚨 Alerte xG {minute}' : {match['teams']['home']['name']} {score_home}-{score_away} {match['teams']['away']['name']} | Total xG: {xg_total:.2f}")

        except Exception as e:
            logging.error(f"Erreur : {e}")
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
