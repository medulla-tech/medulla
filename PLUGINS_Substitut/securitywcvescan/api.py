from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import logging
from typing import List, Dict, Any

# ------------------------
# Configuration
# ------------------------
app = FastAPI(title="SecuritywCVEscan API", version="1.0.0")
DB_PATH = "/opt/securitywcvescan/securitywcvescan.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ------------------------
# Models
# ------------------------
class InventoryItem(BaseModel):
    machine_id: str
    package_name: str
    version: str
    vendor: str


class ResultItem(BaseModel):
    inventory_id: int
    cve_id: str
    severity: str
    score: float
    description: str


class RemediationItem(BaseModel):
    machine_id: str
    cve_id: str
    action: str
    status: str = "pending"


class RemediationRequest(BaseModel):
    machine_id: str
    cve_id: str
    action: str  # ex: "patch_applied", "ignored"


# ------------------------
# Utils
# ------------------------
def get_db() -> sqlite3.Connection:
    """Retourne une connexion SQLite vers la base locale."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # accès dict-like aux résultats
    return conn


# ------------------------
# Endpoints
# ------------------------
@app.get("/health")
def health() -> Dict[str, str]:
    """Vérifie si l’API est en ligne."""
    return {"status": "ok", "message": "API is running"}


@app.post("/inventory")
def add_inventory(items: List[InventoryItem]) -> Dict[str, Any]:
    """Ajoute un ou plusieurs packages à l’inventaire."""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            ids = []
            for it in items:
                cur.execute(
                    """
                    INSERT INTO inventories (machine_id, package_name, version, vendor)
                    VALUES (?, ?, ?, ?)
                    """,
                    (it.machine_id, it.package_name, it.version, it.vendor),
                )
                ids.append(cur.lastrowid)
        return {"inserted_ids": ids}
    except Exception as e:
        logging.error("Erreur lors de l’ajout inventaire: %s", e)
        raise HTTPException(status_code=500, detail="Erreur base de données")


@app.post("/results")
def add_results(items: List[ResultItem]) -> Dict[str, int]:
    """Ajoute des résultats CVE liés à des packages inventoriés."""
    try:
        with get_db() as conn:
            cur = conn.cursor()
            for it in items:
                cur.execute(
                    """
                    INSERT INTO results (inventory_id, cve_id, severity, score, description)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (it.inventory_id, it.cve_id, it.severity, it.score, it.description),
                )
        return {"inserted": len(items)}
    except Exception as e:
        logging.error("Erreur lors de l’ajout résultats: %s", e)
        raise HTTPException(status_code=500, detail="Erreur base de données")


@app.get("/results/{machine_id}")
def get_results(machine_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Récupère les résultats CVE pour une machine donnée."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT i.machine_id, i.package_name, r.cve_id, r.severity, r.score, r.description
            FROM results r
            JOIN inventories i ON r.inventory_id = i.id
            WHERE i.machine_id = ?
            """,
            (machine_id,),
        )
        rows = [dict(row) for row in cur.fetchall()]
    return {"results": rows}


@app.get("/report/{machine_id}")
def get_report(machine_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Retourne un rapport complet (inventaire + vulnérabilités) d’une machine."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT i.machine_id, i.package_name, i.version, i.vendor,
                   r.cve_id, r.severity, r.score, r.description
            FROM inventories i
            LEFT JOIN results r ON r.inventory_id = i.id
            WHERE i.machine_id = ?
            """,
            (machine_id,),
        )
        rows = [dict(row) for row in cur.fetchall()]
    return {"report": rows}


@app.get("/machines")
def list_machines() -> Dict[str, List[str]]:
    """Liste les machines présentes dans l’inventaire."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT machine_id FROM inventories")
        machines = [row[0] for row in cur.fetchall()]
    return {"machines": machines}


@app.get("/stats")
def stats() -> Dict[str, Dict[str, int]]:
    """Retourne des statistiques globales par sévérité CVE."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT severity, COUNT(*) as count FROM results GROUP BY severity")
        rows = {row[0]: row[1] for row in cur.fetchall()}
    return {"stats": rows}


@app.post("/remediation")
def remediation(request: RemediationRequest) -> Dict[str, Any]:
    """Déclenche une action de remédiation (stub pour plugin)."""
    logging.info(
        "[API] Remediation demandée: machine=%s CVE=%s action=%s",
        request.machine_id, request.cve_id, request.action
    )
    # TODO: intégrer la logique réelle du plugin MMC_Plugins
    return {
        "status": "success",
        "machine_id": request.machine_id,
        "cve_id": request.cve_id,
        "action": request.action
    }
