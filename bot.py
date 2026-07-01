import logging
import asyncio
import requests
from telegram import Bot

# --- CONFIGURATION ---
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
CHAT_ID = "-1003960057728"
HEADERS = {
    "x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", 
    "x-rapidapi-host": "v3.football.api-sports.io"
}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
bot = Bot(token=TOKEN)

async def get_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        logging.error(f"Erreur API Stats pour match {fixture_id}: {e}")
    return []

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="✅ Bot en ligne. Mode audit xG et debug activé.")
    logging.info("--- DÉBUT DU SCRIPT ---")
    
    compteur_log = 0
    while True:
        try:
            compteur_log += 1
            if compteur_log >= 60:
                logging.info("HEARTBEAT: Le bot est toujours en surveillance active.")
                compteur_log = 0

            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            for match in data.get("response", []):
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    
                    if minute >= 75:
                        score_home = match["goals"]["home"]
                        score_away = match["goals"]["away"]
                        stats = await get_stats(match["fixture"]["id"])
                        
                        xg_total = 0.0
                        found_xg = False
                        
                        # Debug : Si stats reçues mais pas de xG, on affiche tout pour comprendre
                        for team in stats:
                            for s in team.get("statistics", []):
                                if s["type"] == "Expected Goals":
                                    xg_total += float(s["value"] or 0)
                                    found_xg = True
                        
                        # Ajout debug : si xG est 0, on log les stats brutes pour vérifier l'API
                        if not found_xg and stats:
                            logging.info(f"DEBUG: Aucune donnée xG trouvée pour {match['teams']['home']['name']} vs {match['teams']['away']['name']}. Stats reçues: {stats}")
                        
                        seuil = 2.0 
                        if score_home == 0 and score_away == 0: seuil = 1.2
                        elif (score_home + score_away) == 1: seuil = 1.5
                        elif (score_home + score_away) == 2 and score_home == 1 and score_away == 1: seuil = 1.8
                        
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                        
                        if xg_total >= seuil:
                            logging.info(f"ALERTE : {match_name} ({score_home}-{score_away}) - xG {xg_total:.2f} >= seuil {seuil}")
                            await bot.send_message(chat_id=CHAT_ID, text=f"🚨 Alerte xG {minute}' : {match_name} ({score_home}-{score_away}) | Total xG: {xg_total:.2f}")
                        else:
                            logging.info(f"SCAN : {match_name} vu à la {minute}' (xG {xg_total:.2f} < seuil {seuil}).")

        except Exception as e:
            logging.error(f"Erreur critique dans la boucle: {e}")
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
