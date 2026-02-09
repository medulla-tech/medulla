# -*- coding: utf-8; -*-
from mmc.database.config import DatabaseConfig

class MobileDatabaseConfig(DatabaseConfig):
    dbname = "mobile"
    dbsection = "database"

    def setup(self, config_file):
        # read the database configuration
        DatabaseConfig.setup(self, config_file)
        
        # hmdm api config
        if self.cp.has_section("hmdm"):
            if self.cp.has_option("hmdm", "url"):
                self.hmdm_url = self.cp.get("hmdm", "url")
            
            if self.cp.has_option("hmdm", "login"):
                self.hmdm_login = self.cp.get("hmdm", "login")
            
            if self.cp.has_option("hmdm", "password"):
                self.hmdm_password = self.cp.get("hmdm", "password")
