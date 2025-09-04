# MMC_Database/securitywcvescan/test_select.py
import logging
import sqlite3
from pathlib import Path

DB_PATH = Path("/opt/securitywcvescan/securitywcvescan.db")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logging.info("[test_select] Lecture du contenu de la base %s", DB_PATH)

    if not DB_PATH.exists():
        logging.error("Base inexistante: %s", DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    logging.info("=== Inventaires ===")
    for row in cur.execute("SELECT id, machine_id, package_name, version, vendor, collected_at FROM inventories"):
        print("Inventaire:", row)

    logging.info("=== Vulnérabilités ===")
    query = """
    SELECT i.machine_id, i.package_name, r.cve_id, r.severity, r.score, r.description
    FROM results r
    JOIN inventories i ON r.inventory_id = i.id
    ORDER BY r.detected_at DESC
    """
    for row in cur.execute(query):
        print("Vuln:", row)

    conn.close()
    logging.info("Fin de lecture.")

if __name__ == "__main__":
    main()
