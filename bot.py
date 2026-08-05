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

# METS TON URL GOOGLE APPS SCRIPT ICI
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/TON_SCRIPT_ID/exec"

bot = Bot(token=TOKEN)

def send_to_google_sheet(match_name, score, xg_total):
    if "TON_SCRIPT_ID" in SHEET_WEBAPP_URL:
        return # Ignore si l'URL n'est pas encore configurée
    payload = {
        "match": match_name,
        "score": score,
        "xg": xg_total
    }
    try:
        requests.post(SHEET_WEBAPP_URL, json=payload, timeout=5)
        log(f"SHEET ENVOYE : {match_name}")
    except Exception as e:
        log(f"Erreur d'envoi Google Sheet : {e}")

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
    log("--- INITIALISATION DU BOT (TELEGRAM + GOOGLE SHEET INTEGRAL) ---")
    
    matchs_enregistres = set()  # Pour éviter d'enregistrer le même match plusieurs fois

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
                    fixture_id = match["fixture"]["id"]
                    
                    if minute >= 75 and fixture_id not in matchs_enregistres:
                        stats = get_stats(fixture_id)
                        xg_total = sum(float(s.get("value") or 0) for team in stats for s in team.get("statistics", []) if "expected" in str(s.get("type", "")).lower() and "goals" in str(s.get("type", "")).lower())
                        
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                        s_h, s_a = match["goals"]["home"], match["goals"]["away"]
                        score_str = f"{s_h}-{s_a}"

                        log(f"SCAN 75' : {match_name} ({score_str}) | xG: {xg_total:.2f}")

                        # 1. ENREGISTREMENT SYSTEMATIQUE DANS GOOGLE SHEET (TOUS LES MATCHS)
                        send_to_google_sheet(match_name, score_str, round(xg_total, 2))
                        matchs_enregistres.add(fixture_id)

                        # 2. SEUILS POUR TELEGRAM
                        if s_h == 0 and s_a == 0: seuil = 1.2
                        elif (s_h==1 and s_a==0) or (s_h==0 and s_a==1): seuil = 1.5
                        elif s_h == 1 and s_a == 1: seuil = 1.8
                        elif (s_h==2 and s_a==0) or (s_h==0 and s_a==2): seuil = 2.0
                        elif (s_h==2 and s_a==1) or (s_h==1 and s_a==2): seuil = 2.2
                        else: seuil = 2.5
                        
                        # ALERTE TELEGRAM SEULEMENT SI LE SEUIL EST DEPASSE
                        if xg_total >= seuil:
                            await send_telegram(f"🚨 ALERTE xG {minute}' : {match_name} ({score_str}) | Total xG: {xg_total:.2f}")
            
        except Exception as e:
            log(f"Erreur de scan : {e}")
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
