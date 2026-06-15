import os
import asyncio
import requests
from telegram.ext import Application

# ==========================================
# CONFIGURATION
# ==========================================
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
# Utilise la variable d'environnement ou ton ID par défaut
CHAT_ID_CIBLE = os.environ.get("CHAT_ID_CIBLE", "-1003960057728")

IDS_CHAMPIONNATS = [
    39, 61, 140, 135, 78, 94, 88, 144, 203, 119,
    40, 62, 141, 136, 79, 253, 71, 103, 99, 2, 3, 848, 1
]

SEUILS_XG = {
    "0-0": 1.20, "1-0": 1.65, "0-1": 1.65, "1-1": 2.10,
    "2-1": 2.40, "1-2": 2.40, "2-2": 2.80
}

MATCHS_ALERTES = set()

# ==========================================
# RECUPERATION API
# ==========================================
def recuperer_matchs_en_direct():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json() if response.status_code == 200 else None
    except:
        return None

# ==========================================
# ANALYSE ET ALERTE
# ==========================================
async def verifier_matchs_et_alerter(application: Application):
    global MATCHS_ALERTES
    print("Boucle de surveillance activée.")
    while True:
        try:
            data = recuperer_matchs_en_direct()
            if data and "response" in data:
                for match in data["response"]:
                    if match.get("league", {}).get("id") in IDS_CHAMPIONNATS:
                        fixture_id = str(match.get("fixture", {}).get("id"))
                        minute = match.get("fixture", {}).get("status", {}).get("elapsed", 0)
                        
                        if 75 <= minute <= 90 and fixture_id not in MATCHS_ALERTES:
                            goals_home = match.get("goals", {}).get("home", 0)
                            goals_away = match.get("goals", {}).get("away", 0)
                            score = f"{goals_home}-{goals_away}"
                            
                            stats = match.get("statistics", [])
                            xg_total = sum(float(s.get("home", 0)) + float(s.get("away", 0)) for s in stats if s.get("type") == "Expected Goals")
                            
                            if xg_total == 0:
                                xg_total = sum(int(s.get("home") or 0) + int(s.get("away") or 0) for s in stats if s.get("type") == "Shots on Goal") * 0.15

                            if score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                                msg = (f"🚨 **ALERTE BUT PROBABLE ({minute}')** 🚨\n\n"
                                       f"⚔️ {match['teams']['home']['name']} vs {match['teams']['away']['name']}\n"
                                       f"📊 Score : {score} | xG : {xg_total:.2f}")
                                await application.bot.send_message(chat_id=CHAT_ID_CIBLE, text=msg, parse_mode="Markdown")
                                MATCHS_ALERTES.add(fixture_id)
        except Exception as e:
            print(f"Erreur : {e}")
        await asyncio.sleep(60)

# ==========================================
# SERVEUR WEB (Optimisé pour Render)
# ==========================================
async def lancer_serveur_web_async():
    port = int(os.environ.get("PORT", 8080))
    async def handle(reader, writer):
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
        await writer.drain()
        writer.close()
    
    server = await asyncio.start_server(handle, "0.0.0.0", port)
    print(f"Serveur Web activé sur le port {port}")
    async with server: await server.serve_forever()

async def main_async():
    application = Application.builder().token(TOKEN).build()
    await application.initialize()
    await application.start()
    
    # Message de test au démarrage pour valider la connexion
    try:
        await application.bot.send_message(chat_id=CHAT_ID_CIBLE, text="✅ Bot opérationnel : Patrouille lancée !")
        print("Message de test envoyé.")
    except Exception as e:
        print(f"Erreur envoi message test : {e}")
    
    asyncio.create_task(lancer_serveur_web_async())
    asyncio.create_task(verifier_matchs_et_alerter(application))
    
    while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main_async())
