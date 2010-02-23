# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Pulse 2 Package Server Imaging API
"""

import logging

from twisted.internet import defer
from twisted.internet.defer import maybeDeferred

from pulse2.package_server.config import P2PServerCP as PackageServerConfig
from pulse2.package_server.xmlrpc import MyXmlrpc
from pulse2.package_server.imaging.api.client import ImagingXMLRPCClient
from pulse2.package_server.imaging.cache import UUIDCache
from pulse2.package_server.imaging.api.status import Status

from pulse2.utils import isMACAddress, splitComputerPath
from pulse2.apis import makeURL

class ImagingApi(MyXmlrpc):

    myType = 'Imaging'

    def __init__(self, name, config):
        """
        @param config: Package server config
        @type config: P2PServerCP
        """
        MyXmlrpc.__init__(self)
        self.name = name
        self.logger = logging.getLogger()
        self.logger.info("Initializing %s" % self.myType)
        # Read and check configuration
        self.config = PackageServerConfig()

    def xmlrpc_getServerDetails(self):
        pass

    def xmlrpc_logClientAction(self):
        pass

    def xmlrpc_imagingServerStatus(self):
        """
        Returns the percentage of remaining size from the part where the images
        are stored.

        @return: a percentage, or -1 if it fails
        @rtype: int
        """
        status = Status(self.config)
        status.deferred = defer.Deferred()
        status.get()
        return status.deferred

    def xmlrpc_computerRegister(self, computerName, MACAddress):
        """
        Method to register a new computer.

        @raise TypeError: if computerName or MACAddress are malformed
        @return: a deferred object resulting to 1 if registration was
                 successful, else 0.
        @rtype: int
        """

        def onSuccess(result):
            self.logger.info('Imaging: New client registration succeeded for: %s %s (%s)' % (computerName, MACAddress, str(result)))
            return 1

        if not isMACAddress(MACAddress):
            raise TypeError
        if not len(computerName):
            raise TypeError
        profile, entities, hostname, domain = splitComputerPath(computerName)

        url, credentials = makeURL(PackageServerConfig().mmc_agent)

        self.logger.info('Imaging: Starting registration for %s as %s' % (MACAddress, computerName))
        # Call the MMC agent
        client = ImagingXMLRPCClient(
            '',
            url,
            PackageServerConfig().mmc_agent['verifypeer'],
            PackageServerConfig().mmc_agent['cacert'],
            PackageServerConfig().mmc_agent['localcert']
        )
        func = 'imaging.computerRegister'
        args = (hostname, domain, MACAddress, profile, entities)
        d = client.callRemote(func, *args)
        d.addCallbacks(onSuccess, client.onError, errbackArgs = (func, args, 0))
        return d

    def xmlrpc_computerUpdate(self, MACAddress):
        """
        Method to update the menu a computer.

        @raise TypeError: if MACAddress is malformed
        @return: a deferred object resulting to 1 if update was
                 successful, else 0.
        @rtype: int
        """

        def onSuccess(result):
            # TODO : add menu re-generation here
            return 1

        if not isMACAddress(MACAddress):
            raise TypeError

        url, credentials = makeURL(PackageServerConfig().mmc_agent)

        self.logger.info('Imaging: Starting menu update for %s' % (MACAddress))
        # Call the MMC agent
        client = ImagingXMLRPCClient(
            '',
            url,
            PackageServerConfig().mmc_agent['verifypeer'],
            PackageServerConfig().mmc_agent['cacert'],
            PackageServerConfig().mmc_agent['localcert']
        )
        func = 'imaging.getMenu'
        args = (MACAddress)
        d = client.callRemote(func, *args)
        d.addCallbacks(onSuccess, client.onError, errbackArgs = (func, args, 0))
        return d

    def xmlrpc_injectInventory(self, MACAddress, Inventory):
        """
        Method to process the inventory of a computer

        @raise TypeError: if MACAddress is malformed
        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def onSuccess(result):
            # TODO : add menu re-generation here
            return 1

        if not isMACAddress(MACAddress):
            raise TypeError

        url, credentials = makeURL(PackageServerConfig().mmc_agent)

        self.logger.info('Imaging: Starting inventory processing for %s' % (MACAddress))
        # Call the MMC agent
        client = ImagingXMLRPCClient(
            '',
            url,
            PackageServerConfig().mmc_agent['verifypeer'],
            PackageServerConfig().mmc_agent['cacert'],
            PackageServerConfig().mmc_agent['localcert']
        )
        func = 'imaging.injectInventory'
        args = (MACAddress, Inventory)
        d = client.callRemote(func, *args)
        d.addCallbacks(onSuccess, client.onError, errbackArgs = (func, args, 0))
        return d


    def xmlrpc_getComputerUUID(self, MACAddress):
        """
        Method to obtain the UUID of a computer.

        We are using a cache system :
        pulse2.package_server.imaging.cache.UUIDCache()

        @raise TypeError: if MACAddress is malformed
        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def onSuccess(result):
            try:
                if result[0]:
                    UUIDCache().set(result[1], MACAddress, '', '')
                return result
            except Exception, e:
                self.logger.info('Imaging: While processing result %s for %s : %s' % (MACAddress, result, e))

        if not isMACAddress(MACAddress):
            raise TypeError

        # try to extract from our cache
        res = UUIDCache().getByMac(MACAddress)
        if res: # fetched from cache
            return maybeDeferred(lambda x: x['uuid'], res)
        else : # cache fetching failed, try to obtain the real value
            url, credentials = makeURL(PackageServerConfig().mmc_agent)
            self.logger.info('Imaging: Getting computer UUID for %s' % (MACAddress))
            # Call the MMC agent
            client = ImagingXMLRPCClient(
                '',
                url,
                PackageServerConfig().mmc_agent['verifypeer'],
                PackageServerConfig().mmc_agent['cacert'],
                PackageServerConfig().mmc_agent['localcert']
            )
            d = client.callRemote('imaging.getComputerUUID', MACAddress)
            d.addCallbacks(onSuccess, client.onError, errbackArgs = ('imaging.getComputerUUID', MACAddress, 0))
            return d

    def xmlrpc_computersMenuSet(menus):
        """
        Set computers imaging boot menu.

        @param menus: list of (uuid, menu) couples
        @type menus: list

        @ret:
        """
        for uuid, menu in menus:
            pass
        return 1
