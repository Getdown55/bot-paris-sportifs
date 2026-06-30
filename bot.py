import asyncio
import requests
import logging
from telegram import Bot

# Configuration
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600" # J'ai utilisé celle de ton premier message
CHAT_ID_CIBLE = "-1003960057728"
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]

bot = Bot(token=TOKEN)

async def get_stats(fixture_id):
    """Appel spécifique pour récupérer les statistiques d'un match"""
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        return data.get("response", [])
    except Exception:
        return []

async def verifier_matchs():
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            response = requests.get(url, headers=HEADERS, timeout=10)
            data = response.json()

            if "response" in data:
                for match in data["response"]:
                    if match["league"]["id"] in IDS_CHAMPIONNATS:
                        fixture_id = match["fixture"]["id"]
                        home = match['teams']['home']['name']
                        away = match['teams']['away']['name']
                        minute = match["fixture"]["status"]["elapsed"] or 0

                        # Appel des stats détaillées
                        stats_data = await get_stats(fixture_id)
                        
                        # Traitement des stats reçues
                        tirs_cadres, tirs_totaux, xg_val = 0, 0, 0.0
                        for team_stats in stats_data:
                            for s in team_stats.get("statistics", []):
                                if s.get("type") == "Shots on Goal": tirs_cadres += int(s.get("value") or 0)
                                if s.get("type") == "Total Shots": tirs_totaux += int(s.get("value") or 0)
                                if s.get("type") == "Expected Goals": xg_val += float(s.get("value") or 0)

                        pression = (tirs_cadres * 0.8) + (tirs_totaux * 0.2) + (xg_val * 2.0)
                        
                        logging.info(f"DEBUG: {home} vs {away} | Minute: {minute} | Pression: {pression:.2f}")

                        if minute >= 75 and pression >= 3.5:
                            await bot.send_message(chat_id=CHAT_ID_CIBLE, text=f"🚨 ALERTE : {home} vs {away} | Pression: {pression:.2f}")

        except Exception as e:
            logging.error(f"Erreur globale : {e}")
        
        await asyncio.sleep(60)

async def main():
    await verifier_matchs()

if __name__ == "__main__":
    asyncio.run(main())
