# -*- coding: utf-8 -*-
import logging
from pulse2.database.security import SecurityDatabase as BaseSecurityDatabase
from pulse2.database.security import getVersion as db_getVersion, getApiVersion as db_getApiVersion

logger = logging.getLogger()

class SecurityDatabase(BaseSecurityDatabase):
    def activate(self, *args, **kwargs):
            logger.info("[Security] activate() appelé")
            try:
                # Il suffit d’appeler db_check() : DatabaseHelper va initialiser self.db lui-même
                super().db_check()
                logger.info("[Security] Base security initialisée avec succès")
            except Exception as e:
                logger.error(f"[Security] Erreur init DB : {e}")
            return True
# Instance globale unique
methods = SecurityDatabase()

# Fonctions attendues par MMC
def getVersion():
    return db_getVersion()

def getApiVersion():
    return db_getApiVersion()

def activate():
    return methods.activate()

def tests():
    logger.info("[Security] Appel tests()")
    return methods.tests()

def results():
    logger.info("[Security] Appel results()")
    return methods.results()
