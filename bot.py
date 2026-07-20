import time
import requests
import sys
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

log("--- MODE DEBUG TOTAL ACTIVE ---")

while True:
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        data = requests.get(url, headers=HEADERS, timeout=10).json()

        for match in data.get("response", []):
            match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
            league_id = match["league"]["id"]
            minute = match["fixture"]["status"]["elapsed"]
            
            # Log de TOUS les matchs trouvés pour comprendre le filtrage
            log(f"SCAN MATCH : {match_name} | LeagueID: {league_id} | Minute: {minute}")

            if league_id in IDS_CHAMPIONNATS and minute >= 75:
                stats = get_stats(match["fixture"]["id"])
                xg_total = sum(float(s.get("value") or 0) for team in stats for s in team.get("statistics", []) if "expected" in str(s.get("type", "")).lower() and "goals" in str(s.get("type", "")).lower())
                
                log(f"DEBUG xG : {match_name} | xG trouvé: {xg_total:.2f}")
                
                s_h, s_a = match["goals"]["home"], match["goals"]["away"]
                if s_h == 0 and s_a == 0: seuil = 1.2
                elif (s_h==1 and s_a==0) or (s_h==0 and s_a==1): seuil = 1.5
                elif s_h == 1 and s_a == 1: seuil = 1.8
                elif (s_h==2 and s_a==0) or (s_h==0 and s_a==2): seuil = 2.0
                elif (s_h==2 and s_a==1) or (s_h==1 and s_a==2): seuil = 2.2
                else: seuil = 2.5
                
                if xg_total >= seuil:
                    bot.send_message(chat_id=CHAT_ID, text=f"🚨 ALERTE xG {minute}' : {match_name} ({s_h}-{s_a}) | Total xG: {xg_total:.2f}")
                    log(f"TELEGRAM ENVOYE : {match_name}")
        
    except Exception as e:
        log(f"Erreur : {e}")
        
    time.sleep(60)
