# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides the methods to access the database, it's a wrapper to call the good backend
depending on the version of the database.
"""

# TODO rename location into entity (and locations in location)
from mmc.plugins.glpi.config import GlpiConfig
from mmc.plugins.glpi.database_084 import  Glpi084
from mmc.plugins.glpi.database_92 import Glpi92
from mmc.plugins.glpi.database_94 import Glpi94
from mmc.plugins.glpi.database_95 import Glpi95
from mmc.plugins.glpi.database_100 import Glpi100

from pulse2.database.dyngroup.dyngroup_database_helper import DyngroupDatabaseHelper

import logging

class Glpi(DyngroupDatabaseHelper):
    """
    Singleton Class to query the glpi database.

    """
    is_activated = False

    def db_check(self):
        return self.database.db_check()

    def activate(self, conffile = None):
        self.logger = logging.getLogger()

        if self.is_activated:
            self.logger.info("Glpi don't need activation")
            return None

        self.config = GlpiConfig("glpi", conffile)

        # we choose the good backend for the database
        if Glpi084().try_activation(self.config):
            self.database = Glpi084()
        elif Glpi92().try_activation(self.config):
            self.database = Glpi92()
        elif Glpi94().try_activation(self.config):
            self.database = Glpi94()
        elif Glpi95().try_activation(self.config):
            self.database = Glpi95()
        elif Glpi100().try_activation(self.config):
            self.database = Glpi100()
        else:
            self.logger.warn("Can't load the right database backend for your version of GLPI")
            return False

        # activate the backend
        ret = self.database.activate(self.config)
        self.is_activated = self.database.is_activated
        # Register the panel to the DashboardManager
        try:
            logging.getLogger().debug('Try to load glpi panels')
            from mmc.plugins.dashboard.manager import DashboardManager
            from mmc.plugins.dashboard.panel import Panel
            DM = DashboardManager()
            DM.register_panel(Panel("inventory"))
            if self.database.fusionantivirus is not None:
                DM.register_panel(Panel("antivirus"))
            # Registring OS Repartition panel
            DM.register_panel(Panel("os_repartition"))
        except ImportError:
            logging.getLogger().debug('Failed to load glpi panels')

        return ret

    def __getattr__(self, attr_name):
            return getattr(self.database, attr_name)
