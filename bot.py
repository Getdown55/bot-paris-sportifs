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

HEADERS = {
    "x-apisports-key": "Fd062d2a521ed65d8c0944cc4a373600"
}

IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1, 283]
SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbzz3kxJX8Gft52CKpLjs2iMvFXgQKb-0cX2SiWBc2w1eZa64XdAW4MmpqKMSGzVNRZ-/exec"

bot = Bot(token=TOKEN)

native_xg_alert_sent = False

def send_to_google_sheet(match_name, score, xg_total):
    payload = {"match": match_name, "score": score, "xg": xg_total}
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

def extract_native_xg(stats_data):
    """ Extrait STRICTEMENT le xG natif d'API-Football. Renvoie None si absent. """
    if not stats_data:
        return None

    total_xg = 0.0
    found = False

    for team in stats_data:
        for stat in team.get("statistics", []):
            type_name = str(stat.get("type") or "").strip().lower()
            if "expected" in type_name or "xg" in type_name:
                val = stat.get("value")
                if val is not None and val != "":
                    try:
                        val_str = str(val).replace(",", ".").replace("%", "").strip()
                        total_xg += float(val_str)
                        found = True
                    except (ValueError, TypeError):
                        pass

    return round(total_xg, 2) if found else None

async def send_telegram(text):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text)
        log(f"TELEGRAM ENVOYE : {text[:30]}...")
    except Exception as e:
        log(f"Erreur d'envoi Telegram : {e}")

async def main():
    global native_xg_alert_sent
    log("--- BOT EN VEILLE PASSIVE (ATTENTE RETOUR XG NATIF API-FOOTBALL) ---")
    matchs_suivis = {}

    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code != 200:
                log(f"Erreur API Live HTTP {response.status_code}")
                await asyncio.sleep(60)
                continue

            data = response.json()
            matchs_presents = data.get("response", [])
            log(f"[{time.strftime('%H:%M:%S')}] Scan effectué : {len(matchs_presents)} match(s) en direct.")

            for match in matchs_presents:
                try:
                    league_id = match.get("league", {}).get("id")
                    if league_id in IDS_CHAMPIONNATS:
                        fixture = match.get("fixture", {})
                        minute = fixture.get("status", {}).get("elapsed")
                        fixture_id = fixture.get("id")
                        
                        goals = match.get("goals", {})
                        s_h = goals.get("home") if goals.get("home") is not None else 0
                        s_a = goals.get("away") if goals.get("away") is not None else 0
                        score_str = f"{s_h}-{s_a}"
                        
                        teams = match.get("teams", {})
                        home_name = teams.get("home", {}).get("name", "Domicile")
                        away_name = teams.get("away", {}).get("name", "Exterieur")
                        match_name = f"{home_name} vs {away_name}"

                        if minute is None or minute < 75:
                            continue

                        # Extraction stricte des xG officiels
                        stats = get_stats(fixture_id)
                        native_xg = extract_native_xg(stats)

                        if native_xg is None:
                            log(f"⏳ [VEILLE 75'] {match_name} ({score_str}) | xG natif toujours absent du flux API.")
                            continue

                        # Si le xG natif reparaît enfin :
                        if not native_xg_alert_sent:
                            await send_telegram("ℹ️ **INFO API** : Le flux xG natif officiel d'API-Football est de retour ! Reprise des alertes.")
                            native_xg_alert_sent = True

                        # SEUILS
                        if s_h == 0 and s_a == 0: seuil = 1.2
                        elif (s_h==1 and s_a==0) or (s_h==0 and s_a==1): seuil = 1.5
                        elif s_h == 1 and s_a == 1: seuil = 1.8
                        elif (s_h==2 and s_a==0) or (s_h==0 and s_a==2): seuil = 2.0
                        elif (s_h==2 and s_a==1) or (s_h==1 and s_a==2): seuil = 2.2
                        else: seuil = 2.5

                        log(f"📊 [ANALYSE 75'] {match_name} ({score_str}) | xG Natif: {native_xg} | Seuil: {seuil}")

                        if fixture_id not in matchs_suivis:
                            if native_xg >= seuil:
                                log(f"🚨 DECLENCHEMENT ALERTE NATIF : {match_name}")
                                send_to_google_sheet(f"{match_name} ({minute}')", score_str, native_xg)
                                await send_telegram(f"🚨 ALERTE xG {minute}' : {match_name} ({score_str}) | xG Natif: {native_xg:.2f}")
                                matchs_suivis[fixture_id] = {'score': score_str, 'xg': native_xg}

                except Exception as e_match:
                    log(f"Erreur traitement match : {e_match}")
                    continue

        except Exception as e:
            log(f"Erreur globale : {e}")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
