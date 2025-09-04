# /opt/securitywcvescan/MMC_Database/securitywcvescan/test_db.py
import logging
import sqlite3
from pathlib import Path

from . import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    logging.info("[test_db] Initialisation de la base...")
    db.init_db()

    # Vérifions que la DB existe
    db_path = Path(db.DB_PATH)
    if db_path.exists():
        logging.info(f"[test_db] DB créée: {db_path}")
    else:
        logging.error("[test_db] DB introuvable après init()")

if __name__ == "__main__":
    main()
