# MMC_Database/securitywcvescan/test_reset.py
import sqlite3
import logging
import os

DB_PATH = "/opt/securitywcvescan/securitywcvescan.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def reset_db():
    if not os.path.exists(DB_PATH):
        logging.warning("DB inexistante: %s", DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        logging.info("[test_reset] Suppression du contenu des tables...")
        cur.execute("DELETE FROM results;")
        cur.execute("DELETE FROM inventories;")
        conn.commit()
        logging.info("[test_reset] Tables vidées avec succès.")
    except Exception as e:
        logging.error("Erreur reset DB: %s", e)
    finally:
        conn.close()

if __name__ == "__main__":
    reset_db()
