import logging
from mmc.database_helper import db_session
from .schema import Inventories, Results

def init_db():
    try:
        logging.info("[Security] Vérification des tables...")
        Inventories.__table__.create(bind=db_session.bind, checkfirst=True)
        Results.__table__.create(bind=db_session.bind, checkfirst=True)
        logging.info("[Security] Tables prêtes.")
    except Exception as e:
        logging.error("Erreur initialisation DB: %s", e)
