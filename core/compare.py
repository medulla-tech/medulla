from core.cve_api import get_cves_for_package
from medulla_plugins.core.medulla_sender import get_packages_from_medulla

def compare_packages_with_cve():
    packages = get_packages_from_medulla()
    for package in packages:
        cves = get_cves_for_package(package)
        if cves:
            print(f"[!] Vulnérabilités pour {package}:")
            for cve in cves:
                print(f"   - {cve}")
        else:
            print(f"[+] Aucun CVE trouvé pour {package}")
