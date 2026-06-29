import os
import asyncio
import requests
import logging
from telegram import Bot

# ... (tes configurations restent identiques)

async def verifier_matchs():
    logging.info("Démarrage en mode vérification de disponibilité...")
    while True:
        try:
            # ... (récupération de la liste des matchs)
            
            # Pour chaque match :
            # ... (requête statistique)
            
            xg_total = None # On change : au lieu de 0.0, on met None (inconnu)
            
            if data_stats.get("response"):
                for team_stats in data_stats["response"]:
                    for s in team_stats.get("statistics", []):
                        if s.get("type") == "Expected Goals":
                            val = s.get("value")
                            if val is not None:
                                xg_total = float(val)

            # LOGIQUE MODIFIÉE :
            # Si xg_total est None, on ne conclut pas à 0, on continue d'attendre
            if xg_total is not None:
                logging.info(f"DEBUG: {home} vs {away} | xG trouvé : {xg_total}")
                if 75 <= minute <= 90 and score in SEUILS_XG and xg_total >= SEUILS_XG[score]:
                    # ... (envoi alerte)
            else:
                # La donnée n'est pas encore disponible, on attend la prochaine minute
                pass

        except Exception as e:
            logging.error(f"Erreur : {e}")
        
        await asyncio.sleep(60)
