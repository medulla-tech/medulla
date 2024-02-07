# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

# file : pulse2/database/greenit/config.py


# PULSE2
from mmc.database.config import DatabaseConfig


class GreenitDatabaseConfig(DatabaseConfig):
    dbname = "greenit"
    dbsection = "database"
