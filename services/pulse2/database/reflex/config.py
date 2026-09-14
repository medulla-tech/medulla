# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later

from mmc.database.config import DatabaseConfig


class ReflexDatabaseConfig(DatabaseConfig):
    dbname = "reflex"
    dbsection = "database"
