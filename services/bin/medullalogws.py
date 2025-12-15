#!/usr/bin/env python3
import argparse
import asyncio
import logging
import websockets
import mysql.connector
from datetime import datetime, timedelta
import os
import sys
import json
import configparser
import daemon
from daemon import pidfile

# ============================================
#               CONFIGURATION PAR DÉFAUT
# ============================================
DEFAULT_CONFIG = {
    "PORT": 8082,
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_USER": "root",
    "MYSQL_PASSWORD": "M3dull4+JFK",
    "MYSQL_DATABASE": "xmppmaster",
    "MYSQL_PORT": 3306,
    "taille_historique_line": 150,
    "filelog": "/var/log/medullalogws/medullalogws.log",
    "levellog": "INFO"
}

# taille_historique_line = 150
# Un dictionnaire pour stocker les derniers ID par client et le temps de connexion
last_client_data = {}
# Dictionnaire global pour stocker les last_id et les horodatages
client_last_ids = {}
hist_requests = {}
# ============================================
#               LOGGING
# ============================================
def setup_logging(console_mode, log_file, log_level):
    logger = logging.getLogger("websocket_server")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear previous handlers
    logger.handlers = []
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # File Handler
    if not console_mode:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))

        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler (only in console mode)
    if console_mode:
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)  # En mode console, on force le niveau DEBUG
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger

# ============================================
#             SQL Connection
# ============================================
def get_db(config):
    return mysql.connector.connect(
        host=config["MYSQL_HOST"],
        user=config["MYSQL_USER"],
        password=config["MYSQL_PASSWORD"],
        database=config["MYSQL_DATABASE"],
        port=config["MYSQL_PORT"],
        autocommit=True
    )

# ============================================
#             Load Configuration
# ============================================
def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    # Si le fichier n'existe pas, on le crée avec les valeurs par défaut
    if not os.path.exists(config_file):
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            config["DEFAULT"] = DEFAULT_CONFIG
            config.write(f)

    # Charger la configuration
    if "DEFAULT" not in config:
        config["DEFAULT"] = DEFAULT_CONFIG

    # Fusionner avec les valeurs par défaut
    config_dict = {**DEFAULT_CONFIG, **dict(config["DEFAULT"])}

    # Convertir les types
    config_dict["PORT"] = int(config_dict["PORT"])
    config_dict["MYSQL_PORT"] = int(config_dict["MYSQL_PORT"])
    config_dict["taille_historique_line"] = int(config_dict["taille_historique_line"])

    return config_dict

# ============================================
#             Daemon Context
# ============================================
def run_daemon(config, config_file):
    logger = setup_logging(False, config["filelog"], config["levellog"])

    logger.info(f"Démarrage du serveur WebSocket en mode daemon (config: {config_file})...")

    start_server = websockets.serve(
        lambda ws, p: handle_client(ws, p, logger, config),
        "0.0.0.0",
        config["PORT"]
    )

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

# ============================================
#             Main Function
# ============================================
async def safe_send(ws, data, logger):
    try:
        await ws.send(data)
        return True
    except websockets.exceptions.ConnectionClosed:
        logger.info("WebSocket fermé lors d’un envoi.")
        return False
    except Exception:
        logger.exception("Erreur inattendue lors d’un send()")
        return False

