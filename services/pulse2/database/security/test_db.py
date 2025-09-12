from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schema import Base, Results, Inventories, Tests
from datetime import datetime

# ⚠️ utilise le driver pymysql
DB_URL = "mysql+pymysql://root:M3dull4+ARE@localhost/security"

# Connexion SQLAlchemy
engine = create_engine(DB_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Crée les tables si elles n’existent pas
Base.metadata.create_all(engine)

# --- Données de test ---
# 1. Inventaire simulé
inv = Inventories(
    machine_id="are-win-1",
    package_name="Adobe Acrobat Reader",
    version="23.008.20470",
    vendor="Adobe",
    collected_at=datetime.now()
)

# 2. Résultats CVE factices
res1 = Results(
    inventory=inv,
    cve_id="CVE-2024-12345",
    severity="HIGH",
    score=8.5,
    description="Overflow in Adobe Acrobat Reader allows RCE.",
    detected_at=datetime.now()
)

res2 = Results(
    inventory=inv,
    cve_id="CVE-2023-6789",
    severity="MEDIUM",
    score=5.4,
    description="Information disclosure via crafted PDF file.",
    detected_at=datetime.now()
)

# Ajout en DB
session.add(inv)
session.add_all([res1, res2])
session.commit()

print("✅ Données de test insérées dans la base `security`.")

session.close()
