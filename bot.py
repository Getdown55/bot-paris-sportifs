import time
import requests
import sys

# On force l'affichage immédiat
def log(message):
    print(message)
    sys.stdout.flush()

log("--- DEMARRAGE DU MOTEUR DE SCAN ---")

while True:
    try:
        log("Scan en cours...")
        # On fait juste un test de connexion simple à l'API
        url = "https://v3.football.api-sports.io/status"
        headers = {"x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", "x-rapidapi-host": "v3.football.api-sports.io"}
        response = requests.get(url, headers=headers, timeout=10)
        
        log(f"Réponse API : {response.status_code}")
        
    except Exception as e:
        log(f"Erreur : {e}")
        
    log("Pause de 60 secondes...")
    time.sleep(60)