async def handle_client(websocket, path, logger, config):
    MAX_SIZE = 5000
    PING_INTERVAL = 60
    RECONNECT_WINDOW = 180
    HIST_DELAY = 60

    # # Initialisation des variables "globales" locales
    # if not hasattr(handle_client, 'client_last_ids'):
    #     handle_client.client_last_ids = {}
    # if not hasattr(handle_client, 'hist_requests'):
    #     handle_client.hist_requests = {}

    logger.info("Client connecté")
    db = get_db(config)
    cursor = db.cursor(dictionary=True)

    try:
        params = await websocket.recv()
        logger.info(f"Paramètres reçus : {params}")
        p = json.loads(params)
        action = p.get("action")
        cn = p.get("cn")

        if action not in ["viewlog", "hist"]:
            await safe_send(websocket, "Action invalide", logger)
            return

    except Exception:
        logger.exception("Erreur lors du parsing des paramètres")
        await safe_send(websocket, "Erreur paramètres", logger)
        return

    # ============================================================================
    #  MODE HIST : envoi de l’historique seulement une fois par minute
    # ============================================================================
    if action == "hist":
        now = datetime.now()
        await safe_send(websocket, "@COMMAND@:CLEANIFRAME", logger)
        hist_requests[cn] = now
        await safe_send(websocket, f"Machine OFF Historique Machine  {cn}", logger)
        cursor.execute("""
            SELECT id, text
            FROM (
                SELECT id, text
                FROM logs
                WHERE type = 'viewlog'
                AND module = %s
                ORDER BY id DESC
                LIMIT %s
            ) AS t
            ORDER BY id ASC
        """, (cn, config["taille_historique_line"],))
        rows = cursor.fetchall()

        for r in rows:
            for line in r["text"].splitlines():
                for i in range(0, len(line), MAX_SIZE):
                    await safe_send(websocket, line[i:i+MAX_SIZE], logger)

        logger.info(f"Historique HIST envoyé pour {cn}")
        await websocket.close()
        return

    # ============================================================================
    #  MODE VIEWLOG : Live + reconnexion rapide
    # ============================================================================
    last_id = 0
    now = datetime.now()

    # Reconnexion rapide
    if cn in client_last_ids:
        stored_last_id, stored_time = client_last_ids[cn]
        if now - stored_time < timedelta(seconds=RECONNECT_WINDOW):
            last_id = stored_last_id
            logger.info(f"Reconnexion rapide pour {cn}, reprise depuis id={last_id}")
        else:
            del client_last_ids[cn]
    else:
        logger.info(f"Nouveau client ou reconnexion tardive pour {cn} ")

    # --------------------------------------------------------------------------
    # Envoi de l’historique live (appel viewlog)
    # --------------------------------------------------------------------------
    if last_id == 0:
        cursor.execute("""
            SELECT id, text
            FROM (
                SELECT id, text
                FROM logs
                WHERE type = 'viewlog'
                AND module = %s
                ORDER BY id DESC
                LIMIT %s
            ) AS t
            ORDER BY id ASC
        """, (cn, config["taille_historique_line"],))
        rows = cursor.fetchall()

        for r in rows:
            for line in r["text"].splitlines():
                for i in range(0, len(line), MAX_SIZE):
                    if not await safe_send(websocket, line[i:i+MAX_SIZE], logger):
                        return
            last_id = r["id"]

        logger.info(f"Historique VIEWLOG envoyé pour {cn}, last_id={last_id} ")

    # ============================================================================
    # Boucle LIVE
    # ============================================================================
    last_ping_time = asyncio.get_event_loop().time()
    try:
        while True:
            if websocket.closed:
                logger.info(f"Client déconnecté. {cn}")
                client_last_ids[cn] = (last_id, datetime.now())
                return

            # Ping périodique
            current_time = asyncio.get_event_loop().time()
            if current_time - last_ping_time >= PING_INTERVAL:
                if not await safe_send(websocket, "PING", logger):
                    client_last_ids[cn] = (last_id, datetime.now())
                    return
                last_ping_time = current_time

            # Chercher les nouvelles lignes
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, text
                FROM logs
                WHERE type = 'viewlog'
                AND module = %s
                AND id > %s
                ORDER BY id ASC
            """, (cn, last_id))
            rows = cursor.fetchall()
            # if len(rows) > 0:
            #     logger.info(f"FROM {cn} : {len(rows)} ")

            for r in rows:
                for line in r["text"].splitlines():
                    for i in range(0, len(line), MAX_SIZE):
                        if not await safe_send(websocket, line[i:i+MAX_SIZE], logger):
                            client_last_ids[cn] = (last_id, datetime.now())
                            return
                last_id = r["id"]

            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client a fermé proprement. {cn}")
        client_last_ids[cn] = (last_id, datetime.now())
    except Exception:
        logger.exception(f"Erreur inattendue dans le live. {cn}")
        client_last_ids[cn] = (last_id, datetime.now())

# ============================================
#               MAIN
# ============================================
def main():
    parser = argparse.ArgumentParser(description="Serveur WebSocket pour les logs.")
    parser.add_argument("-c", "--console", action="store_true", help="Mode console (logs en direct)")
    parser.add_argument("-d", "--daemon", action="store_true", help="Mode daemon (logs dans un fichier)")
    parser.add_argument("-f", "--config", default="/etc/medullalogws/medullalogws.ini", help="Chemin vers le fichier de configuration")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.daemon:
        # Mode daemon
        context = daemon.DaemonContext(
            working_directory="/tmp",
            umask=0o002,
            pidfile=pidfile.TimeoutPIDLockFile("/var/run/medullalogws.pid"),
            stdout=open(config["filelog"], "a+"),
            stderr=open(config["filelog"], "a+"),
        )
        with context:
            asyncio.run(run_daemon(config, args.config))
    elif args.console:
        # Mode console
        logger = setup_logging(True, config["filelog"], "DEBUG")  # En mode console, on force le niveau DEBUG
        logger.info(f"Démarrage du serveur WebSocket en mode console (config: {args.config})...")

        start_server = websockets.serve(
            lambda ws, p: handle_client(ws, p, logger, config),
            "0.0.0.0",
            config["PORT"]
        )

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
    else:
        print("Veuillez spécifier un mode : -c (console) ou -d (daemon).")
        sys.exit(1)

if __name__ == "__main__":
    main()
