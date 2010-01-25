# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os

from mmc.support import mmctools
from mmc.support.config import PluginConfig
from pulse2.database.imaging.config import ImagingDatabaseConfig
from ConfigParser import NoOptionError

class ImagingConfig(ImagingDatabaseConfig):
    disable = True

    def init(self, name = 'imaging', conffile = None):
        self.dbsection = "database"
        self.name = name
        if not conffile: self.conffile = mmctools.getConfigFile(name)
        else: self.conffile = conffile

        ImagingDatabaseConfig.setup(self, self.conffile)
        self.setup(self.conffile)

    def setup(self, conf_file):
        """
        Read the module configuration
        
        Currently used params:
        - section "imaging":
          + revopath
          + publicdir
        """
        self.disable = self.cp.getboolean("main", "disable")
        self.revopath = self.cp.get("imaging", "revopath")
        self.publicdir = self.cp.get("imaging", "publicdir")
        self.isodir = self.cp.get("imaging", "isodir")
        self.tmpdir = self.cp.get("imaging", "tmpdir")
        self.bindir = self.cp.get("imaging", "bindir")
        self.publicpath = os.path.join(self.revopath, self.publicdir)
        self.isopath = os.path.join(self.revopath, self.isodir)
        self.tmppath = os.path.join(self.revopath, self.tmpdir)
        self.binpath = os.path.join(self.revopath, self.bindir)

    def setDefault(self):
        """
        Set default values
        """
        PluginConfig.setDefault(self)

