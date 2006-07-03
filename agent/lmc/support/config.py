#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of LMC.
#
# LMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# LMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import lmctools
from ConfigParser import *

class ConfigException(Exception):
    pass

class PluginConfig(ConfigParser):

    def __init__(self, name, conffile = None):
        ConfigParser.__init__(self)
        if not conffile: self.conffile = lmctools.getConfigFile(name)
        else: self.conffile = conffile
        self.setDefault()
        self.read(self.conffile)
        self.readConf()

    def readConf(self):
        """Read the configuration file"""
        try: self.disabled = self.getboolean("main", "disable")
        except NoSectionError, NoOptionError: pass

    def setDefault(self):
        """Set reasonable default"""
        self.disabled = True

    def check(self):
        """
        Check the values set in the configuration file.

        Must be implemented by the subclass.
        ConfigException is raised with a corresponding error string if a check
        fails.
        """
        pass
