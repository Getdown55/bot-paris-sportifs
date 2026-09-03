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

# URL GOOGLE APPS SCRIPT
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzz3kxJX8Gft52CKpLjs2iMvFXgQKb-0cX2SiWBc2w1eZa64XdAW4MmpqKMSGzVNRZ-/exec"

bot = Bot(token=TOKEN)

def send_to_google_sheet(match_name, score, xg_total):
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
        if response.status_code == 200:
            return response.json().get("response", [])
        else:
            log(f"Erreur API Stats HTTP {response.status_code}")
            return []
    except Exception as e:
        log(f"Exception get_stats : {e}")
        return []

def extract_xg(stats_data):
    total_xg = 0.0
    for team in stats_data:
        for stat in team.get("statistics", []):
            type_name = str(stat.get("type") or "").lower().strip()
            if "expected" in type_name or "xg" in type_name:
                val = stat.get("value")
                if val is not None and val != "":
                    try:
                        total_xg += float(val)
                    except ValueError:
                        pass
    return total_xg

async def send_telegram(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
        log(f"TELEGRAM ENVOYE : {text[:30]}...")
    except Exception as e:
        log(f"Erreur d'envoi Telegram : {e}")

async def main():
    log("--- INITIALISATION DU BOT (TELEGRAM + GOOGLE SHEET INTEGRAL) ---")
    
    matchs_suivis = {}

    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code != 200:
                log(f"Erreur API Live HTTP {response.status_code}: {response.text[:100]}")
                await asyncio.sleep(60)
                continue

            data = response.json()
            matchs_presents = data.get("response", [])
            
            log(f"[{time.strftime('%H:%M:%S')}] Scan effectue : {len(matchs_presents)} match(s) en direct.")

            for match in matchs_presents:
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    fixture_id = match["fixture"]["id"]
                    
                    if minute is not None and minute >= 75:
                        s_h, s_a = match["goals"]["home"], match["goals"]["away"]
                        score_str = f"{s_h}-{s_a}"
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"

                        # DETERMINATION DU SEUIL XG DE BASE
                        if s_h == 0 and s_a == 0: seuil = 1.2
                        elif (s_h==1 and s_a==0) or (s_h==0 and s_a==1): seuil = 1.5
                        elif s_h == 1 and s_a == 1: seuil = 1.8
                        elif (s_h==2 and s_a==0) or (s_h==0 and s_a==2): seuil = 2.0
                        elif (s_h==2 and s_a==1) or (s_h==1 and s_a==2): seuil = 2.2
                        else: seuil = 2.5

                        # CAS 1 : PREMIER SCAN APRES 75 MINUTE
                        if fixture_id not in matchs_suivis:
                            stats = get_stats(fixture_id)
                            xg_total = round(extract_xg(stats), 2)

                            if xg_total >= seuil:
                                log(f"SCAN 75' : {match_name} ({score_str}) | xG: {xg_total:.2f}")

                                send_to_google_sheet(f"{match_name} ({minute}')", score_str, xg_total)
                                await send_telegram(f"🚨 ALERTE xG {minute}' : {match_name} ({score_str}) | Total xG: {xg_total:.2f}")

                                matchs_suivis[fixture_id] = {'score': score_str, 'xg': xg_total}

                        # CAS 2 : SUIVI DES EVOLUTIONS (BUT OU +0.25 xG)
                        else:
                            dernier_etat = matchs_suivis[fixture_id]
                            score_change = (score_str != dernier_etat['score'])

                            stats = get_stats(fixture_id)
                            xg_actuel = round(extract_xg(stats), 2)
                            xg_increase = (xg_actuel - dernier_etat['xg']) >= 0.25

                            if score_change or xg_increase:
                                raison = "⚽ GOAL" if score_change else "📈 HAUSSE xG"
                                log(f"EVOLUTION {minute}' ({raison}) : {match_name} ({score_str}) | xG: {xg_actuel:.2f}")

                                send_to_google_sheet(f"{match_name} ({minute}')", score_str, xg_actuel)
                                await send_telegram(f"🔄 EVOLUTION {minute}' ({raison}) : {match_name} ({score_str}) | Total xG: {xg_actuel:.2f}")

                                matchs_suivis[fixture_id] = {'score': score_str, 'xg': xg_actuel}
            
        except Exception as e:
            log(f"Erreur globale de scan : {e}")
            
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
