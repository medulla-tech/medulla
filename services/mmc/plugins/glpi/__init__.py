#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of MMC.
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

"""
MMC GLPI Backend plugin
It provide an API to access informations in the GLPI database.
"""

from mmc.support.mmctools import xmlrpcCleanup, RpcProxyI, ContextMakerI, SecurityContext
from mmc.plugins.base.computers import ComputerManager
from mmc.plugins.base.provisioning import ProvisioningManager
from mmc.plugins.glpi.config import GlpiConfig
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.glpi.computers import GlpiComputers
from mmc.plugins.glpi.provisioning import GlpiProvisioner
from pulse2.managers.location import ComputerLocationManager
from mmc.plugins.glpi.location import GlpiLocation

from pulse2.version import getVersion, getRevision # pyflakes.ignore

# health check
from mmc.plugins.glpi.health import scheduleCheckStatus

import logging

APIVERSION = "0:0:0"

NOAUTHNEEDED = [
    'getMachineUUIDByMacAddress',
    'hasKnownOS',
]


def getApiVersion():
    return APIVERSION


def activate():
    config = GlpiConfig("glpi")
    logger = logging.getLogger()
    if config.disable:
        logger.warning("Plugin glpi: disabled by configuration.")
        return False

    if not GlpiLocation().init(config):  # does Glpi().activate()
        return False
    if not Glpi().db_check():
        return False

    ComputerManager().register("glpi", GlpiComputers)
    ProvisioningManager().register("glpi", GlpiProvisioner)
    if config.displayLocalisationBar:
        ComputerLocationManager().register("glpi", GlpiLocation)

    if config.check_db_enable:
        scheduleCheckStatus(config.check_db_interval)

    return True


class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s


class RpcProxy(RpcProxyI):
    def getMachineNumberByState(self):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineNumberByState(ctx))

    def getMachineListByState(self, groupName):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineListByState(ctx, groupName))

    def getAntivirusStatus(self):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getAntivirusStatus(ctx))

    def getRestrictedComputersListLen(self):
        ctx = self.currentContext
        return Glpi().getRestrictedComputersListLen(ctx, {})

    def getMachineByOsLike(self, osname, count):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineByOsLike(ctx, osname, count))

    def getMachineListByAntivirusState(self, groupName):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineListByAntivirusState(ctx,
                                                                   groupName))

    def getMachineByHostnameAndMacs(self, hostname, macs):
        ctx = self.currentContext
        return xmlrpcCleanup(Glpi().getMachineByHostnameAndMacs(ctx,
                                                                hostname,
                                                                macs))


def getLicensesCount(vendor, software, version):
    ctx = SecurityContext()
    ctx.userid = "root"

    def replace_splat(param):
        if '*' in param:
            return param.replace('*', '%')
        return param

    def check_param(param):
        if param == '' or param == '*' or param == '%':
            return None
        return replace_splat(param)

    software = check_param(software)
    vendor = check_param(vendor)
    version = check_param(version)
    if software is None:
        software = '%'
    return xmlrpcCleanup(Glpi().getAllSoftwaresImproved(ctx,
                                                     software,
                                                     vendor=vendor,
                                                     version=version,
                                                     count=1))


def getLastMachineInventoryFull(uuid):
    return xmlrpcCleanup(Glpi().getLastMachineInventoryFull(uuid))


def inventoryExists(uuid):
    return xmlrpcCleanup(Glpi().inventoryExists(uuid))


def getLastMachineInventoryPart(uuid,
                                part,
                                minbound=0,
                                maxbound=-1,
                                filt=None,
                                options={}):
    return xmlrpcCleanup(Glpi().getLastMachineInventoryPart(uuid,
                                                            part,
                                                            minbound,
                                                            maxbound,
                                                            filt,
                                                            options))


def countLastMachineInventoryPart(uuid, part, filt=None, options={}):
    return xmlrpcCleanup(Glpi().countLastMachineInventoryPart(uuid,
                                                              part,
                                                              filt,
                                                              options))


def getMachineMac(uuid):
    return xmlrpcCleanup(Glpi().getMachineMac(uuid))


def getMachineIp(uuid):
    return xmlrpcCleanup(Glpi().getMachineIp(uuid))


def setGlpiEditableValue(uuid, name, value):
    return xmlrpcCleanup(Glpi().setGlpiEditableValue(uuid, name, value))


# TODO
def getInventoryEM(part):
    return []


def getGlpiMachineUri():
    return Glpi().config.glpi_computer_uri


def getMachineUUIDByMacAddress(mac):
    return xmlrpcCleanup(Glpi().getMachineUUIDByMacAddress(mac))


def getMachinesLocations(uuids):
    return xmlrpcCleanup(Glpi().getMachinesLocations(uuids))


def hasKnownOS(uuid):
    return xmlrpcCleanup(Glpi().hasKnownOS(uuid))
