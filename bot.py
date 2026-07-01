
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

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
bot = Bot(token=TOKEN)

async def get_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json().get("response", [])
    except:
        return []

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="✅ Bot en ligne. Correction xG appliquée.")
    
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            data = requests.get(url, headers=HEADERS, timeout=10).json()

            for match in data.get("response", []):
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    if minute >= 75:
                        stats = await get_stats(match["fixture"]["id"])
                        xg_total = 0.0
                        
                        # CORRECTION ICI : On cherche les deux formats possibles
                        for team in stats:
                            for s in team.get("statistics", []):
                                type_stat = str(s.get("type", "")).lower()
                                if "expected" in type_stat and "goals" in type_stat:
                                    xg_total += float(s.get("value") or 0)
                        
                        score_h = match["goals"]["home"]
                        score_a = match["goals"]["away"]
                        seuil = 1.2 if (score_h+score_a)==0 else (1.5 if (score_h+score_a)==1 else 1.8)
                        
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                        
                        if xg_total >= seuil:
                            await bot.send_message(chat_id=CHAT_ID, text=f"🚨 ALERTE xG {minute}' : {match_name} | Total xG: {xg_total:.2f}")
                        
                        logging.info(f"SCAN : {match_name} | xG calculé : {xg_total:.2f} (Seuil: {seuil})")

        except Exception as e:
            logging.error(f"Erreur : {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
