# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
from mmc.database.config import DatabaseConfig

class StoreDatabaseConfig(DatabaseConfig):
    dbname = "store"
    dbsection = "database"
