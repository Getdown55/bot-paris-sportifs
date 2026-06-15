import os
import asyncio
import json
import urllib.request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================================
# CONFIGURATION & FILTRES PERSONNALISÉS
# ==========================================
TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"

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
    print("Boucle de surveillance FotMob initialisée.")
    while True:
        try:
            data = recuperer_matchs_fotmob()
            if data and "leagues" in data:
                for league in data["leagues"]:
                    nom_league = league.get("name", "")
                    est_un_championnat_cible = any(mot.lower() in nom_league.lower() for mot in MOTS_CLES_CHAMPIONNATS)
                    
                    if est_un_championnat_cible:
                        for match in league.get("matches
