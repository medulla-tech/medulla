# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Plugin to manage the interface with xmppmaster
"""
import logging
from mmc.plugins.guacamole.config import guacamoleConfig

from pulse2.version import getVersion, getRevision  # pyflakes.ignore

VERSION = "1.0.0"
APIVERSION = "4:1:3"


logger = logging.getLogger()


# #############################################################
# PLUGIN GENERAL FUNCTIONS
# #############################################################


def getApiVersion():
    return APIVERSION


def activate():
    """
    Read the plugin configuration, initialize it, and run some tests to ensure
    it is ready to operate.
    """
    logger = logging.getLogger()
    config = guacamoleConfig("guacamole")
    if config.disable:
        logger.warning("Plugin guacamole: disabled by configuration.")
        return False
    return True
