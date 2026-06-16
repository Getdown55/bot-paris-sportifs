import os
import asyncio
import requests
from telegram import Bot # Import spécifique pour l'envoi manuel

# CONFIGURATION
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = os.environ.get("CHAT_ID_CIBLE", "-1003960057728")

IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]
SEUILS_XG = {"0-0": 1.20, "1-0": 1.65, "0-1": 1.65, "1-1": 2.10, "2-1": 2.40, "1-2": 2.40, "2-2": 2.80}
MATCHS_ALERTES = set()

# Fonction de récupération (ta logique)
def recuperer_matchs_en_direct():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return response.json() if response.status_code == 200 else None
    except: return None

# La patrouille
async def verifier_matchs_et_alerter(bot):
    while True:
        data = recuperer_matchs_en_direct()
        if data and "response" in data:
            for match in data["response"]:
                if match.get("league", {}).get("id") in IDS_CHAMPIONNATS:
                    # (Ton code de logique reste ici)
                    pass
        await asyncio.sleep(60)

# Lancement propre
async def main():
    bot = Bot(token=TOKEN)
    # Envoi du message de démarrage une seule fois
    await bot.send_message(chat_id=CHAT_ID_CIBLE, text="✅ Bot opérationnel : Patrouille lancée !")
    
    # Lancement de la boucle de patrouille
    await verifier_matchs_et_alerter(bot)

if __name__ == "__main__":
    asyncio.run(main())
