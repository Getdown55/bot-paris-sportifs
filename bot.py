import time
import requests
import sys
import asyncio
from telegram import Bot

def log(message):
    print(message)
    sys.stdout.flush()

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
CHAT_ID = "-1003960057728"
HEADERS = {"x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", "x-rapidapi-host": "v3.football.api-sports.io"}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1, 283]

bot = Bot(token=TOKEN)

def get_stats(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json().get("response", [])
    except:
        return []

async def send_telegram(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
        log(f"TELEGRAM ENVOYE : {text[:30]}...")
    except Exception as e:
        log(f"Erreur d'envoi Telegram : {e}")

async def main():
    log("--- INITIALISATION DU BOT (MODE ASYNC) ---")
    
    # Test immédiat au démarrage
    await send_telegram("✅ Test de connexion : Le bot communique parfaitement avec Telegram !")
    
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            data = requests.get(url, headers=HEADERS, timeout=10).json()

            matchs_presents = data.get("response", [])
            if not matchs_presents:
                log("Aucun match en direct (quota API probablement dépassé ou aucun match en cours).")
                
            for match in matchs_presents:
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    if minute >= 75:
                        stats = get_stats(match["fixture"]["id"])
                        xg_total = sum(float(s.get("value") or 0) for team in stats for s in team.get("statistics", []) if "expected" in str(s.get("type", "")).lower() and "goals" in str(s.get("type", "")).lower())
                        
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                        log(f"SCAN : {match_name} ({minute}') | xG: {xg_total:.2f}")
                        
                        s_h, s_a = match["goals"]["home"], match["goals"]["away"]
                        
                        if s_h == 0 and s_a == 0: seuil = 1.2
                        elif (s_h==1 and s_a==0) or (s_h==0 and s_a==1): seuil = 1.5
                        elif s_h == 1 and s_a == 1: seuil = 1.8
                        elif (s_h==2 and s_a==0) or (s_h==0 and s_a==2): seuil = 2.0
                        elif (s_h==2 and s_a==1) or (s_h==1 and s_a==2): seuil = 2.2
                        else: seuil = 2.5
                        
                        if xg_total >= seuil:
                            await send_telegram(f"🚨 ALERTE xG {minute}' : {match_name} ({s_h}-{s_a}) | Total xG: {xg_total:.2f}")
            
        except Exception as e:
            log(f"Erreur de scan : {e}")
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
