import logging
import asyncio
import requests
from telegram import Bot

TOKEN = "8625843812:AAEgCJDUqjXP_ShrMpZUbAtbzI9h2eK51SA"
CHAT_ID = "-1003960057728"
URL_SHEET = "TON_URL_A_METTRE_ICI"

bot = Bot(token=TOKEN)

def envoyer_vers_sheets(match_name, score, xg_total):
    try:
        # On met un timeout court pour ne pas bloquer le bot
        requests.post(URL_SHEET, json={"match": match_name, "score": score, "xg": xg_total}, timeout=5)
    except Exception:
        pass # Si ça rate, on ignore et on continue

async def main():
    while True:
        try:
            url = "https://v3.football.api-sports.io/fixtures?live=all"
            headers = {"x-rapidapi-key": "Fd062d2a521ed65d8c0944cc4a373600", "x-rapidapi-host": "v3.football.api-sports.io"}
            data = requests.get(url, headers=headers, timeout=10).json()

            for match in data.get("response", []):
                # 75e minute et plus
                if match["fixture"]["status"]["elapsed"] >= 75:
                    f_id = match["fixture"]["id"]
                    # Calcul xG simple sans requête supplémentaire pour éviter les timeouts
                    # Note : on utilise les stats déjà présentes dans 'data' si possible
                    stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={f_id}"
                    stats = requests.get(stats_url, headers=headers, timeout=10).json().get("response", [])
                    
                    xg = sum(float(s.get("value") or 0) for team in stats for s in team.get("statistics", []) if "expected" in str(s.get("type", "")).lower())
                    
                    s_h, s_a = match["goals"]["home"], match["goals"]["away"]
                    match_name = f"{match['teams']['home']['name']} vs {match['teams']['away']['name']}"
                    
                    # 1. Envoi systématique au Sheet
                    envoyer_vers_sheets(match_name, f"{s_h}-{s_a}", f"{xg:.2f}")
                    
                    # 2. Tes conditions Telegram
                    if s_h == 0 and s_a == 0: seuil = 1.2
                    elif (s_h == 1 and s_a == 0) or (s_h == 0 and s_a == 1): seuil = 1.5
                    elif s_h == 1 and s_a == 1: seuil = 1.8
                    elif (s_h == 2 and s_a == 0) or (s_h == 0 and s_a == 2): seuil = 2.0
                    elif (s_h == 2 and s_a == 1) or (s_h == 1 and s_a == 2): seuil = 2.2
                    else: seuil = 2.5
                    
                    if xg >= seuil:
                        await bot.send_message(chat_id=CHAT_ID, text=f"🚨 ALERTE {match_name} | xG: {xg:.2f}")

        except Exception as e:
            # On log l'erreur mais on ne crash pas
            print(f"Erreur : {e}")
        
        await asyncio.sleep(60) # Pause de 1 minute

if __name__ == "__main__":
    asyncio.run(main())
