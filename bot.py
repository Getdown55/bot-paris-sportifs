import time
import requests
import sys

def log(message):
    print(message)
    sys.stdout.flush()

HEADERS = {"x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", "x-rapidapi-host": "v3.football.api-sports.io"}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1, 283]

log("--- SCAN DES MATCHS ACTIVE ---")

while True:
    try:
        url = "https://v3.football.api-sports.io/fixtures?live=all"
        data = requests.get(url, headers=HEADERS, timeout=10).json()
        
        matchs_trouves = 0
        for match in data.get("response", []):
            if match["league"]["id"] in IDS_CHAMPIONNATS:
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                log(f"Match trouvé : {home} vs {away}")
                matchs_trouves += 1
        
        if matchs_trouves == 0:
            log("Aucun match en direct dans les championnats suivis.")
            
    except Exception as e:
        log(f"Erreur de scan : {e}")
        
    time.sleep(60)
