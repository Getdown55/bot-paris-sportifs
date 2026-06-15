import os
import asyncio
import requests
from telegram.ext import Application

# ==========================================
# CONFIGURATION
# ==========================================
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = os.environ.get("CHAT_ID_CIBLE", "-1003960057728")

IDS_CHAMPIONNATS = [39, 61, 140, 135, 78, 94, 88, 144, 203, 119, 40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1]
SEUILS_XG = {"0-0": 1.20, "1-0": 1.65, "0-1": 1.65, "1-1": 2.10, "2-1": 2.40, "1-2": 2.40, "2-2": 2.80}
MATCHS_ALERTES = set()

# ==========================================
# FONCTIONS
# ==========================================
def recuperer_matchs_en_direct():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

async def lancer_serveur_web_async():
    port = int(os.environ.get("PORT", 10000))
    async def handle(reader, writer):
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nBot en ligne")
        await writer.drain()
        writer.close()
    server = await asyncio.start_server(handle, "0.0.0.0", port)
    print(f"Serveur Web actif sur port {port}")
    async with server: await server.serve_forever()

async def verifier_matchs_et_alerter(application):
    global MATCHS_ALERTES
    print("Patrouille lancée avec logique de secours activée.")
    while True:
        data = recuperer_matchs_en_direct()
        if data and "response" in data:
            for match in data["response"]:
                if match.get("league", {}).get("id") in IDS_CHAMPIONNATS:
                    fixture_id = str(match.get("fixture", {}).get("id"))
                    minute = match.get("fixture", {}).get("status", {}).get("elapsed", 0)
                    score = f"{match['goals']['home']}-{match['goals']['away']}"
                    
                    if 75 <= minute <= 90 and fixture_id not in MATCHS_ALERTES:
                        stats = match.get("statistics", [])
                        
                        # Récupération xG (API)
                        xg_api = sum(float(s.get("home", 0) or 0) + float(s.get("away", 0) or 0) 
                                     for s in stats if s.get("type") == "Expected Goals")
                        
                        # Récupération Tirs Cadrés (Plan B)
                        tirs_cadres = sum(int(s.get("home", 0) or 0) + int(s.get("away", 0) or 0) 
                                          for s in stats if s.get("type") == "Shots on Goal")
                        
                        xg_estime = tirs_cadres * 0.20
                        xg_total = max(xg_api, xg_estime)
                        
                        print(f"Analyse: {match['teams']['home']['name']} vs {match['teams']['away']['name']} ({minute}') | xG API: {xg_api} | Estimé: {xg_estime:.2f}")
                        
                        if score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                            msg = f"🚨 {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n📊 Score : {score} | xG : {xg_total:.2f}"
                            await application.bot.send_message(chat_id=CHAT_ID_CIBLE, text=msg)
                            MATCHS_ALERTES.add(fixture_id)
        await asyncio.sleep(60)

# ==========================================
# LANCEMENT (MAIN)
# ==========================================
if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    async def main_run():
        await application.initialize()
        await application.start()
        asyncio.create_task(lancer_serveur_web_async())
        asyncio.create_task(verifier_matchs_et_alerter(application))
        print("Bot opérationnel.")
        await asyncio.Event().wait()
    asyncio.run(main_run())
