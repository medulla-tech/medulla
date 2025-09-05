from pulse2.database.mobile.schema import Devices
from pulse2.database.mobile import MobileDatabase
from pulse2.database.mobile.config import MobileDatabaseConfig 
from sqlalchemy.orm import sessionmaker
import datetime

mobile_db = MobileDatabase()
config = MobileDatabaseConfig()
success = mobile_db.activate(config)

Session = sessionmaker(bind=mobile_db.db)
session = Session()

def insertData():
   
    if session.query(Devices).count() == 0:
        test_device = Devices(
            number="0102030405",
            description="Test device",
            lastupdate=datetime.datetime.utcnow(),
            configurationid=100,
            oldconfigurationid=50,
            info="Un appareil fictif pour test",
            imei="999999999999999",
            phone="0601020304",
            customerid=1,
            imeiupdatets=datetime.datetime.utcnow(),
            custom1="Alpha",
            custom2="Beta",
            custom3="Gamma",
            oldnumber="0504030201",
            fastsearch="test1",
            enrolltime=datetime.datetime.utcnow(),
            infojson="{}",
            publicip="10.0.0.1"
        )
        session.add(test_device)
        session.commit()
        print("Appareil de test inséré dans la table 'devices'")
    else:
        print("La table 'devices' contient déjà des données.")

if __name__ == "__main__":
    insertData()
