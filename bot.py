async def main_async():
    # 1. On configure le bot Telegram (Envoi seul, pas de polling conflictuel)
    application = Application.builder().token(TOKEN).build()

    # 2. On initialise et démarre uniquement le moteur d'envoi
    await application.initialize()
    await application.start()
    
    print("Démarrage simultané du serveur Web et du scanner xG...")
    
    # Lancement groupé : serveur web + surveillance FotMob
    await asyncio.gather(
        lancer_serveur_web_async(),
        verifier_matchs_et_alerter(application)
    )
