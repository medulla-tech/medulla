# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Methods for the MMC status page.
"""

from time import time

from mmc.plugins.base.config import BasePluginConfig
from mmc.support.config import PluginConfigFactory
from mmc.support.mmctools import shlaunchDeferred, ProcessScheduler


def getLdapRootDN():
    """
    Returns the LDAP root DN.
    """
    config = PluginConfigFactory.new(BasePluginConfig, "base")
    return {"LDAP root": config.baseDN}


def getDisksInfos():
    """
    Returns a deferred resulting to the output of df -k
    """
    return shlaunchDeferred("df -k")


def getMemoryInfos():
    """
    Returns a deferred resulting to the output of free -m
    """
    return shlaunchDeferred("free -m")


def getUptime():
    """
    Returns the machine uptime
    """
    with open("/proc/uptime") as f:
        data = f.read()
    return data


def listProcess():
    """
    Returns a list of background processes started by the MMC agent
    """
    ret = []
    psdict = ProcessScheduler().listProcess()

    for i in list(psdict.keys()):
        if time() - psdict[i].time > 60:
            # Process do not respond for 60 secondes or exited for 60
            # seconds... remove it
            # FIXME: This should not be done here but in an internal loop of
            # ProcessScheduler()
            del psdict[i]
        else:
            assoc = [psdict[i].desc, psdict[i].progress, psdict[i].status]
            # assoc.append(psdict[i].out)
            ret.append(assoc)

    return ret
