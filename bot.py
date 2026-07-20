import time
import requests
import sys

def log(message):
    print(message)
    sys.stdout.flush()

HEADERS = {"x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", "x-rapidapi-host": "v3.football.api-sports.io"}

log("--- MODE DEBUG : LISTAGE DE TOUS LES MATCHS EN COURS ---")

while True:
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        data = requests.get(url, headers=HEADERS, timeout=10).json()

        if not data.get("response"):
            log("Aucun match en direct détecté par l'API.")
        else:
            for match in data.get("response", []):
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                league_id = match["league"]["id"]
                log(f"MATCH TROUVE : {home} vs {away} | ID Ligue : {league_id}")
        
    except Exception as e:
        log(f"Erreur : {e}")
        
    time.sleep(60)
