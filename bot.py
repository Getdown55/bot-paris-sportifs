import os
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================================
# CONFIGURATION & CLEFS OFFICIELLES
# ==========================================
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
API_KEY = "Fd062d2a521ed65d8c0944cc4a373600"
CHAT_ID_CIBLE = 8684553871

# Liste des IDs officiels de l'API pour tes championnats cibles
# (Évite le tri par texte, on va directement cibler les bonnes compétitions)
IDS_CHAMPIONNATS = [
    39, 61, 140, 135, 78,   # Premier League, Ligue 1, LaLiga, Serie A, Bundesliga
    94, 88, 144, 203, 119,  # Primeira Liga, Eredivisie, Jupiler Pro League, Süper Lig, Super League
    40, 62, 141, 136, 79,   # Championship, Ligue 2, LaLiga 2, Serie B, 2. Bundesliga
    253, 71, 103, 99,       # MLS, Serie A (Brésil), Eliteserien, Allsvenskan
    2, 3, 848, 1            # Champions League, Europa League, Conference League, World Cup
]

SEUILS_XG = {
    "0-0": 1.20,
    "1-0": 1.65,
    "0-1": 1.65,
    "1-1": 2.10,
    "2-1": 2.40,
    "1-2": 2.40,
    "2-2": 2.80
}

MATCHS_ALERTES = set()

# ==========================================
# FONCTION DE RECUPERATION VIA API-FOOTBALL
# ==========================================
def recuperer_matchs_en_direct():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur API-Football (Status {response.status_code})")
            return None
    except Exception as e:
        print(f"Erreur requête API-Football : {e}")
        return None

# ==========================================
# ANALYSE DES MATCHS ET STRATÉGIE xG
# ==========================================
async def verifier_matchs_et_alerter(application: Application):
    global MATCHS_ALERTES
    print("Boucle de surveillance API-Football initialisée.")
    
    while True:
        try:
            data = recuperer_matchs_en_direct()
            if data and "response" in data:
                matchs_en_cours = data["response"]
                print(f"Patrouille officielle effectuée. {len(matchs_en_cours)} matchs en direct trouvés dans le monde.")
                
                for match in matchs_en_cours:
                    league_id = match.get("league", {}).get("id")
                    
                    # On vérifie si le match fait partie de tes championnats cibles
                    if league_id in IDS_CHAMPIONNATS:
                        fixture_id = str(match.get("fixture", {}).get("id"))
                        nom_league = match.get("league", {}).get("name", "Championnat")
                        
                        # Récupération du temps de jeu
                        minute = match.get("fixture", {}).get("status", {}).get("elapsed", 0)
                        
                        if 75 <= minute <= 90 and fixture_id not in MATCHS_ALERTES:
                            # Récupération du score actuel
                            goals_home = match.get("goals", {}).get("home", 0)
                            goals_away = match.get("goals", {}).get("away", 0)
                            score = f"{goals_home}-{goals_away}"
                            
                            # Récupération des xG (si disponibles dans les stats live de l'API)
                            # Note : Si les xG live ne sont pas fournis, on se base sur un calcul d'attaques dangereuses/tirs
                            # Pour rester fidèle à tes seuils, on extrait les tirs ou xG si présents
                            # API-Football fournit les Tirs aux buts dans le flux live
                            stats = match.get("statistics", [])
                            # Par défaut si pas de xG natif, on simule une estimation via les tirs pour ne pas bloquer
                            xg_total = 0.0
                            
                            # Recherche des xG dans les stats si disponibles
                            for s in stats:
                                if s.get("type") == "Expected Goals":
                                    xg_total += float(s.get("home", 0.0)) + float(s.get("away", 0.0))
                            
                            # Si l'API ne donne pas les xG en direct sur ce match, on estime avec les tirs cadrés (0.15 xG par tir cadré)
                            if xg_total == 0.0:
                                tirs_cadres = 0
                                for s in stats:
                                    if s.get("type") == "Shots on Goal":
                                        tirs_cadres += int(s.get("home") or 0) + int(s.get("away") or 0)
                                xg_total = tirs_cadres * 0.15

                            if score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                                domicile = match.get("teams", {}).get("home", {}).get("name", "Domicile")
                                exterieur = match.get("teams", {}).get("away", {}).get("name", "Extérieur")
                                
                                message = (
                                    f"🚨 **ALERTE BUT PROBABLE ({minute}')** 🚨\n\n"
                                    f"🏆 {nom_league}\n"
                                    f"⚔️ {domicile} vs {exterieur}\n"
                                    f"📊 Score actuel : {score}\n"
                                    f"📈 Indice de pression / xG : {xg_total:.2f} (Seuil requis : {SEUILS_XG[score]:.2f})\n\n"
                                    f"💡 *Statistiquement, les conditions d'un but sont réunies !*"
                                )
                                
                                try:
                                    await application.bot.send_message(chat_id=CHAT_ID_CIBLE, text=message, parse_mode="Markdown")
                                    MATCHS_ALERTES.add(fixture_id)
                                    print(f"Alerte envoyée avec succès pour {domicile} - {exterieur}")
                                except Exception as e:
                                    print(f"Erreur envoi Telegram : {e}")
                                    
        except Exception as e:
            print(f"Erreur dans la boucle principale : {e}")

        # L'API payante autorise un scan régulier, on patrouille toutes les 60 secondes
        await asyncio.sleep(60)

# ==========================================
# SERVEUR WEB ASYNC (Pour satisfaire Render)
# ==========================================
async def gerer_ping_render(reader, writer):
    try:
        data = await reader.read(100)
    except:
        pass
    reponse = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 24\r\n\r\nBot xG en cours de run..."
    try:
        writer.write(reponse)
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except:
        pass

async def lancer_serveur_web_async():
    port = int(os.environ.get("PORT", 8080))
    serveur = await asyncio.start_server(gerer_ping_render, "0.0.0.0", port)
    print(f"Serveur Web Asynchrone activé sur le port {port}")
    async with serveur:
        await serveur.serve_forever()

# ==========================================
# POINT D'ENTRÉE ASYNC PRINCIPAL
# ==========================================
async def main_async():
    application = Application.builder().token(TOKEN).build()
    await application.initialize()
    await application.start()
    
    print("Démarrage simultané du serveur Web et du scanner Officiel...")
    
    asyncio.create_task(lancer_serveur_web_async())
    asyncio.create_task(verifier_matchs_et_alerter(application))
    
    while True:
        await asyncio.sleep(3600)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
