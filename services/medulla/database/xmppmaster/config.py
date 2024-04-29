# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# PULSE2
from mmc.database.config import DatabaseConfig


class XmppMasterDatabaseConfig(DatabaseConfig):
    dbname = "xmppmaster"
    dbsection = "database"

    # def setup(self, config_file):
    # read the database configuration
    # DatabaseConfig.setup(self, config_file)
