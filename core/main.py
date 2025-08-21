import os
import csv
import json
import time
import logging
from datetime import datetime
import shutil
from pathlib import Path
from dotenv import load_dotenv

from core.cve_api import CVEChecker
from core.medulla_api import MedullaAPIClient, parse_machine_list

# Charge le .env placé à côté de ce fichier
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

# ---------- Helpers ENV ----------
def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def env_list(name: str):
    v = os.getenv(name)
    if not v:
        return None
    return [x.strip().upper() for x in v.split(",") if x.strip()]

# ---------- Variables d'environnement ----------
MEDULLA_URL  = os.getenv("MEDULLA_URL")
MEDULLA_USER = os.getenv("MEDULLA_USER")
MEDULLA_PASS = os.getenv("MEDULLA_PASS")
LDAP_USER    = os.getenv("LDAP_USER")
LDAP_PASS    = os.getenv("LDAP_PASS")
NVD_API_KEY  = os.getenv("NVD_API_KEY")

CVSS_THRESHOLD = float(os.getenv("CVSS_THRESHOLD", "0.0"))
TARGET_UUID    = os.getenv("TARGET_UUID")                   # optionnel (uuid_inventory)
MACHINE_SOURCE = os.getenv("MACHINE_SOURCE", "xmpp")
VERIFY_TLS     = env_bool("VERIFY_TLS", False)
INJECT_TEST_SOFTWARE = os.getenv("INJECT_TEST_SOFTWARE")   # ex: "log4j-core:2.14.1"
SEVERITIES     = env_list("SEVERITIES")                    # ex: "LOW,MEDIUM,HIGH,CRITICAL,UNKNOWN"

# Répertoires
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BASE_DIR = Path(os.getenv("BASE_DIR", "/opt/src/core/db"))
RESULT_DIR = BASE_DIR / "results"
INVENTORY_DIR = BASE_DIR / "inventories"
RESULT_DIR.mkdir(parents=True, exist_ok=True)
INVENTORY_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = RESULT_DIR / f"results_cve_{timestamp}.json"
OUTPUT_CSV  = RESULT_DIR / f"results_cve_{timestamp}.csv"
LATEST_JSON = RESULT_DIR / "results_cve_latest.json"

# Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Validation minimale (ne loggue pas les secrets)
_required = ["MEDULLA_URL","MEDULLA_USER","MEDULLA_PASS","LDAP_USER","LDAP_PASS","NVD_API_KEY"]
_missing = [k for k in _required if not globals().get(k)]
if _missing:
    raise SystemExit(f"Variables .env manquantes: {', '.join(_missing)}")

# ---------- Export ----------
def export_results(results):
    # JSON
    try:
        with OUTPUT_JSON.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        logging.info("Résultats JSON exportés : %s", OUTPUT_JSON)
    except Exception as e:
        logging.error("Échec export JSON : %s", e)

    # CSV
    try:
        with OUTPUT_CSV.open("w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Machine", "UUID", "Package", "Version", "CVE ID", "Severity", "CVSS", "Description"])
            for entry in results:
                for vuln in entry.get("vulnerabilities", []) or []:
                    writer.writerow([
                        entry.get("machine", ""),
                        entry.get("uuid", ""),
                        entry.get("package", ""),
                        entry.get("version", ""),
                        vuln.get("id", ""),
                        vuln.get("severity", ""),
                        vuln.get("score", ""),
                        (vuln.get("description", "") or "").replace("\n", " ")[:120]
                    ])
        logging.info("Résultats CSV exportés : %s", OUTPUT_CSV)
    except Exception as e:
        logging.error("Échec export CSV : %s", e)

