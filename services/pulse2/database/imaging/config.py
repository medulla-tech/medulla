# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

# MMC
from mmc.database.config import DatabaseConfig

class ImagingDatabaseConfig(DatabaseConfig):
    dbname = "imaging"

#    def setup(self, config_file):
#        # read the database configuration
#        DatabaseConfig.setup(self, config_file)
#        # add the rest of the config retrieving if needed
