# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2020-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-2.0-or-later

# PULSE2
from mmc.database.config import DatabaseConfig

class UpdatesDatabaseConfig(DatabaseConfig):
    dbname = "updates"
    dbsection = "database"

