import os
import asyncio
import threading
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================================
# CONFIGURATION & FILTRES PERSONNALISÉS
# ==========================================
TOKEN = "8625843812:AAHbyKLK0R5PrywkG9hBadP87QNXQIxOE5k"

MOTS_CLES_CHAMPIONNATS = [
    "Ligue 1", "Premier League", "LaLiga", "Serie A", "Bundesliga",
    "Liga Portugal", "Eredivisie", "Pro League", "Süper Lig", "Super League",
    "Ligue 2", "Championship", "2. Bundesliga", "LaLiga 2", "Serie B", "Liga Portugal 2",
    "MLS", "Brazil", "Eliteserien", "Allsvenskan", "J1 League",
    "Champions League", "Europa League", "Conference League", "World Cup"
]

CHAT_ID_CIBLE = 8684553871

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
# FONCTION DE SCRAPING DE FOTMOB
# ==========================================
def recuperer_matchs_fotmob():
    url = "https://www.fotmob.com/api/matches?date=today"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Erreur scraping FotMob : {e}")
        return None

# ==========================================
# ANALYSE DES MATCHS ET STRATÉGIE xG
# ==========================================
async def verifier_matchs_et_alerter(application: Application):
    global MATCHS_ALERTES
    while True:
        try:
            data = recuperer_matchs_fotmob()
            if data and "leagues" in data:
                for league in data["leagues"]:
                    nom_league = league.get("name", "")
                    est_un_championnat_cible = any(mot.lower() in nom_league.lower() for mot in MOTS_CLES_CHAMPIONNATS)
                    
                    if est_un_championnat_cible:
                        for match in league.get("matches", []):
                            match_id = str(match.get("id"))
                            
                            if match.get("status", {}).get("live", False):
                                try:
                                    minute = int(match.get("status", {}).get("liveTime", {}).get("short", "0").replace("'", ""))
                                except:
                                    minute = 0

                                if 75 <= minute <= 90 and match_id not in MATCHS_ALERTES:
                                    score = match.get("status", {}).get("scoreStr", "0-0").replace(" ", "")
                                    
                                    xg_domicile = float(match.get("stats", {}).get("xgHome", 0.0) or 0.0)
                                    xg_exterieur = float(match.get("stats", {}).get("xgAway", 0.0) or 0.0)
                                    xg_total = xg_domicile + xg_exterieur

                                    if score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                                        domicile = match.get("home", {}).get("name", "Domicile")
                                        exterieur = match.get("away", {}).get("name", "Extérieur")
                                        
                                        message = (
                                            f"🚨 **ALERTE BUT PROBABLE ({minute}')** 🚨\n\n"
                                            f"🏆 {nom_league}\n"
                                            f"⚔️ {domicile} vs {exterieur}\n"
                                            f"📊 Score actuel : {score}\n"
                                            f"📈 Total xG du match : {xg_total:.2f} (Seuil requis : {SEUILS_XG[score]:.2f})\n\n"
                                            f"💡 *Statistiquement, un but est très proche !*"
                                        )
                                        
                                        try:
                                            await application.bot.send_message(chat_id=CHAT_ID_CIBLE, text=message, parse_mode="Markdown")
                                            MATCHS_ALERTES.add(match_id)
                                            print(f"Alerte envoyée pour {domicile} - {exterieur}")
                                        except Exception as e:
                                            print(f"Erreur envoi Telegram : {e}")
        except Exception as e:
            print(f"Erreur dans la boucle principale : {e}")

        await asyncio.sleep(60)

# ==========================================
# SERVEUR HTTP POUR LA SURVEILLANCE RENDER
# ==========================================
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot en cours d'execution...")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

def lancer_serveur_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), WebServerHandler)
    print(f"Serveur Web activé sur le port {port}")
    server.serve_forever()

# ==========================================
# COMMANDE TELEGRAM ET INITIALISATION
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Le bot de surveillance xG est actif et stabilisé !")

async def main_async():
    """Gère l'initialisation et le polling de manière asynchrone et propre"""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Initialisation manuelle et sécurisée de l'application Telegram
    await application.initialize()
    await application.start()
    
    # On lance la boucle de surveillance en tâche de fond dans la boucle principale
    asyncio.create_task(verifier_matchs_et_alerter(application))
    
    # On démarre le polling officiel
    print("Démarrage du bot Telegram (Polling actif)...")
    await application.updater.start_polling()
    
    # Maintient le thread principal éveillé tant que le bot tourne
    while True:
        await asyncio.sleep(3600)

def main():
    # 1. Lancement du serveur Web en arrière-plan pour Render
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    
    # 2. Création forcée d'une nouvelle boucle d'événements propre pour éviter l'erreur de thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 3. Exécution globale
    try:
        loop.run_until_complete(main_async())
    except KeyboardInterrupt:
        print("Arrêt demandé.")

if __name__ == "__main__":
    main()
