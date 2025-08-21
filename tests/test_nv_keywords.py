import requests
import json

# 🔧 Clé API NVD (remplace par la tienne)
API_KEY = "f7de8960-238e-4187-addc-168a7f0d6a85"
API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

# 🔧 Fichier inventaire à tester
INVENTORY_FILE = "/opt/src/core/db/inventories/fake_inventory.json"

# 🔧 Limite du nombre de résultats affichés
MAX_RESULTS = 3


def query_nvd(keyword):
    try:
        params = {
            "keywordSearch": keyword,
            "resultsPerPage": MAX_RESULTS
        }
        headers = {
            "apiKey": API_KEY
        }
        r = requests.get(API_URL, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("vulnerabilities", [])
    except Exception as e:
        print(f"[ERREUR] {keyword} → {e}")
        return []


def main():
    with open(INVENTORY_FILE, "r") as f:
        inventory = json.load(f)

    packages = inventory.get("packages", [])
    print(f"📦 {len(packages)} paquets détectés dans l'inventaire.\n")

    for pkg in packages:
        name = pkg.get("name", "")
        if not name:
            continue

        # On teste le nom brut et le nom simplifié
        keywords = list(set([
            name,
            name.split(".")[0],
            name.split("-")[0]
        ]))

        for kw in keywords:
            results = query_nvd(kw)
            if results:
                print(f"✅ {kw} → {len(results)} CVEs trouvées")
                for cve in results:
                    cve_id = cve["cve"]["id"]
                    desc = cve["cve"]["descriptions"][0]["value"][:80].replace("\n", " ")
                    print(f"    - {cve_id} : {desc}...")
                break  # on arrête après le premier mot-clé qui marche
        else:
            print(f"❌ Aucun résultat pour {name}")

if __name__ == "__main__":
    main()
