# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# MMC
from mmc.database.config import DatabaseConfig


class MscDatabaseConfig(DatabaseConfig):
    dbname = "msc"
    dbsection = "msc"

    def setup(self, config_file):
        # read the database configuration
        DatabaseConfig.setup(self, config_file)

        # read the other inventory default parameters
