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

# --- TEST TELEGRAM IMMEDIAT AU DEMARRAGE ---
try:
    bot.send_message(chat_id=CHAT_ID, text="✅ Test de connexion : Le bot communique parfaitement avec Telegram !")
    log("TELEGRAM : Message de test envoyé avec succès.")
except Exception as e:
    log(f"TELEGRAM : Échec du test -> {e}")

log("--- BOT EN ATTENTE DE REACTIVATION DE L'API ---")

while True:
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        data = requests.get(url, headers=HEADERS, timeout=10).json()

        matchs_presents = data.get("response", [])
        if not matchs_presents:
            log("Aucun match en direct (quota API probablement dépassé).")
            
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
                        bot.send_message(chat_id=CHAT_ID, text=f"🚨 ALERTE xG {minute}' : {match_name} ({s_h}-{s_a}) | Total xG: {xg_total:.2f}")
                        log(f"TELEGRAM ENVOYE : {match_name}")
        
    except Exception as e:
        log(f"Erreur de scan : {e}")
        
    time.sleep(60)
