import logging
import asyncio
import requests
from telegram import Bot

# --- CONFIGURATION ---
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
CHAT_ID = "-1003960057728"
# Clé API et Host
HEADERS = {
    "x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", 
    "x-rapidapi-host": "v3.football.api-sports.io"
}
# Liste des championnats à surveiller
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]

# Configuration des logs pour Render
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
bot = Bot(token=TOKEN)

async def get_stats(fixture_id):
    """Récupère les statistiques détaillées (dont xG) pour un match."""
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", [])
    except Exception as e:
        logging.error(f"Erreur API Stats: {e}")
    return []

async def main():
    # Message de confirmation de lancement
    await bot.send_message(chat_id=CHAT_ID, text="✅ Bot en ligne. Audit et surveillance xG activés.")
    logging.info("Bot démarré avec succès.")
    
    compteur_log = 0
    while True:
        try:
            # Heartbeat dans les logs toutes les heures (60 boucles de 1min)
            compteur_log += 1
            if compteur_log >= 60:
                logging.info("HEARTBEAT: Le bot est toujours en surveillance active.")
                compteur_log = 0

            # Récupération des matchs en live
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            for match in data.get("response", []):
                # Vérification si le championnat est suivi
                if match["league"]["id"] in IDS_CHAMPIONNATS:
                    minute = match["fixture"]["status"]["elapsed"]
                    
                    if minute >= 75:
                        score_home = match["goals"]["home"]
                        score_away = match["goals"]["away"]
                        stats = await get_stats(match["fixture"]["id"])
                        
                        # Calcul du total xG
                        xg_total = 0.0
                        for team in stats:
                            for s in team.get("statistics", []):
                                if s["type"] == "Expected Goals":
                                    xg_total += float(s["value"] or 0)
                        
                        # Logique des seuils dynamiques
                        seuil = 2.0 # Seuil par défaut
                        if score_home == 0 and score_away == 0: seuil = 1.2
                        elif (score_home + score_away) == 1: seuil = 1.5
                        elif (score_home + score_away) == 2 and score_home == 1 and score_away == 1: seuil = 1.8
                        
                        match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                        
                        # Audit dans les logs (visible sur Render Live Tail)
                        if xg_total >= seuil:
                            logging.info(f"ALERTE : {match_name} ({score_home}-{score_away}) - xG {xg_total:.2f} >= seuil {seuil}")
                            await bot.send_message(chat_id=CHAT_ID, text=f"🚨 Alerte xG {minute}' : {match_name} ({score_home}-{score_away}) | Total xG: {xg_total:.2f}")
                        else:
                            logging.info(f"SCAN : {match_name} vu à la {minute}' (xG {xg_total:.2f} < seuil {seuil}).")

        except Exception as e:
            logging.error(f"Erreur dans la boucle principale: {e}")
            
        # Pause d'une minute avant le prochain scan
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
