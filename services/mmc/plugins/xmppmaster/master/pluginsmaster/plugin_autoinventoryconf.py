#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2017 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# file pluginsmaster/plugin_autoinventoryconf.py

from mmc.plugins.glpi.database import Glpi
from mmc.plugins.xmppmaster.config import xmppMasterConfig
import hashlib
from pulse2.database.xmppmaster import XmppMasterDatabase
import logging
import traceback
import sys


plugin = {"VERSION": "1.1", "NAME": "autoinventoryconf", "TYPE": "master"}
# Plugin for configuring glpi database for holding the registry keys
# and for configuring the machine agent for inventory


def action(xmppobject):
    logging.getLogger().debug(plugin)
    try:
        # read max_key_index parameter to find out the number of keys
        if hasattr(xmppobject.config, 'max_key_index'):
            logging.getLogger().debug("Loading %s keys" % xmppobject.config.max_key_index)
            nb_iter = int(xmppobject.config.max_key_index) + 1
            for num in range(1, nb_iter):
                registry_key = getattr(xmppobject.config, 'reg_key_' + str(num)).split('|')[0]
                try:
                    registry_key_name = getattr(
                        xmppobject.config, 'reg_key_' + str(num)).split('|')[1]
                except IndexError:
                    registry_key_name = getattr(
                        xmppobject.config, 'reg_key_' + str(num)).split('\\')[-1]
                # Check that the keys are in glpi and insert them if not present
                if not Glpi().getRegistryCollect(registry_key):
                    Glpi().addRegistryCollect(registry_key, registry_key_name)
        pass
    except Exception, e:
        logging.getLogger().error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        pass