# ---------- Main ----------
def main():
    logging.info("[*] Initialisation de la connexion Medulla...")
    try:
        client = MedullaAPIClient(MEDULLA_URL, MEDULLA_USER, MEDULLA_PASS, verify=VERIFY_TLS)
        if not client.authenticate(LDAP_USER, LDAP_PASS):
            logging.error("Échec de l'authentification.")
            return

        logging.info("Authentification réussie.")
        logging.info("Récupération des machines depuis %s...", MACHINE_SOURCE)

        xml_text = client.get_machines(source=MACHINE_SOURCE, raw=True)
        if not xml_text:
            logging.error("get_machines() n'a rien renvoyé (auth/cookie ?).")
            return

        machines = parse_machine_list(xml_text)
        if not machines:
            logging.warning("Aucune machine détectée.")
            return

        checker = CVEChecker(NVD_API_KEY, verbose=True)
        all_results = []

        # Paramètres de polling après injection
        POLL_ROUNDS = 4   # 5s + 3*10s ≈ 35s
        FIRST_SLEEP = 5
        NEXT_SLEEP  = 10

        for m in machines:
            uuid = m.get("uuid")
            uuid_inventory = m.get("uuid_inventory")
            hostname = m.get("hostname", "Inconnu")

            #if TARGET_UUID and uuid_inventory != TARGET_UUID:
             #   continue

            logging.info("🔍 Analyse de %s (InvUUID: %s)", hostname, uuid_inventory)

            try:
                # 1) Inventaire (OS/HW)
                inventory = client.get_inventory_dict(uuid, uuid_inventory)
                if not inventory:
                    logging.warning("Inventaire vide ou non récupérable pour %s", hostname)
                    continue

                # 2) (Optionnel) Injection d'un faux logiciel dans HKLM\...\Uninstall
                pkgs = []
                injected_name = injected_ver = None
                if INJECT_TEST_SOFTWARE:
                    injected_name, _, injected_ver = INJECT_TEST_SOFTWARE.partition(":")
                    injected_name = (injected_name or "").strip()
                    injected_ver  = (injected_ver or "1.0.0").strip()

                    if injected_name:
                        logging.info("🧪 Injection distante '%s:%s' sur %s...", injected_name, injected_ver, hostname)
                        ok = client.inject_uninstall_entry(uuid, injected_name, injected_ver)
                        if not ok:
                            logging.warning("Injection distante: certains REG ADD ont pu échouer (droits ?).")

                        # Déclenche inventaire côté agent
                        logging.info("🔄 Déclenchement inventaire agent...")
                        client.trigger_inventory(uuid)

                        # Poll l'inventaire jusqu'à voir le logiciel
                        sleep = FIRST_SLEEP
                        for i in range(POLL_ROUNDS):
                            time.sleep(sleep)
                            pkgs = client.get_inventory_softwares(uuid, uuid_inventory) or []
                            if any(p.get("name","").lower() == injected_name.lower() for p in pkgs):
                                logging.info("✅ Faux logiciel détecté dans l'inventaire de %s.", hostname)
                                break
                            sleep = NEXT_SLEEP
                        else:
                            logging.warning("⚠️ Faux logiciel non vu dans l'inventaire (droits/agent ?).")

                # 3) Récupération des logiciels si pas déjà fait par le polling
                if not pkgs:
                    pkgs = client.get_inventory_softwares(uuid, uuid_inventory) or []
                logging.info("🧩 %s: %d logiciels inventoriés", hostname, len(pkgs))
                if pkgs[:5]:
                    logging.info("   Exemples: %s", pkgs[:5])

                # Ceinture+bretelles: si on a demandé une injection, ajoute-le in-mémoire si absent
                if INJECT_TEST_SOFTWARE and injected_name:
                    if not any(p.get("name","").lower() == injected_name.lower() for p in pkgs):
                        pkgs.append({"name": injected_name, "version": injected_ver})
                        logging.info("ℹ️ Ajout en mémoire du paquet injecté (non vu côté agent).")

                inventory["packages"] = pkgs

                # 4) Sauvegarde locale de l'inventaire
                inventory_path = INVENTORY_DIR / f"{hostname}_{uuid_inventory}.json"
                with inventory_path.open("w", encoding="utf-8") as f:
                    json.dump(inventory, f, indent=4, ensure_ascii=False)
                logging.info("Inventaire sauvegardé : %s", inventory_path)

                # 5) Analyse CVE via fichier (OS + packages)
                result = checker.check_machine_vuln(
                    str(inventory_path),
                    min_cvss=CVSS_THRESHOLD,
                    severities=SEVERITIES
                )

                # 5bis) Scanner l'OS aussi par mot-clé pour plus de robustesse
                os_info = inventory.get("os", {})
                os_kw = " ".join(filter(None, [
                    os_info.get("vendor", ""),
                    os_info.get("name", ""),
                    os_info.get("version", "")
                ])).strip()
                if os_kw:
                    vulns_os_kw = checker.check_package_vuln(
                        os_kw, os_info.get("version", ""), min_cvss=CVSS_THRESHOLD, severities=SEVERITIES
                    ) or []
                    for v in vulns_os_kw:
                        result["cve_results"].append({**v, "raw_name": f"os:{os_kw.lower()}"})

                # 6) Regroupement par package + déduplication des CVE par id
                package_map = {}
                for vuln in result.get("cve_results", []) or []:
                    pkg = (vuln.get("raw_name") or "").lower()
                    if not pkg:
                        continue

                    if pkg not in package_map:
                        # retrouve la version du package dans l'inventaire
                        pkg_version = ""
                        for p in inventory.get("packages", []):
                            if (p.get("name") or "").lower() == pkg:
                                pkg_version = p.get("version", "")
                                break

                        package_map[pkg] = {
                            "machine": hostname,
                            "uuid": uuid_inventory,
                            "package": pkg,
                            "version": pkg_version,
                            "vulnerabilities": [],
                            "_seen_ids": set(),  # pour dédup interne
                        }

                    vid = vuln.get("id")
                    if vid and vid in package_map[pkg]["_seen_ids"]:
                        continue
                    if vid:
                        package_map[pkg]["_seen_ids"].add(vid)
                    package_map[pkg]["vulnerabilities"].append(vuln)

                # retire la clé technique _seen_ids
                for pkg in list(package_map.keys()):
                    package_map[pkg].pop("_seen_ids", None)

                all_results.extend(package_map.values())

            except Exception as e:
                logging.error("Analyse échouée pour %s : %s", hostname, e)

        # Export & récap
        export_results(all_results)

        sev_count = {}
        for r in all_results:
            for v in r.get("vulnerabilities", []) or []:
                sev = (v.get("severity") or "UNKNOWN").upper()
                sev_count[sev] = sev_count.get(sev, 0) + 1
        if sev_count:
            logging.info("Répartition par sévérité : %s", sev_count)
            logging.info("Vulnérabilités détectées : résultats exportés.")
        else:
            logging.info("Aucun CVE détecté avec les filtres actuels (CVSS_THRESHOLD=%s, SEVERITIES=%s).",
                         CVSS_THRESHOLD, SEVERITIES or "TOUTES")

    except Exception as e:
        logging.exception("[!] Erreur inattendue : %s", e)

if __name__ == "__main__":
    main()
    if OUTPUT_JSON.exists():
        try:
            shutil.copy(OUTPUT_JSON, LATEST_JSON)
            logging.info("Copie latest réussie : %s", LATEST_JSON)
        except Exception as e:
            logging.error("Copie latest échouée : %s", e)
    else:
        logging.warning("Fichier JSON introuvable. Copie latest ignorée.")
