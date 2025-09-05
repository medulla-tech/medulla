# create_tables.py

from pulse2.database.mobile import MobileDatabase
from pulse2.database.mobile.config import MobileDatabaseConfig

def main():
    config = MobileDatabaseConfig()
    mobile_db = MobileDatabase()
    
    success = mobile_db.activate(config)

    if success:
        print("Tables créées ou déjà existantes.")
    else:
        print("Échec de la création des tables.")

if __name__ == "__main__":
    main()