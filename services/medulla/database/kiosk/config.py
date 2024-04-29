# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>uuuuuuu
# SPDX-License-Identifier: GPL-3.0-or-later

# PULSE2
from mmc.database.config import DatabaseConfig


class KioskDatabaseConfig(DatabaseConfig):
    dbname = "kiosk"
    dbsection = "database"
