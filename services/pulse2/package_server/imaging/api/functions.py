# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Pulse 2 Package Server Imaging API common functions
"""

import logging
import os
import shutil
import re
import subprocess
from time import gmtime
import uuid

from twisted.internet import defer
from twisted.internet.defer import maybeDeferred

from pulse2.package_server.config import P2PServerCP as PackageServerConfig
from pulse2.package_server.imaging.api.client import ImagingXMLRPCClient
from pulse2.package_server.imaging.cache import UUIDCache
from pulse2.package_server.imaging.api.status import Status
from pulse2.package_server.imaging.menu import (
    isMenuStructure,
    ImagingDefaultMenuBuilder,
    ImagingComputerMenuBuilder,
    changeDefaultMenuItem,
    ImagingBootServiceItem,
    ImagingMulticastMenuBuilder,
    CleanMenu,
)
from pulse2.package_server.imaging.computer import ImagingComputerConfiguration
from pulse2.package_server.imaging.iso import ISOImage
from pulse2.package_server.imaging.archiver import Archiver
from pulse2.package_server.imaging.rpcreplay import RPCReplay

from pulse2.utils import (
    isMACAddress,
    splitComputerPath,
    macToNode,
    isUUID,
    rfc3339Time,
    humanReadable,
    SingletonN,
    start_process,
    stop_process,
)
from pulse2.apis import makeURL
from pulse2.imaging.image import Pulse2Image
import json
import configparser


class Imaging(object, metaclass=SingletonN):
    """Common imaging function to perform PXE actions and others"""

    def init1(self, config):
        """
        @param config: Package server config
        @type config: P2PServerCP
        """
        self.logger = logging.getLogger("imaging")
        # Read and check configuration
        self.config = config
        self.myUUIDCache = UUIDCache()
        self.check()
        self._init()

    def check(self):
        """
        Validate imaging configuration.

        @raise ValueError: if the configuration is not right
        """
        basefolder = self.config.imaging_api["base_folder"]
        # Skip bootmenus folder because it is generated dynamically now
        for folder in [
            "base",
            "bootloader",
            "diskless",
            "computers",
            "inventories",
            "masters",
            "postinst",
        ]:
            optname = folder + "_folder"
            dirname = self.config.imaging_api[optname]
            if folder != "base":
                dirname = os.path.join(basefolder, dirname)
            if not os.path.isdir(dirname):
                raise ValueError(
                    "Directory '%s' does not exists. Please check option '%s' in your configuration file."
                    % (dirname, optname)
                )
        for optname in ["diskless_kernel", "diskless_initrd"]:
            fpath = os.path.join(
                basefolder,
                self.config.imaging_api["diskless_folder"],
                self.config.imaging_api[optname],
            )
            if not os.path.isfile(fpath):
                raise ValueError(
                    "File '%s' does not exists. Please check option '%s' in your configuration file."
                    % (fpath, optname)
                )

    def _init(self):
        """
        Perform package server internals initialization, if needed.
        For now, we only set the package server default computer register menu.
        """

        def _cbDefaultMenu(menu):
            self.logger.debug("Default computer boot menu received.")
            if not menu:
                self.logger.info(
                    "Default computer boot menu is empty. Looks like this package server has not been registered."
                )
            else:
                try:
                    imb = ImagingDefaultMenuBuilder(self.config, menu)
                    m = imb.make()
                    m.write()
                    self.logger.info("Default computer boot menu successfully written")
                except Exception as e:
                    self.logger.exception(
                        "Error while setting default computer menu: %s", e
                    )

        def _errDefaultMenu(error):
            self.logger.error(
                "Error while setting default computer boot menu: %s" % error
            )

        self.logger.debug("Starting package server internals initialization")
        RPCReplay().init()
        RPCReplay().firstRun()
        client = self._getXMLRPCClient()
        func = "imaging.getDefaultMenuForRegistering"
        args = (self.config.imaging_api["uuid"],)
        d = client.callRemote(func, *args)
        d.addCallbacks(_cbDefaultMenu, _errDefaultMenu)

    def refreshPXEParams(self, callback=None, *args, **kw):
        def _success(params):
            PackageServerConfig().pxe_login = params["pxe_login"]
            PackageServerConfig().pxe_password = params["pxe_password"]
            PackageServerConfig().pxe_keymap = params["pxe_keymap"]
            if callback:
                callback.__call__(*args, **kw)

        def _error(error):
            self.logger.error("Error while retrieving PXE Params: %s" % error)

        RPCReplay().init()
        RPCReplay().firstRun()
        client = self._getXMLRPCClient()
        func = "imaging.getPXEParams"
        args0 = (self.config.imaging_api["uuid"],)
        d = client.callRemote(func, *args0)
        d.addCallbacks(_success, _error)

    def getBuiltMenu(self, mac):
        global menu_data
        menu_data = None

        def _success(menu):
            global menu_data
            if not isMenuStructure(menu):
                self.logger.error("Invalid menu structure for computer MAC %s" % mac)
                # TODO: generate default menu
                menu_data = ""

            try:
                # self.logger.debug('Setting menu for computer UUID/MAC/hostname %s/%s/%s' % (cuuid, macaddress, hostname))
                imb = ImagingComputerMenuBuilder(self.config, mac, menu)
                imenu = imb.make()
                menu_data = imenu.buildMenu()

            except Exception as e:
                self.logger.exception(
                    "Error while setting new menu of computer uuid/mac %s", str(e)
                )
                # if cant generate specific menu, use default menu
                # or minimal menu genre "Continue usual startup"
                menu_data = ""

        def _error(error):
            global menu_data
            menu_data = ""
            self.logger.error("Error while retrieving PXE Params: %s" % error)

        RPCReplay().init()
        RPCReplay().firstRun()
        client = self._getXMLRPCClient()
        func = "imaging.getGeneratedMenu"
        args0 = (mac,)
        d = client.callRemote(func, *args0)
        d.addCallbacks(_success, _error)
        while menu_data is None:
            pass
        return menu_data

    def getActiveConvergenceForHost(self, uuid):
        RPCReplay().init()
        RPCReplay().firstRun()
        client = self._getXMLRPCClient()
        func = "dyngroup.get_active_convergence_for_host"
        args0 = (uuid,)
        d = client.callRemote(func, *args0)
        return d

    def _getXMLRPCClient(self):
        """
        @return: a XML-RPC client allowing to connect to the agent
        @rtype: ImagingXMLRPCClient
        """
        url, _ = makeURL(PackageServerConfig().mmc_agent)
        return ImagingXMLRPCClient(
            "",
            url,
            PackageServerConfig().mmc_agent["verifypeer"],
            PackageServerConfig().mmc_agent["cacert"],
            PackageServerConfig().mmc_agent["localcert"],
        )

    def getClientShortname(self, mac):
        """
        Querying cache to get client shortname

        @param mac: client's MAC address
        @return: client shortname if exists
        @rtype: str or bool
        """
        res = self.myUUIDCache.getByMac(mac)
        return res and res["shortname"]

    def getClientShortnameByUuid(self, uuid):
        """
        Querying cache to get client shortname

        @param mac: client's MAC address
        @return: client shortname if exists
        @rtype: str or bool
        """
        res = self.myUUIDCache.getByUuid(uuid)
        return res and res["shortname"]

    def getServerDetails(self):
        # FIXME: I don't know if it is needed
        pass

    def logClientAction(self, mac, level, phase, message):
        """
        Remote logging.

        Mainly used to send progress info to our mmc-agent.

        @param mac : The mac address of the client
        @param level : the log level
        @param phase : what the client was doing when the info was logged
        @param message : the log message itself
        @raise TypeError: if MACAddress is malformed
        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def _infoLogs(message):
            """
            Display Some info logs:
                * When a machine is booting
                * When a restoration is done
            """
            shortname = self.getClientShortname(mac)
            if "booted" in message:
                if shortname:
                    self.logger.info(
                        "Imaging: Client %s (%s) has booted" % (shortname, mac)
                    )
                else:
                    self.logger.info("Imaging: Unknown client (%s) has booted" % (mac))
            elif "restoration started" in message:
                # image UUID is in the 36 last characters of message variable
                # message[-37:-1] to get image UUID
                if shortname:
                    self.logger.info(
                        "Imaging: Client %s (%s) is restoring a disk image (%s)"
                        % (shortname, mac, message[-37:-1])
                    )
                else:
                    self.logger.info(
                        "Imaging: Unknown client (%s) is restoring a disk image (%s)"
                        % (mac, message[-37:-1])
                    )
            elif "restoration finished" in message:
                # image UUID is in the 36 last characters of message variable
                # message[-37:-1] to get image UUID
                if shortname:
                    self.logger.info(
                        "Imaging: Disk image (%s) restored successfully to client %s (%s)"
                        % (message[-37:-1], shortname, mac)
                    )
                else:
                    self.logger.info(
                        "Imaging: Disk image (%s) restored successfully to unknown client (%s)"
                        % (message[-37:-1], mac)
                    )

        def _getmacCB(result):
            displayed_statuses = [
                "booted",
                "restoration started",
                "restoration finished",
            ]
            if result and isinstance(result, dict):
                if any(s in message for s in displayed_statuses):
                    _infoLogs(message)  # Display some info logs
                client = self._getXMLRPCClient()
                func = "imaging.logClientAction"
                args = (
                    self.config.imaging_api["uuid"],
                    result["uuid"],
                    level,
                    phase,
                    message,
                )
                d = client.callRemote(func, *args)
                d.addCallbacks(
                    lambda x: True, RPCReplay().onError, errbackArgs=(func, args, 0)
                )
                return d

            if any(s in message for s in displayed_statuses):
                _infoLogs(message)  # Display some info logs
            return False

        if not isMACAddress(mac):
            # TODO: Add better error message.
            raise TypeError

        self.logger.debug(
            "Imaging: Client %s sent a log message while %s (%s) : %s"
            % (mac, phase, level, message)
        )
        d = self.getComputerByMac(mac)
        d.addCallback(_getmacCB)
        return d

    def computerMenuUpdate(self, mac):
        """
        Perform a menu refresh.

        @param mac : The mac address of the client
        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def _getmacCB(result):
            if result and isinstance(result, dict):
                # TODO : call menu refresh here
                return True
            return False

        if not isMACAddress(mac):
            raise TypeError
        self.logger.debug("Imaging: Client %s asked for a menu update" % (mac))
        d = self.getComputerByMac(mac)
        d.addCallback(_getmacCB)
        return d

    def imagingServerStatus(self):
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

    def computersRegister(self, computers):
        """
        Mass method to perform multiple computerRegister.
        Always called by the MMC agent.

        @param computers: list of triplets (hostname,MAC address,imaging data)
        @type computers: list

        @return: the list of UUID that were successfully registered.
        @rtype: list
        """
        ret = []
        for item in computers:
            try:
                computerName, macAddress, imagingData = item
            except (ValueError, TypeError):
                self.logger.error(
                    "Can't register computer, bad input value: %s" % (str(item))
                )
                continue
            if not imagingData:
                self.logger.error(
                    "No imaging data available for %s / %s" % (computerName, macAddress)
                )
                continue
            try:
                if self.computerRegister(computerName, macAddress, imagingData):
                    # Registration succeeded
                    ret.append(imagingData["uuid"])
            except Exception as e:
                self.logger.error(
                    "Can't register computer %s / %s: %s"
                    % (computerName, macAddress, str(e))
                )
        return ret

    def computerRegister(
        self, computerName, macAddress, imagingData=False, waitToBeInventoried=False
    ):
        """
        Method to register a new computer.

        if imagingData is set, we know that the method is called from a MMC
        agent !

        @raise TypeError: if computerName or MACAddress are malformed
        @return: a deferred object resulting to True if registration was
                 successful, else False.
        @rtype: bool
        """

        def onSuccess(result):
            if not isinstance(result, list) and len(result) != 2:
                self.logger.error(
                    "Imaging: Registering client %s (%s) failed: %s"
                    % (computerName, macAddress, str(result))
                )
                ret = False
            elif not result[0]:
                self.logger.error(
                    "Imaging: Registering client %s (%s) failed: %s"
                    % (computerName, macAddress, result[1])
                )
                ret = False
            else:
                uuid = result[1]
                self.logger.info(
                    "Imaging: Client %s (%s) registered as %s"
                    % (computerName, macAddress, uuid)
                )
                self.myUUIDCache.set(uuid, macAddress, hostname, domain, entity)
                ret = self.computerPrepareImagingDirectory(
                    uuid, {"mac": macAddress, "hostname": hostname}
                )
            return ret

        try:
            # check MAC Addr is conform
            if not isMACAddress(macAddress):
                raise TypeError("Malformed MAC address: %s" % macAddress)
            # check computer name is conform
            if not len(computerName):
                raise TypeError("Malformed computer name: %s" % computerName)
            profile, entity_path, hostname, domain = splitComputerPath(computerName)
            entity_path = entity_path.split("/")
            entity = entity_path.pop()
        except TypeError as ex:
            self.logger.error(
                "Imaging: Won't register %s as %s : %s" % (macAddress, computerName, ex)
            )
            return maybeDeferred(lambda x: x, False)

        if not imagingData:
            # Registration is coming from the imaging server
            self.logger.info(
                "Imaging: Registering %s as %s" % (macAddress, computerName)
            )
            client = self._getXMLRPCClient()
            func = "imaging.computerRegister"
            args = (
                self.config.imaging_api["uuid"],
                hostname,
                domain,
                macAddress,
                profile,
                entity,
                waitToBeInventoried,
            )
            d = client.callRemote(func, *args)
            d.addCallbacks(onSuccess, client.onError, errbackArgs=(func, args, False))
            return d
        else:
            # Registration is coming from the MMC agent
            if "uuid" not in imagingData:
                self.logger.error("UUID missing in imaging data")
                return False
            cuuid = imagingData["uuid"]
            self.myUUIDCache.set(cuuid, macAddress, hostname, domain)
            if not self.computerPrepareImagingDirectory(
                cuuid, {"mac": macAddress, "hostname": computerName}
            ):
                return False
            if self.computersMenuSet(imagingData["menu"]) != [cuuid]:
                return False
            return True

    def computerUnregister(self, computerUUID, imageList, archive):
        """
        Unregister a computer from the imaging service:
         - move its boot menu into the archive directory
         - move its home directory into the archive directory
         - move its backup images into the archive directory

        All this move are done in background in another thread, so that it is
        not blocking the whole package server.

        @rtype: bool
        @return: True if the operation succeeded to start
        """
        assert isinstance(imageList, list)
        if not isUUID(computerUUID):
            return False
        macAddress = self.myUUIDCache.getByUUID(computerUUID)
        if not macAddress:
            return False
        else:
            macAddress = macAddress["mac"]
        archiver = Archiver(self.config, archive, computerUUID, macAddress, imageList)
        ret = archiver.check() and archiver.prepare()
        if ret:
            # If all is OK, start archival process in another thread
            archiver.run()
        return ret

    def computerPrepareImagingDirectory(self, uuid, imagingData=False):
        """
        Prepare a full imaging folder for client <uuid>

        if imagingData is False, ask the mmc agent for additional
        parameters (not yet done).

        @param mac : The mac address of the client
        @type menus: MAC Address
        @param imagingData : The data to use for image creation
        @type imagingData: ????
        """
        target_folder = os.path.join(
            PackageServerConfig().imaging_api["base_folder"],
            PackageServerConfig().imaging_api["computers_folder"],
            uuid,
        )
        if os.path.isdir(target_folder):
            self.logger.debug(
                "Imaging: folder %s for client %s : It already exists !"
                % (target_folder, uuid)
            )
            return True
        if os.path.exists(target_folder):
            self.logger.warn(
                "Imaging: folder %s for client %s : It already exists, but is not a folder !"
                % (target_folder, uuid)
            )
            return False
        try:
            os.mkdir(target_folder)
            self.logger.debug(
                "Imaging: folder %s for client %s was created" % (target_folder, uuid)
            )
        except Exception as e:
            self.logger.error(
                "Imaging: I was not able to create folder %s for client %s : %s"
                % (target_folder, uuid, e)
            )
            return False
        return True

    def computerUpdate(self, MACAddress):
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

        self.logger.info("Imaging: Starting menu update for %s" % (MACAddress))
        client = self._getXMLRPCClient()
        func = "imaging.getMenu"
        args = MACAddress
        d = client.callRemote(func, *args)
        d.addCallbacks(onSuccess, client.onError, errbackArgs=(func, args, 0))
        return d

    def injectInventory(self, MACAddress, inventory):
        """
        Method to process the inventory of a computer

        @raise TypeError: if MACAddress is malformed
        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def _onSuccess(result):
            shortname = self.getClientShortname(MACAddress)
            if result and isinstance(result, list) and len(result) == 2:
                if result[0]:
                    if shortname:
                        self.logger.debug(
                            "Imaging: Imaging database disks and partitions information successfully updated for client %s (%s)"
                            % (shortname, MACAddress)
                        )
                    else:
                        self.logger.debug(
                            "Imaging: Imaging database disks and partitions information successfully updated for unknown client (%s)"
                            % (MACAddress)
                        )
                    return True
                else:
                    if shortname:
                        self.logger.error(
                            "Imaging: Failed to update disks and partitions information for client %s (%s): %s"
                            % (shortname, MACAddress, result[1])
                        )
                    else:
                        self.logger.error(
                            "Imaging: Failed to update disks and partitions information for unknown client (%s): %s"
                            % (MACAddress, result[1])
                        )
                    return False
            else:
                if shortname:
                    self.logger.error(
                        "Imaging: Failed to update disks and partitions information for client %s (%s): %s"
                        % (shortname, MACAddress, result)
                    )
                else:
                    self.logger.error(
                        "Imaging: Failed to update disks and partitions information for unknown client (%s): %s"
                        % (MACAddress, result)
                    )
                return False

        def _getmacCB(result):
            if result and isinstance(result, dict):
                if "shortname" in result:
                    inventory["shortname"] = result["shortname"]
                elif "name" in result:
                    inventory["shortname"] = result["name"]

                client = self._getXMLRPCClient()
                func = "imaging.injectInventory"
                args = (self.config.imaging_api["uuid"], result["uuid"], inventory)
                d = client.callRemote(func, *args)
                d.addCallbacks(_onSuccess, client.onError, errbackArgs=(func, args, 0))
                return d
            return False

        if not isMACAddress(MACAddress):
            raise TypeError
        self.logger.debug(
            "Imaging: New PXE inventory received from client %s" % (MACAddress)
        )
        d = self.getComputerByMac(MACAddress)
        d.addCallback(_getmacCB)
        return d

    def injectInventoryUuid(self, uuid, inventory):
        """
        Method to process the inventory of a computer

        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def _onSuccess(result):
            shortname = self.getClientShortnameByUuid(uuid)
            if result and isinstance(result, list) and len(result) == 2:
                if result[0]:
                    if shortname:
                        self.logger.debug(
                            "Imaging: Imaging database disks and partitions information successfully updated for client %s (%s)"
                            % (shortname, uuid)
                        )
                    else:
                        self.logger.debug(
                            "Imaging: Imaging database disks and partitions information successfully updated for unknown client (%s)"
                            % (uuid)
                        )
                    return str(True)
                else:
                    if shortname:
                        self.logger.error(
                            "Imaging: Failed to update disks and partitions information for client %s (%s): %s"
                            % (shortname, uuid, result[1])
                        )
                    else:
                        self.logger.error(
                            "Imaging: Failed to update disks and partitions information for unknown client (%s): %s"
                            % (uuid, result[1])
                        )
                    return str(False)
            else:
                if shortname:
                    self.logger.error(
                        "Imaging: Failed to update disks and partitions information for client %s (%s): %s"
                        % (shortname, uuid, result)
                    )
                else:
                    self.logger.error(
                        "Imaging: Failed to update disks and partitions information for unknown client (%s): %s"
                        % (uuid, result)
                    )
                return str(False)

        def _getuuidCB(result):
            inventory = {}
            if result and isinstance(result, dict):
                if "name" not in result and "shortname" in result:
                    result["name"] = result["shortname"]
                inventory["shortname"] = result["name"]
                _id = result["id"]

                client = self._getXMLRPCClient()
                func = "imaging.injectInventoryUuid"
                args = (self.config.imaging_api["uuid"], _id, inventory)
                d = client.callRemote(func, *args)
                d.addCallbacks(_onSuccess, client.onError, errbackArgs=(func, args, 0))
                return d
            return False

        self.logger.debug("Imaging: New PXE inventory received from client %s" % (uuid))

        d = self.getMachineByUuidSetup(uuid)
        d.addCallback(_getuuidCB)
        return d

    def getMachineByUuidSetup(self, uuid):
        def _onSuccess(result):
            if isinstance(result, dict) and "faultCode" in result:
                self.logger.warning(
                    "Imaging: While processing result for %s %s : %s"
                    % (type(uuid), uuid, result["faultTraceback"])
                )
                return False
            try:
                if result[0]:
                    _id = result[1]["id"]
                    shortname = result[1]["name"]
                    fqdn = ""
                    entity = "UUID%s" % result[1]["entities_id"]

                    self.myUUIDCache.setByUuid(_id, uuid, shortname, fqdn, entity)
                    self.logger.debug("Imaging: Updating cache for %s" % (uuid))
                    return result[1]
                else:
                    self.logger.debug(
                        "Imaging: Unable to resolve %s neither from cache nor from database (unknown computer?)"
                        % (uuid)
                    )
                    return False
            except Exception as e:
                self.logger.error(
                    "Imaging: While processing result %s for %s %s: %s"
                    % (result, type(uuid), uuid, e)
                )

        # try to extract from our cache
        res = self.myUUIDCache.getByUuid(uuid)
        if res:  # fetched from cache
            res["shortname"] = res["shortname"]
            res["fqdn"] = res["fqdn"]
            res["entity"] = res["entity"]
            return maybeDeferred(lambda x: x, res)
        else:  # cache fetching failed, try to obtain the real value
            self.logger.debug(
                "Imaging: Unable to resolve %s from cache, querying database" % (uuid)
            )
            client = self._getXMLRPCClient()
            func = "imaging.getMachineByUuidSetup"
            args = [uuid]
            d = client.callRemote(func, *args)
            d.addCallbacks(_onSuccess, client.onError, errbackArgs=(func, args, 0))
            return d

    def getComputerByMac(self, MACAddress):
        """
        Method to obtain informations about a computer using its MAC address.

        We are using a cache system :
        pulse2.package_server.imaging.cache.UUIDCache()

        @raise TypeError: if MACAddress is malformed
        @return: a deferred object resulting to 1 if processing was
                 successful, else 0.
        @rtype: int
        """

        def _onSuccess(result):
            if isinstance(result, dict) and "faultCode" in result:
                self.logger.warning(
                    "Imaging: While processing result for %s %s : %s"
                    % (type(MACAddress), MACAddress, result["faultTraceback"])
                )
                return False
            try:
                if result[0]:
                    self.myUUIDCache.set(
                        result[1]["uuid"],
                        MACAddress.encode("utf-8"),
                        result[1]["shortname"].encode("utf-8"),
                        result[1]["fqdn"].encode("utf-8"),
                        result[1]["entity"].encode("utf-8"),
                    )
                    self.logger.debug("Imaging: Updating cache for %s" % (MACAddress))
                    return result[1]
                else:
                    self.logger.debug(
                        "Imaging: Unable to resolve %s neither from cache nor from database (unknown computer?)"
                        % (MACAddress)
                    )
                    return False
            except Exception as e:
                self.logger.error(
                    "Imaging: While processing result %s for %s %s: %s"
                    % (result, type(MACAddress), MACAddress, e)
                )

        if not isMACAddress(MACAddress):
            raise TypeError("Bad MAC address: %s" % MACAddress)

        # try to extract from our cache
        res = self.myUUIDCache.getByMac(MACAddress)
        if res:  # fetched from cache
            res["shortname"] = (
                res["shortname"].decode("utf-8")
                if isinstance(res["shortname"], bytes)
                else res["shortname"]
            )
            res["fqdn"] = (
                res["fqdn"].decode("utf-8")
                if isinstance(res["fqdn"], bytes)
                else res["fqdn"]
            )
            res["entity"] = (
                res["entity"].decode("utf-8")
                if isinstance(res["entity"], bytes)
                else res["entity"]
            )
            return maybeDeferred(lambda x: x, res)
        else:  # cache fetching failed, try to obtain the real value
            self.logger.debug(
                "Imaging: Unable to resolve %s from cache, querying database"
                % (MACAddress)
            )
            client = self._getXMLRPCClient()
            func = "imaging.getComputerByMac"
            args = [MACAddress]
            d = client.callRemote(func, *args)
            d.addCallbacks(_onSuccess, client.onError, errbackArgs=(func, args, 0))
            return d

    def computersMenuSet(self, menus):
        """
        Set computers imaging boot menu.

        @param menus: list of (uuid, menu) couples
        @type menus: list

        @ret: list of the computer uuid which menu have been successfully set
        @rtype: list
        """
        ret = []
        for cuuid in menus:
            menu = menus[cuuid]
            if not isUUID(cuuid):
                self.logger.error("Invalid computer UUID %s" % cuuid)
                continue
            if not isMenuStructure(menu):
                self.logger.error("Invalid menu structure for computer UUID %s" % cuuid)
                continue

            res = self.myUUIDCache.getByUUID(cuuid)
            if not res:
                self.logger.warn("Updating MAC address for UUID %s" % cuuid)
                self.myUUIDCache.set(
                    menu["target"]["uuid"],
                    menu["target"]["macaddress"],
                    menu["target"]["name"],
                    "",
                )  # FIXME : domainname '' is probably a wrong idea
                res = self.myUUIDCache.getByUUID(cuuid)
            try:
                macaddress = res["mac"]
                hostname = res["shortname"]
                self.logger.debug(
                    "Setting menu for computer UUID/MAC/hostname %s/%s/%s"
                    % (cuuid, macaddress, hostname)
                )
                imb = ImagingComputerMenuBuilder(self.config, macaddress, menu)
                imenu = imb.make()
                imenu.write()
                ret.append(cuuid)
                imc = ImagingComputerConfiguration(self.config, cuuid, hostname, menu)
                imc.write()
            except Exception as e:
                self.logger.exception(
                    "Error while setting new menu of computer uuid/mac %s: %s"
                    % (cuuid, e)
                )
                # FIXME: Rollback to the previous menu
        return ret

    def imagingServerDefaultMenuSet(self, menu):
        """
        Set the imaging server default boot menu displayed to all un-registered
        computers.

        Called by the MMC agent.

        @param menu: default menu to set
        @type menu: dict

        @return: True if successful
        @rtype: bool
        """
        if not isMenuStructure(menu):
            self.logger.error("Can't set default computer menu: bad menu structure")
            ret = False
        else:
            try:
                self.logger.debug("Setting default boot menu for computers")
                imb = ImagingDefaultMenuBuilder(self.config, menu)
                imenu = imb.make()
                imenu.write()
                ret = True
            except Exception as e:
                self.logger.exception(
                    "Error while setting default boot menu of unregistered computers: %s"
                    % e
                )
                ret = False
        return ret

    # Image management

    def imageGetLogs(self, imageUUID):
        """
        Send the backup logs of an image.
        The content of the log.txt file of the image folder is returned.

        @param imageUUID: image UUID from which logs are wanted
        @type imageUUID: str

        @rtype: list
        @return: list of str with the image logs, or an empty list on error
        """
        ret = []
        if not isUUID(imageUUID):
            if isinstance(imageUUID, bytes):
                imageUUID = imageUUID.decode("utf-8")
            self.logger.error("Bad image UUID %s" % imageUUID)
        else:
            path = os.path.join(
                self.config.imaging_api["base_folder"],
                self.config.imaging_api["masters_folder"],
                imageUUID,
            )
            try:
                image = Pulse2Image(path, False)
                ret = image.logs
            except Exception as e:
                self.logger.error(
                    "Can't get backup logs of image with UUID %s: %s"
                    % (imageUUID, str(e))
                )
        assert isinstance(ret, list)
        return ret

    def computerCreateImageDirectory(self, mac):
        """
        Create an image folder for client <mac>

        This is quiet different as for the LRS, where the UUID was given
        in revosavedir (kernel command line) : folder is now generated
        real-time, if no generation has been done backup is dropped
        client-side

        @param mac : The mac address of the client
        @type mac: MAC Address

        @return: True if the folder
        @rtype: bool
        """

        def _onSuccess(result):
            if not isinstance(result, list) and len(result) != 2:
                self.logger.error(
                    "Imaging: Couldn't register on the MMC agent the image with UUID %s : %s"
                    % (image_uuid, str(result))
                )
                ret = False
            elif not result[0]:
                self.logger.error(
                    "Imaging: Couldn't register on the MMC agent the image with UUID %s : %s"
                    % (image_uuid, result[1])
                )
                ret = False
            else:
                image_path = os.path.join(
                    self.config.imaging_api["base_folder"],
                    self.config.imaging_api["masters_folder"],
                    image_uuid,
                )
                self.logger.debug(
                    "Imaging: Successfully registered disk image to %s" % image_path
                )
                ret = image_uuid
            return ret

        def _gotMAC(result):
            """
            Process result return by getComputerByMac, BTW should be either False or the required info
            """
            if not result:
                self.logger.error("Can't get computer UUID for MAC address %s" % (mac))
                os.rmdir(os.path.join(target_folder, image_uuid))
                return False
            else:  # start gathering details about our image
                c_uuid = result["uuid"]
                isMaster = False  # by default, an image is private
                path = os.path.join(
                    self.config.imaging_api["base_folder"],
                    self.config.imaging_api["masters_folder"],
                    image_uuid,
                )
                size = 0
                creationDate = tuple(gmtime())
                name = "Backup of %s" % result["shortname"]
                desc = "In Progress"
                creator = ""
                state = "EMPTY"  # FIXME : define and use consts

                client = self._getXMLRPCClient()
                func = "imaging.imageRegister"
                args = (
                    self.config.imaging_api["uuid"],
                    c_uuid,
                    image_uuid,
                    isMaster,
                    name,
                    desc,
                    path,
                    size,
                    creationDate,
                    creator,
                    state,
                )
                d = client.callRemote(func, *args)
                d.addCallbacks(
                    _onSuccess, RPCReplay().onError, errbackArgs=(func, args, False)
                )
                return image_uuid

        shortname = self.getClientShortname(mac)
        if shortname:
            self.logger.info(
                "Imaging: Client %s (%s) is creating a disk image" % (shortname, mac)
            )
        else:
            self.logger.info("Imaging: Client %s is creating a disk image" % (mac))

        if not isMACAddress(mac):
            raise TypeError

        target_folder = os.path.join(
            PackageServerConfig().imaging_api["base_folder"],
            PackageServerConfig().imaging_api["masters_folder"],
        )
        # compute our future UUID, using the MAC address as node
        # according the doc, the node is a 48 bits (= 6 bytes) integer
        attempts = 10
        while attempts:
            image_uuid = str(uuid.uuid1(macToNode(mac)))
            if not os.path.exists(os.path.join(target_folder, image_uuid)):
                break
            attempts -= 1
        if not attempts:
            self.logger.warn(
                "Imaging: I was not able to create a folder for client %s" % (mac)
            )
            return maybeDeferred(lambda x: x, False)

        try:
            os.mkdir(os.path.join(target_folder, image_uuid))
        except Exception as e:
            self.logger.warn(
                "Imaging: I was not able to create folder %s for client %s : %s"
                % (os.path.join(target_folder, image_uuid), mac, e)
            )
            return maybeDeferred(lambda x: x, False)

        # now the folder is created (and exists), if can safely be used
        d = self.getComputerByMac(mac)
        d.addCallback(_gotMAC)
        return d

    def getDefaultMenuItem(self, mac):
        """
        Getting of default menu entry from the database.

        @param mac: MAC address of machine
        @type mac: str

        @return: default menu entry
        @rtype: int
        """
        if not isMACAddress(mac):
            self.logger.error("Get default menu item: bad computer MAC %s" % str(mac))
            ret = False
        else:
            computerUUID = self.myUUIDCache.getByMac(mac)
            if not computerUUID:
                self.logger.error("Can't get computer UUID for MAC address %s" % mac)
                ret = False
            else:
                computerUUID = computerUUID["uuid"]
                client = self._getXMLRPCClient()
                func = "imaging.getDefaultMenuItem"
                d = client.callRemote(func, computerUUID)

                @d.addCallback
                def _cb(result):
                    if isinstance(result, list):
                        success, order = result
                        if success:
                            shortname = self.getClientShortname(mac)
                            if shortname:
                                self.logger.debug(
                                    "Client %s (%s) default menu entry is %s"
                                    % (shortname, str(mac), order)
                                )
                            else:
                                self.logger.debug(
                                    "Unknown client %s (%s) default menu entry is %s"
                                    % (shortname, str(mac), order)
                                )
                            return order

                return d
        return ret

    def computerChangeDefaultMenuItem(self, mac, num):
        """
        Called by computer MAC when he want to set its default entry to num

        @param mac : The mac address of the client
        @param num : The menu number
        @type mac: MAC Address
        @type num: int
        """

        def _onSuccess(result):
            if not isinstance(result, list) and len(result) != 2:
                self.logger.error(
                    "Couldn't set default entry on %s for %s : %s"
                    % (num, computerUUID, str(result))
                )
                ret = False
            elif not result[0]:
                self.logger.error(
                    "Couldn't set default entry on %s for %s : %s"
                    % (num, computerUUID, str(result))
                )
                ret = False
            else:
                shortname = self.getClientShortname(mac)
                if shortname:
                    self.logger.info(
                        "Default entry set to %s after disk image creation/restoration for client %s (%s)"
                        % (num, shortname, mac)
                    )
                else:
                    self.logger.info(
                        "Default entry set to %s after disk image creation/restoration for unknown client (%s)"
                        % (num, mac)
                    )
                ret = True
            return ret

        def _onError(error, funcname, args, default_return):
            # Storing RPC so that it can be replayed lated
            RPCReplay().onError(error, funcname, args, default_return)
            # Manually update the computer boot menu
            self.logger.warning(
                'MMC agent can\'t be contacted: updating default menu item to the first "manually"'
            )
            if changeDefaultMenuItem(mac, 0):
                self.logger.warning("Update done")
            else:
                self.logger.error("Update failed")
            return default_return

        if not isMACAddress(mac):
            self.logger.error("Bad computer MAC %s" % str(mac))
            ret = False
        else:
            computerUUID = self.myUUIDCache.getByMac(mac)
            if not computerUUID:
                self.logger.error("Can't get computer UUID for MAC address %s" % mac)
                ret = False
            else:
                computerUUID = computerUUID["uuid"]
                client = self._getXMLRPCClient()
                func = "imaging.computerChangeDefaultMenuItem"
                args = (self.config.imaging_api["uuid"], computerUUID, num)
                d = client.callRemote(func, *args)
                d.addCallbacks(_onSuccess, _onError, errbackArgs=(func, args, True))
                return d
        return ret

    def imageDone(self, computerMACAddress, imageUUID):
        """
        Called by the imaging server to register a new image.

        @return: True if successful
        @rtype: bool
        """

        def _onSuccess(result):
            if not isinstance(result, list) and len(result) != 2:
                self.logger.error(
                    "Imaging: Couldn't update on the MMC agent the image with UUID %s : %s"
                    % (imageUUID, str(result))
                )
                ret = False
            elif not result[0]:
                self.logger.error(
                    "Imaging: Couldn't update on the MMC agent the image with UUID %s : %s"
                    % (imageUUID, result[1])
                )
                ret = False
            else:
                image_path = os.path.join(
                    self.config.imaging_api["base_folder"],
                    self.config.imaging_api["masters_folder"],
                    imageUUID,
                )
                shortname = self.getClientShortname(computerMACAddress)
                if shortname:
                    self.logger.info(
                        "Imaging: Disk image of client %s (%s) created successfully into %s"
                        % (shortname, computerMACAddress, image_path)
                    )
                else:
                    self.logger.info(
                        "Imaging: Disk image of unknown client (%s) created successfully into %s"
                        % (computerMACAddress, image_path)
                    )
                ret = True
            return ret

        def _gotMAC(result):
            """
            Process result return by getComputerByMac, BTW should be either False or the required info
            """
            if not result:
                self.logger.error(
                    "Can't get computer UUID for MAC address %s" % (computerMACAddress)
                )
                return False
            else:
                # start gathering details about our image

                path = os.path.join(
                    self.config.imaging_api["base_folder"],
                    self.config.imaging_api["masters_folder"],
                    imageUUID,
                )
                image = Pulse2Image(path)
                if not image:
                    state = "INVALID"
                    size = 0  # FIXME : use actual size
                    name = "Failed backup of %s" % result["shortname"]
                    desc = "%s, %s" % (rfc3339Time(), humanReadable(size))
                elif image.has_error:
                    state = "FAILED"
                    size = image.size
                    name = "Backup of %s" % result["shortname"]
                    desc = "%s, %s" % (rfc3339Time(), humanReadable(size))
                else:
                    state = "DONE"
                    size = image.size
                    name = "Backup of %s" % result["shortname"]
                    desc = "%s, %s" % (rfc3339Time(), humanReadable(size))

                c_uuid = result["uuid"]
                updateDate = tuple(gmtime())

                client = self._getXMLRPCClient()
                func = "imaging.imageUpdate"
                # size converted to float to bypass xmlrpc limitations
                args = (
                    self.config.imaging_api["uuid"],
                    c_uuid,
                    imageUUID,
                    name,
                    desc,
                    float(size),
                    updateDate,
                    state,
                )
                d = client.callRemote(func, *args)
                d.addCallbacks(
                    _onSuccess, RPCReplay().onError, errbackArgs=(func, args, False)
                )
                return True

        if not isUUID(imageUUID):
            self.logger.error("Bad image UUID %s" % str(imageUUID))
            ret = False
        elif not isMACAddress(computerMACAddress):
            self.logger.error("Bad computer MAC %s" % str(computerMACAddress))
            ret = False
        else:
            d = self.getComputerByMac(computerMACAddress)
            d.addCallback(_gotMAC)
            return d
        return ret

    def imagingServerImageDelete(self, imageUUID):
        """
        Delete an image (backup or master) from the imaging server.
        The corresponding directory is simply removed.

        @param imageUUID: image UUID
        @type: str

        @return: True if it worked, else False
        @rtype: bool
        """
        if not isUUID(imageUUID):
            self.logger.warn("Bad image UUID %s" % str(imageUUID))
            ret = False
        else:
            path = os.path.join(
                self.config.imaging_api["base_folder"],
                self.config.imaging_api["masters_folder"],
                imageUUID,
            )
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    ret = True
                except Exception as e:
                    self.logger.error(
                        "Error while removing image with UUID %s: %s" % (imageUUID, e)
                    )
                    ret = False

            else:
                self.logger.warn(
                    "Can't delete unavailable image with UUID %s" % imageUUID
                )
                ret = False
        return ret

    def imagingServerISOCreate(self, imageUUID, size, title):
        """
        Create an ISO image corresponding to a Pulse 2 image.
        The ISO image is bootable and allows to auto-restore the Pulse 2 image
        to a computer hard disk.
        For now, the creation process is started as a background process.

        @param imageUUID: UUID of the Pulse 2 image to convert to an ISO
        @type imageUUID: str
        @param size: media size, in bytes
        @type size: int
        @param title: title of the image, in UTF-8
        @type title: str
        @return: True if the creation process started
        @rtype: bool
        """
        iso = ISOImage(self.config, imageUUID, size, title)
        ret = True
        try:
            iso.prepare()
            iso.create()
        except Exception as e:
            self.logger.error("Error while creating ISO image: %s" % e)
            ret = False
        return ret

    def imagingClearMenu(self, macadress):
        return CleanMenu(self.config, macadress).clear()

    # Imaging server configuration
    def imagingServermenuMulticast(self, objmenu):
        # create menu multicast
        m = ImagingMulticastMenuBuilder(objmenu)
        ret = m.make()
        return [ret]

    def _checkProcessDrblClonezilla(self):
        s = subprocess.Popen(
            "ps ax | grep drbl-ocs | grep /usr/sbin/drbl-ocs | grep -v grep| grep -v stop",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, err = s.communicate()
        returnprocess = False
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        if re.search("/usr/sbin/drbl-ocs", output):
            returnprocess = True
        s.stdout.close()
        if returnprocess:
            logging.getLogger().debug("drbl-ocs running")
        else:
            logging.getLogger().debug("drbl-ocs stoped")
        return returnprocess

    # Imaging server configuration
    def check_process_multicast(self, objprocess):
        # check execution process multicast
        return self._checkProcessDrblClonezilla()

    def check_process_multicast_finish(self, objprocess):
        # controle process multicast terminat
        if not os.path.exists("/tmp/multicastdescription.txt"):
            self._listPartition(objprocess)
        result = {}
        result["complete"] = False
        pathfile = "/var/lib/pulse2/imaging/masters/%s" % objprocess["uuidmaster"]
        partition = self._listPart(pathfile)
        result["sizeuser"] = {}
        result["partitionlist"] = [x.strip(" \t\n\r") for x in partition[0].split(" ")]
        for x in result["partitionlist"]:
            result["sizeuser"][x] = self._sizeImgDevice(pathfile, x)
        result["indexpartition"] = -1
        result["partionname"] = ""
        result["bytesend"] = int(0)
        if os.path.exists("/tmp/udp-sender.log"):
            r = subprocess.Popen(
                'cat /tmp/udp-sender.log | awk \'BEGIN{ aa=-1;bb =0;a="0"; } /^[0-9]./{ e=a; a= $NF; } /Starting transfer/{aa+=1;} /Transfer complete/{bb+=1;} END{ee=sprintf("%d %s %d",aa,a,bb);print ee;}\'',
                shell=True,
                stdout=subprocess.PIPE,
            )
            line = [x.strip(" \t\n\r") for x in r.stdout]
            r.wait()
            r.stdout.close()
            lineinformation = [
                x.strip(" \t\n\r")
                for x in line[0].split(" ")
                if x.strip(" \t\n\r") != ""
            ]
            if lineinformation[0] != "-1" and len(lineinformation) >= 3:
                result["indexpartition"] = int(lineinformation[0])
                result["bytesend"] = int(lineinformation[1])
                if len(result["partitionlist"]) == int(lineinformation[2]):
                    result["complete"] = True
                if int(result["indexpartition"]) != -1:
                    result["partionname"] = result["partitionlist"][
                        result["indexpartition"]
                    ]
        result["finish"] = (
            os.path.exists("/tmp/processmulticast")
            and not self._checkProcessDrblClonezilla()
        )
        if os.path.exists("/tmp/multicastdescription.txt"):
            f = open("/tmp/multicastdescription.txt", "r")
            lignes = f.readlines()
            f.close()
            result["informations"] = lignes
        if os.path.exists("/tmp/multicast.sh") and result["finish"]:
            os.remove("/tmp/multicast.sh")
            os.remove("/tmp/processmulticast")
        return json.dumps(result)

    def muticast_script_exist(self, objprocess):
        # controle script existance script multicast
        return os.path.exists(objprocess["process"])

    def SetMulticastMultiSessionParameters(self, parameters):
        try:
            Config = configparser.ConfigParser()
            cfgfile = open("/tmp/MultiSessionParameters.ini", "w")
            Config.add_section("sessionparameters")
            Config.set("sessionparameters", "gid", parameters["gid"])
            Config.set("sessionparameters", "from", parameters["from"])
            Config.set("sessionparameters", "is_master", parameters["is_master"])
            Config.set("sessionparameters", "uuidmaster", parameters["uuidmaster"])
            Config.set("sessionparameters", "itemid", parameters["itemid"])
            Config.set("sessionparameters", "itemlabel", parameters["itemlabel"])
            Config.set("sessionparameters", "target_uuid", parameters["target_uuid"])
            Config.set("sessionparameters", "target_name", parameters["target_name"])
            Config.set("sessionparameters", "location", parameters["location"])
            Config.write(cfgfile)
            cfgfile.close()
            return True
        except BaseException:
            return False

    def GetMulticastMultiSessionParameters(self, location):
        parameters = {}
        try:
            Config = configparser.ConfigParser()
            Config.read("/tmp/MultiSessionParameters.ini")
            parameters["gid"] = Config.get("sessionparameters", "gid")
            parameters["from"] = Config.get("sessionparameters", "from")
            parameters["is_master"] = Config.get("sessionparameters", "is_master")
            parameters["uuidmaster"] = Config.get("sessionparameters", "uuidmaster")
            parameters["itemid"] = Config.get("sessionparameters", "itemid")
            parameters["itemlabel"] = Config.get("sessionparameters", "itemlabel")
            parameters["target_uuid"] = Config.get("sessionparameters", "target_uuid")
            parameters["target_name"] = Config.get("sessionparameters", "target_name")
            parameters["location"] = Config.get("sessionparameters", "location")
            return parameters
        except BaseException:
            return parameters

    def ClearMulticastMultiSessionParameters(self, location):
        try:
            if os.path.exists("/tmp/MultiSessionParameters.ini"):
                os.remove("/tmp/MultiSessionParameters.ini")
            if os.path.exists("/tmp/udp-sender.log"):
                os.remove("/tmp/udp-sender.log")
            return True
        except BaseException:
            return False

    def clear_script_multicast(self, objprocess):
        # suppression commande multicast
        # renvoi le groupe a regenerer bootmenu pour unicast
        if os.path.exists("/tmp/processmulticast"):
            os.remove("/tmp/processmulticast")
        if os.path.exists("/tmp/multicast.sh"):
            f = open("/tmp/multicast.sh", "r")
            lignes = f.readlines()
            f.close()
            s = [
                x.split("=")[1].strip(" \t\n\r")
                for x in lignes
                if x.startswith("groupuuid")
            ]
            if len(s) == 0:
                return -1
            os.remove("/tmp/multicast.sh")
            return s[0]
        else:
            return -1

    def _sizeImgDevice(self, pathfiles, device):
        cmd = (
            'ls -al %s/%s* | awk \'BEGIN{ result = 0; } /ptcl-img/{ result = result + $5; } END{ee = sprintf("%%17.0f",result); gsub(/ /,"",ee); print ee}\''
            % (pathfiles, device)
        )
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        line = [x.strip(" \t\n\r".encode("utf-8")) for x in r.stdout]
        r.wait()
        r.stdout.close()
        return line[0].decode("utf-8")

    def start_process_multicast(self, objprocess):
        # start execution process multicast
        # efface file
        if os.path.exists("/tmp/udp-sender.log"):
            os.remove("/tmp/udp-sender.log")
        if os.path.exists("/tmp/multicastdescription.txt"):
            os.remove("/tmp/multicastdescription.txt")
        self._listPartition(objprocess)
        start_process(objprocess["process"])
        return self._checkProcessDrblClonezilla()

    def _listDisk(self, pathfiles):
        if os.path.isfile("%s/disk" % pathfiles):
            f = open("%s/disk" % pathfiles, "r")
            lignes = f.readlines()
            f.close()
            return [x.strip(" \t\n\r") for x in lignes]

    def _sizeTransferReel(self, pathfiles):
        # return Space in use disk
        if os.path.isfile("%s/clonezilla-img" % pathfiles):
            f = open("%s/clonezilla-img" % pathfiles, "r")
            lignes = f.readlines()
            f.close()
            return [x.strip(" \t\n\r") for x in lignes if x.startswith("Space in use:")]

    def _listPart(self, pathfiles):
        if os.path.isfile("%s/parts" % pathfiles):
            f = open("%s/parts" % pathfiles, "r")
            lignes = f.readlines()
            f.close()
            return [x.strip(" \t\n\r") for x in lignes]

    def _listPartition(self, objprocess):
        patitiondisk = []
        # if not os.path.isfile("/tmp/multicastdescription.txt"):
        fe = open("/tmp/multicastdescription.txt", "w")
        # exceptions.KeyError:
        try:
            fe.write("group %s\n" % (str(objprocess["gid"])))
            fe.write("description %s\n" % (objprocess["itemlabel"]))
            objprocess["path"] = "/var/lib/pulse2/imaging/masters/%s" % (
                objprocess["uuidmaster"]
            )
        except KeyError:
            pass
        try:
            fe.write("group %s\n" % (str(objprocess["group"])))
            fe.write("description %s\n" % (objprocess["description"]))
        except KeyError:
            pass
        fe.write("location %s\n" % (objprocess["location"]))
        bootable = "no"
        disk = self._listDisk(objprocess["path"])
        diskorder = " ".join(disk)
        fe.write("diskorder %s\n" % diskorder)
        part = self._listPart(objprocess["path"])
        order = " ".join(part)
        fe.write("partorder %s\n" % order)
        for diskel in disk:
            if os.path.isfile("%s/%s-pt.sf" % (objprocess["path"], diskel)):
                f = open("%s/%s-pt.sf" % (objprocess["path"], diskel), "r")
                lignes = f.readlines()
                f.close()
                for t in lignes:
                    if t.startswith("/dev"):
                        datapart = {}
                        # traitement
                        data = [
                            x.strip("type=, \t\n\r") for x in t.split(" ") if x != ""
                        ]
                        data1 = data[0].split("/")
                        datadesc = {}
                        datadesc["size"] = data[5].strip(", \t\n\r")
                        datadesc["start"] = data[3].strip(", \t\n\r")
                        datadesc["type"] = data[6].strip("type=, \t\n\r")
                        if len(data) >= 8:
                            datadesc["bootable"] = "yes"
                            bootable = "yes"
                        else:
                            datadesc["bootable"] = "no"
                            bootable = "no"
                        datapart[data1[2]] = datadesc
                        patitiondisk.append(datapart)
                        fe.write(
                            "%s %s %s %s\n"
                            % (
                                data1[2],
                                data[5].strip(", \t\n\r"),
                                data[6].strip("type=, \t\n\r"),
                                bootable,
                            )
                        )
        fe.close()
        return patitiondisk

    def checkDeploymentUDPSender(self, objprocess):
        result = {}
        result["data"] = ""
        result["tranfert"] = False
        if os.path.isfile("/tmp/udp-sender.log"):
            s = subprocess.Popen(
                "grep 'Starting transfer'  /tmp/udp-sender.log",
                shell=True,
                stdout=subprocess.PIPE,
            )
            result["tranfert"] = False
            for x in s.stdout:
                result["tranfert"] = True
                break
            s.stdout.close()
            s.wait()
            # if result['tranfert'] == True:
            # self.logger.debug("Starting transfer exist in the file")
            # else:
            # self.logger.debug("Starting transfer no exist in the file")
        return result

    def stop_process_multicast(self, objprocess):
        # stop execution process multicast
        s = subprocess.Popen(
            "/usr/sbin/drbl-ocs -h 127.0.0.1 stop", shell=True, stdout=subprocess.PIPE
        )
        stop_process(objprocess["process"])
        return self._checkProcessDrblClonezilla()

    def imagingServerConfigurationSet(self, conf):
        """
        Set the global imaging server configuration (traffic shaping, etc.)

        @param conf: imaging server configuration to apply
        @type conf: dict
        """
        self.logger.warn("Not yet implemented !")
        return True

    def createBootServiceFromPostInstall(self, script_file):
        ret = True
        try:
            entry = script_file.pop()
            ImagingBootServiceItem(entry).writeShFile(script_file)
        except Exception as e:
            self.logger.error("Error while writing sh file: %s" % e)
            ret = False

        return ret

    def bsUnlinkShFile(self, datas):
        ret = True
        try:
            entry = datas.pop()
            ImagingBootServiceItem(entry).unlinkShFile(datas)
        except Exception as e:
            self.logger.error("Error while deleting sh file: %s" % e)
            ret = False

        return ret

    def getClonezillaParamsForTarget(self, computer_uuid):
        """
        Method to obtain clonezilla parameters for a computer using its UUID.

        @param computer_uuid: The target UUID
        @type computer_uuid: str

        @return: the clonezilla parameters
        @rtype: int
        """
        client = self._getXMLRPCClient()
        func = "imaging.getClonezillaParamsForTarget"
        d = client.callRemote(func, computer_uuid)
        return d
