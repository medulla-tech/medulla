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
    config = PluginConfigFactory.new(BasePluginConfig, 'base')
    return {'LDAP root': config.baseDN}

def getDisksInfos():
    """
    Returns a deferred resulting to the output of df -k
    """
    return shlaunchDeferred('df -k')

def getMemoryInfos():
    """
    Returns a deferred resulting to the output of free -m
    """
    return shlaunchDeferred('free -m')

def getUptime():
    """
    Returns the machine uptime
    """
    f = file('/proc/uptime')
    data = f.read()
    f.close()
    return data

def listProcess():
    """
    Returns a list of background processes started by the MMC agent
    """
    ret = []
    psdict = ProcessScheduler().listProcess()

    for i in psdict.keys():
        assoc = []
        if time() - psdict[i].time > 60:
            # Process do not respond for 60 secondes or exited for 60
            # seconds... remove it
            # FIXME: This should not be done here but in an internal loop of
            # ProcessScheduler()
            del psdict[i]
        else:
            assoc.append(psdict[i].desc)
            assoc.append(psdict[i].progress)
            assoc.append(psdict[i].status)
            #assoc.append(psdict[i].out)
            ret.append(assoc)

    return ret
