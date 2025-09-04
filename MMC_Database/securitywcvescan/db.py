import sqlite3, logging
from pathlib import Path

DB_PATH = "/opt/securitywcvescan/securitywcvescan.db"
SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "MMC_SQLSchema" / "securitywcvescan"

def init_db():
    logging.info("[SecuritywCVEscan] Initialisation DB")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Charger tous les fichiers SQL
    for sql_file in sorted(SCHEMA_DIR.glob("*.sql")):
        logging.info(f"[SecuritywCVEscan] Exécution du schema: {sql_file.name}")
        with sql_file.open("r", encoding="utf-8") as f:
            cur.executescript(f.read())

    conn.commit()
    conn.close()
