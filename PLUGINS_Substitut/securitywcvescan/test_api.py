import requests
import logging

BASE_URL = "http://127.0.0.1:8000"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    logging.info("Health: %s", r.json())

def test_add_inventory():
    items = [
        {"machine_id": "UUID-DEMO-0001", "package_name": "Chrome", "version": "120.0", "vendor": "Google"},
        {"machine_id": "UUID-DEMO-0002", "package_name": "Firefox", "version": "115.0", "vendor": "Mozilla"},
    ]
    r = requests.post(f"{BASE_URL}/inventory", json=items)
    logging.info("Add inventory: %s", r.json())

def test_add_results():
    items = [
        {"inventory_id": 1, "cve_id": "CVE-2025-1111", "severity": "HIGH", "score": 7.5, "description": "Faille Chrome"},
        {"inventory_id": 2, "cve_id": "CVE-2025-2222", "severity": "CRITICAL", "score": 9.8, "description": "Faille Firefox"},
    ]
    r = requests.post(f"{BASE_URL}/results", json=items)
    logging.info("Add results: %s", r.json())

def test_report():
    r = requests.get(f"{BASE_URL}/report/UUID-DEMO-0001")
    logging.info("Report UUID-DEMO-0001: %s", r.json())

def test_list_machines():
    r = requests.get(f"{BASE_URL}/machines")
    logging.info("Machines: %s", r.json())

def test_stats():
    r = requests.get(f"{BASE_URL}/stats")
    logging.info("Stats: %s", r.json())

def test_remediation():
    payload = {
        "machine_id": "UUID-DEMO-0001",
        "cve_id": "CVE-2025-1111",
        "action": "patch_applied"
    }
    r = requests.post(f"{BASE_URL}/remediation", json=payload)
    logging.info("Remediation: %s", r.json())


if __name__ == "__main__":
    test_health()
    test_add_inventory()
    test_add_results()
    test_report()
    test_list_machines()
    test_stats()
    test_remediation()
