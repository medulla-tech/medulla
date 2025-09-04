# MMC_Database/securitywcvescan/test_insert.py
import sqlite3
import logging
from pathlib import Path

DB_PATH = Path("/opt/securitywcvescan/securitywcvescan.db")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def test_insert():
    if not DB_PATH.exists():
        logging.error("DB inexistante : %s", DB_PATH)
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    logging.info("Insertion d’un inventaire fictif...")

    # 1) Inventaire simulé
    cur.execute(
        """
        INSERT INTO inventories (machine_id, package_name, version, vendor)
        VALUES (?, ?, ?, ?)
        """,
        ("UUID-TEST-1234", "TestSoft", "1.0.0", "VendorX"),
    )
    inv_id = cur.lastrowid

    logging.info("Inventaire inséré avec id=%s", inv_id)

    # 2) Vulnérabilités fictives liées à cet inventaire
    vulns = [
        ("CVE-2025-0001", "HIGH", 8.5, "Test vulnérabilité critique"),
        ("CVE-2025-0002", "MEDIUM", 5.4, "Test vulnérabilité moyenne"),
    ]
    for cve_id, sev, score, desc in vulns:
        cur.execute(
            """
            INSERT INTO results (inventory_id, cve_id, severity, score, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (inv_id, cve_id, sev, score, desc),
        )
    conn.commit()

    logging.info("Vulnérabilités insérées (%d)", len(vulns))

    # 3) Vérification du contenu
    cur.execute(
        """
        SELECT i.machine_id, i.package_name, r.cve_id, r.severity, r.score
        FROM inventories i
        JOIN results r ON i.id = r.inventory_id
        WHERE i.id = ?
        """,
        (inv_id,),
    )
    rows = cur.fetchall()
    logging.info("Requête de vérification :")
    for row in rows:
        print(" →", row)

    conn.close()


if __name__ == "__main__":
    test_insert()
