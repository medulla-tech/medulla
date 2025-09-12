# -*- coding: utf-8 -*-
import logging
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.security.schema import Tests, Results

print("[Security] __init__.py chargé par mmc-agent")

VERSION = "1.0.0"
APIVERSION = "1:0:0"

class SecurityDatabase(DatabaseHelper):
    def db_check(self):
        self.my_name = "security"
        self.configfile = "security.ini"
        return DatabaseHelper.db_check(self)

    @DatabaseHelper._sessionm
    def tests(self, session):
        logger = logging.getLogger()
        logger.info("[Security] Appel tests()")
        return [{
            "cve_id": "CVE-2025-1234",
            "severity": "HIGH",
            "score": 9.8,
            "machine_id": "demo-machine",
            "package_name": "openssl",
            "description": "Faille simulée pour test UI"
        }]

    @DatabaseHelper._sessionm
    def results(self, session):
        logger = logging.getLogger()
        logger.info("[Security] Appel results()")
        return [{"msg": "Hello depuis results()"}]


def getVersion():
    return VERSION

def getApiVersion():
    return APIVERSION
