import logging
import asyncio
import requests
from telegram import Bot

# --- CONFIGURATION ---
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
CHAT_ID = "-1003960057728"
URL_SHEET = "TON_LIEN_APRES_DEPLOIEMENT" 

HEADERS = {
    "x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", 
    "x-rapidapi-host": "v3.football.api-sports.io"
}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
bot = Bot(token=TOKEN)

def envoyer_vers_sheets(match_name, score, xg_total):
    try:
        requests.post(URL_SHEET, json={"match": match_name, "score": score, "xg": xg_total}, timeout=20)
    except:
        pass 

async def get_stats(fixture_id):
    try:
        response = requests.get(f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}", headers=HEADERS, timeout=20)
        return response.json().get("response", [])
    except:
        return []

async def main():
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            data = requests.get(url, headers=HEADERS, timeout=20).json()

            for match in data.get("response", []):
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    if minute >= 75:
                        stats = await get_stats(match["fixture"]["id"])
                        xg_total = sum(float(s.get("value") or 0) for team in stats for s in team.get("statistics", []) if "expected" in str(s.get("type", "")).lower())
                        
                        s_h, s_a = match["goals"]["home"], match["goals"]["away"]
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                        
                        # ENVOI SYSTÉMATIQUE AU TABLEAU (ça, c'est le changement)
                        envoyer_vers_sheets(match_name, f"{s_h}-{s_a}", f"{xg_total:.2f}")
                        
                        # TES SEUILS ORIGINAUX (j'ai remis tes conditions exactes)
                        if s_h == 0 and s_a == 0: seuil = 1.2
                        elif (s_h == 1 and s_a == 0) or (s_h == 0 and s_a == 1): seuil = 1.5
                        elif s_h == 1 and s_a == 1: seuil = 1.8
                        elif (s_h == 2 and s_a == 0) or (s_h == 0 and s_a == 2): seuil = 2.0
                        elif (s_h == 2 and s_a == 1) or (s_h == 1 and s_a == 2): seuil = 2.2
                        elif s_h == 2 and s_a == 2: seuil = 2.5
                        else: seuil = 2.5
                        
                        if xg_total >= seuil:
                            await bot.send_message(chat_id=CHAT_ID, text=f"🚨 ALERTE xG {minute}' : {match_name} ({s_h}-{s_a}) | Total xG: {xg_total:.2f}")
                        
                        logging.info(f"SCAN : {match_name} ({s_h}-{s_a}) | xG calculé : {xg_total:.2f} (Seuil: {seuil})")
        except:
            pass
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
